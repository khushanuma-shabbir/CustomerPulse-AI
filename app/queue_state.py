"""
Queue State Management Module
Tracks solved tickets, queue history, and starvation metrics
"""
from datetime import datetime
from typing import Dict, List, Optional, Set
import json
import os


class QueueState:
    """
    Manages queue state across sessions
    
    Responsibilities:
    - Track solved tickets
    - Track queue position history for starvation detection
    - Track times each ticket was bypassed
    - Persist state (optional, in-memory for now)
    """
    
    def __init__(self, session_id: str = None):
        """
        Initialize queue state
        
        Args:
            session_id: Unique session identifier (optional)
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Solved tickets: {ticket_id: solve_info}
        self.solved_tickets: Dict[str, Dict] = {}
        
        # Queue history: {ticket_id: {times_bypassed, last_position, history}}
        self.queue_history: Dict[str, Dict] = {}
        
        # Active tickets (not solved)
        self.active_tickets: Set[str] = set()
        
        # Queue snapshots over time
        self.queue_snapshots: List[Dict] = []
    
    def add_active_tickets(self, ticket_ids: List[str]):
        """
        Register tickets as active in the queue
        
        Args:
            ticket_ids: List of ticket IDs to mark as active
        """
        for ticket_id in ticket_ids:
            if ticket_id not in self.solved_tickets:
                self.active_tickets.add(ticket_id)
                
                # Initialize history if not exists
                if ticket_id not in self.queue_history:
                    self.queue_history[ticket_id] = {
                        'times_bypassed': 0,
                        'last_position': None,
                        'position_history': [],
                        'first_seen': datetime.now().isoformat()
                    }
    
    def update_queue_positions(self, ranked_tickets: List[Dict]):
        """
        Update queue position history and calculate bypass counts
        
        Args:
            ranked_tickets: List of tickets with queue_position
        """
        # Store snapshot
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'positions': {t['ticket_id']: t['queue_position'] for t in ranked_tickets}
        }
        self.queue_snapshots.append(snapshot)
        
        # Update individual ticket histories
        for ticket in ranked_tickets:
            ticket_id = ticket['ticket_id']
            new_position = ticket['queue_position']
            
            if ticket_id in self.queue_history:
                history = self.queue_history[ticket_id]
                last_position = history['last_position']
                
                # Track position changes
                history['position_history'].append({
                    'position': new_position,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Calculate if bypassed
                # If position stayed same or got worse while others got solved,
                # it means newer/higher priority tickets were selected
                if last_position is not None and new_position > last_position:
                    # Position got worse (moved down in queue)
                    history['times_bypassed'] += 1
                
                # Update last position
                history['last_position'] = new_position
    
    def solve_ticket(self, ticket_id: str, solved_by: str = "System", 
                    queue_position: int = None) -> Dict:
        """
        Mark a ticket as solved
        
        Args:
            ticket_id: ID of ticket to solve
            solved_by: Who solved the ticket
            queue_position: Position in queue when solved
            
        Returns:
            Solve info dictionary
        """
        # Get times_bypassed defensively
        ticket_history = self.queue_history.get(ticket_id, {})
        if isinstance(ticket_history, dict):
            times_bypassed = ticket_history.get('times_bypassed', 0)
        elif isinstance(ticket_history, int):
            times_bypassed = ticket_history
        else:
            times_bypassed = 0
        
        solve_info = {
            'ticket_id': ticket_id,
            'solved_at': datetime.now().isoformat(),
            'solved_by': solved_by,
            'queue_position_when_solved': queue_position,
            'times_bypassed': times_bypassed
        }
        
        # Mark as solved
        self.solved_tickets[ticket_id] = solve_info
        
        # Remove from active
        self.active_tickets.discard(ticket_id)
        
        return solve_info
    
    def unsolve_ticket(self, ticket_id: str) -> bool:
        """
        Undo solve action (move ticket back to active queue)
        
        Args:
            ticket_id: ID of ticket to unsolve
            
        Returns:
            True if successful, False if ticket wasn't solved
        """
        if ticket_id in self.solved_tickets:
            del self.solved_tickets[ticket_id]
            self.active_tickets.add(ticket_id)
            return True
        return False
    
    def is_solved(self, ticket_id: str) -> bool:
        """Check if ticket is solved"""
        return ticket_id in self.solved_tickets
    
    def get_active_ticket_ids(self) -> List[str]:
        """Get list of active (not solved) ticket IDs"""
        return list(self.active_tickets)
    
    def get_solved_ticket_ids(self) -> List[str]:
        """Get list of solved ticket IDs"""
        return list(self.solved_tickets.keys())
    
    def get_queue_history_for_ticket(self, ticket_id: str) -> Dict:
        """Get queue history for a specific ticket"""
        return self.queue_history.get(ticket_id, {
            'times_bypassed': 0,
            'last_position': None,
            'position_history': []
        })
    
    def get_starvation_data(self) -> Dict[str, Dict]:
        """
        Get starvation data for all tickets (for queue engine)
        
        Returns:
            Dictionary mapping ticket_id to history dict with times_bypassed
        """
        result = {}
        for ticket_id, history in self.queue_history.items():
            # Ensure history is a dictionary
            if isinstance(history, dict):
                result[ticket_id] = history
            elif isinstance(history, int):
                # Convert old integer format to dict
                result[ticket_id] = {
                    'times_bypassed': history,
                    'last_position': None,
                    'last_considered_at': None
                }
                # Update the stored value
                self.queue_history[ticket_id] = result[ticket_id]
            else:
                # Default for unknown types
                result[ticket_id] = {
                    'times_bypassed': 0,
                    'last_position': None,
                    'last_considered_at': None
                }
                self.queue_history[ticket_id] = result[ticket_id]
        
        return result
    
    def get_statistics(self) -> Dict:
        """Get queue statistics"""
        return {
            'total_active': len(self.active_tickets),
            'total_solved': len(self.solved_tickets),
            'total_tickets': len(self.active_tickets) + len(self.solved_tickets),
            'queue_snapshots': len(self.queue_snapshots),
            'session_id': self.session_id
        }
    
    def export_state(self) -> Dict:
        """Export complete state as dictionary"""
        return {
            'session_id': self.session_id,
            'solved_tickets': self.solved_tickets,
            'queue_history': self.queue_history,
            'active_tickets': list(self.active_tickets),
            'queue_snapshots': self.queue_snapshots[-10:]  # Last 10 snapshots only
        }
    
    def import_state(self, state: Dict):
        """Import state from dictionary"""
        self.session_id = state.get('session_id', self.session_id)
        self.solved_tickets = state.get('solved_tickets', {})
        self.queue_history = state.get('queue_history', {})
        self.active_tickets = set(state.get('active_tickets', []))
        self.queue_snapshots = state.get('queue_snapshots', [])
    
    def reset(self):
        """Reset all state"""
        self.solved_tickets.clear()
        self.queue_history.clear()
        self.active_tickets.clear()
        self.queue_snapshots.clear()
