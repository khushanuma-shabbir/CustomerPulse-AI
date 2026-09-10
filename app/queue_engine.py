"""
Dynamic Time-Aware Queue Engine for CustomerPulse AI
Combines ML predictions with time factors, aging, and starvation detection
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


class QueueConfig:
    """Configuration for queue scoring and aging thresholds"""
    
    # Aging thresholds (hours)
    AGING_MEDIUM_THRESHOLD = 24  # After 24 hours, Low can become Medium
    AGING_HIGH_THRESHOLD = 48     # After 48 hours, Medium can become High
    AGING_CRITICAL_THRESHOLD = 72 # After 72 hours, High can become Critical
    
    # Starvation detection thresholds
    STARVATION_BYPASS_THRESHOLD = 5  # Times bypassed before starvation risk
    STARVATION_AGE_THRESHOLD = 12     # Hours old before starvation consideration
    
    # SLA risk thresholds (hours)
    SLA_CRITICAL_THRESHOLD = 2  # SLA < 2 hours = critical
    SLA_HIGH_THRESHOLD = 4      # SLA < 4 hours = high risk
    
    # Score weights for final priority calculation
    WEIGHT_ML_PRIORITY = 1.0
    WEIGHT_SLA_RISK = 1.5
    WEIGHT_IMPACT = 1.2
    WEIGHT_AGING = 0.8
    WEIGHT_STARVATION = 1.0
    WEIGHT_SECURITY = 1.3
    WEIGHT_URGENCY = 0.7


class QueueEngine:
    """
    Dynamic Queue Engine
    
    Responsibilities:
    - Calculate ticket age from current datetime
    - Apply aging logic (old tickets get priority boost)
    - Apply starvation detection (repeatedly bypassed tickets get boost)
    - Calculate dynamic SLA status
    - Combine ML prediction with business rules
    - Rank tickets by final priority score
    """
    
    def __init__(self, config: QueueConfig = None):
        """Initialize queue engine with configuration"""
        self.config = config or QueueConfig()
        self.priority_values = {
            'Critical': 4,
            'High': 3,
            'Medium': 2,
            'Low': 1
        }
    
    def calculate_ticket_age(self, created_at: str, current_time: datetime = None) -> float:
        """
        Calculate ticket age in hours from current time
        
        Args:
            created_at: ISO timestamp string or datetime
            current_time: Current datetime (defaults to now)
            
        Returns:
            Age in hours
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Parse created_at if it's a string
        if isinstance(created_at, str):
            try:
                # Try ISO format first
                created_dt = pd.to_datetime(created_at)
            except:
                # Fallback to other formats
                created_dt = pd.to_datetime(created_at, errors='coerce')
        else:
            created_dt = pd.to_datetime(created_at)
        
        # Remove timezone info to avoid tz-naive/tz-aware errors
        if hasattr(created_dt, 'tz') and created_dt.tz is not None:
            created_dt = created_dt.tz_localize(None)
        
        # Calculate age
        age = (current_time - created_dt).total_seconds() / 3600.0
        return max(0, age)  # Ensure non-negative
    
    def calculate_dynamic_sla_remaining(self, created_at: str, sla_target_hours: float, 
                                       current_time: datetime = None) -> Tuple[float, str]:
        """
        Calculate dynamic SLA remaining from current time
        
        Args:
            created_at: Ticket creation timestamp
            sla_target_hours: SLA target in hours
            current_time: Current datetime (defaults to now)
            
        Returns:
            Tuple of (sla_remaining_hours, sla_status)
        """
        if current_time is None:
            current_time = datetime.now()
        
        ticket_age = self.calculate_ticket_age(created_at, current_time)
        sla_remaining = sla_target_hours - ticket_age
        
        # Determine SLA status
        if sla_remaining <= 0:
            status = "BREACHED"
        elif sla_remaining < self.config.SLA_CRITICAL_THRESHOLD:
            status = "CRITICAL_RISK"
        elif sla_remaining < self.config.SLA_HIGH_THRESHOLD:
            status = "HIGH_RISK"
        else:
            status = "OK"
        
        return sla_remaining, status
    
    def calculate_aging_boost(self, ticket_age_hours: float, current_priority: str) -> Tuple[int, str, str]:
        """
        Calculate aging boost based on ticket age
        
        Args:
            ticket_age_hours: Age of ticket in hours
            current_priority: Current ML-predicted priority
            
        Returns:
            Tuple of (boost_score, aging_status, aging_reason)
        """
        boost = 0
        status = "NONE"
        reason = ""
        
        # Age-based priority escalation
        if ticket_age_hours >= self.config.AGING_CRITICAL_THRESHOLD:
            boost = 3
            status = "CRITICAL"
            reason = f"Ticket has been waiting for {ticket_age_hours:.1f} hours (>72h)"
        elif ticket_age_hours >= self.config.AGING_HIGH_THRESHOLD:
            boost = 2
            status = "HIGH"
            reason = f"Ticket has been waiting for {ticket_age_hours:.1f} hours (>48h)"
        elif ticket_age_hours >= self.config.AGING_MEDIUM_THRESHOLD:
            boost = 1
            status = "MEDIUM"
            reason = f"Ticket has been waiting for {ticket_age_hours:.1f} hours (>24h)"
        else:
            status = "NONE"
            reason = "No aging concerns"
        
        return boost, status, reason
    
    def calculate_starvation_risk(self, times_bypassed: int, ticket_age_hours: float,
                                  last_position: int = None) -> Tuple[int, str, str]:
        """
        Calculate starvation risk and boost
        
        Starvation occurs when a ticket is repeatedly bypassed by newer high-priority tickets
        
        Args:
            times_bypassed: Number of times this ticket was bypassed
            ticket_age_hours: Age of ticket
            last_position: Last queue position
            
        Returns:
            Tuple of (boost_score, starvation_status, starvation_reason)
        """
        boost = 0
        status = "NONE"
        reason = "No starvation risk"
        
        # Only check if ticket is old enough
        if ticket_age_hours < self.config.STARVATION_AGE_THRESHOLD:
            return boost, status, reason
        
        # Calculate risk based on bypass count
        if times_bypassed >= self.config.STARVATION_BYPASS_THRESHOLD:
            # High starvation risk
            boost = 2 + (times_bypassed - self.config.STARVATION_BYPASS_THRESHOLD)
            status = "HIGH"
            reason = f"Ticket has been bypassed {times_bypassed} times while waiting {ticket_age_hours:.1f}h"
        elif times_bypassed >= 3:
            # Medium starvation risk
            boost = 1
            status = "MEDIUM"
            reason = f"Ticket has been bypassed {times_bypassed} times"
        
        return boost, status, reason
    
    def calculate_impact_score(self, ticket: Dict) -> Tuple[float, List[str]]:
        """
        Calculate business impact score from ticket attributes
        
        Args:
            ticket: Ticket dictionary with all attributes
            
        Returns:
            Tuple of (impact_score, impact_reasons)
        """
        score = 0
        reasons = []
        
        # Production Impact
        production_impact = ticket.get('production_impact', '')
        if production_impact in ['Major', 'Critical', 'Severe']:
            score += 3
            reasons.append(f"Major production impact ({production_impact})")
        elif production_impact in ['Moderate', 'Medium']:
            score += 1.5
            reasons.append(f"Moderate production impact")
        
        # Business Impact
        business_impact = ticket.get('business_impact', '')
        if business_impact in ['High', 'Critical', 'Severe']:
            score += 2.5
            reasons.append(f"High business impact")
        elif business_impact in ['Medium', 'Moderate']:
            score += 1
        
        # Affected Users
        affected_users = ticket.get('affected_users_estimate', 0)
        if affected_users >= 5000:
            score += 3
            reasons.append(f"Large user impact ({affected_users:,}+ users)")
        elif affected_users >= 1000:
            score += 2
            reasons.append(f"Significant user impact ({affected_users:,}+ users)")
        elif affected_users >= 100:
            score += 1
        
        # Customer Tier
        customer_tier = ticket.get('customer_tier', '')
        if customer_tier in ['Platinum', 'Enterprise']:
            score += 2
            reasons.append(f"{customer_tier} tier customer")
        elif customer_tier in ['Premium', 'Gold']:
            score += 1
            reasons.append(f"{customer_tier} tier customer")
        
        # Product Criticality
        product_criticality = ticket.get('product_criticality', '')
        if product_criticality in ['Critical', 'High']:
            score += 1.5
            reasons.append(f"{product_criticality} criticality product")
        
        return score, reasons
    
    def calculate_security_urgency_score(self, ticket: Dict) -> Tuple[float, List[str]]:
        """
        Calculate security and urgency score
        
        Args:
            ticket: Ticket dictionary
            
        Returns:
            Tuple of (score, reasons)
        """
        score = 0
        reasons = []
        
        # Security Related
        security_related = ticket.get('security_related', 0)
        if security_related in [1, 'Yes', True]:
            score += 3
            reasons.append("Security-related issue")
        
        # Urgency Keywords
        urgency_keywords = ticket.get('urgency_keywords', '')
        if urgency_keywords in ['Critical', 'Urgent', 'Emergency']:
            score += 2
            reasons.append(f"Urgent: {urgency_keywords}")
        
        # Current Severity
        current_severity = ticket.get('current_severity', '')
        if current_severity in ['Critical', 'Sev-1', 'Urgent']:
            score += 2
            reasons.append(f"{current_severity} severity")
        elif current_severity in ['High', 'Sev-2']:
            score += 1
        
        # Previous Escalation
        previous_escalation = ticket.get('previous_escalation', 0)
        if previous_escalation in [1, 'Yes', True]:
            score += 1.5
            reasons.append("Previously escalated")
        
        # Reopen Count
        reopen_count = ticket.get('reopen_count', 0)
        if reopen_count >= 3:
            score += 1.5
            reasons.append(f"Reopened {reopen_count} times")
        elif reopen_count >= 1:
            score += 0.5
        
        return score, reasons
    
    def calculate_final_score(self, ticket: Dict, ml_priority: str, 
                             current_time: datetime = None,
                             queue_history: Dict = None) -> Dict:
        """
        Calculate final priority score combining all factors
        
        Args:
            ticket: Ticket dictionary with all attributes
            ml_priority: ML-predicted priority
            current_time: Current datetime for time calculations
            queue_history: History data for starvation detection
            
        Returns:
            Dictionary with final score, priority, and detailed breakdown
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Initialize result
        result = {
            'ticket_id': ticket.get('ticket_id', 'UNKNOWN'),
            'ml_priority': ml_priority,
            'final_priority': ml_priority,
            'final_score': 0,
            'breakdown': {},
            'reasons': []
        }
        
        # 1. ML Priority Base Score
        ml_score = self.priority_values.get(ml_priority, 1)
        result['breakdown']['ml_score'] = ml_score
        result['final_score'] = ml_score * self.config.WEIGHT_ML_PRIORITY
        
        # 2. Calculate ticket age
        created_at = ticket.get('created_at')
        if created_at:
            ticket_age = self.calculate_ticket_age(created_at, current_time)
            result['ticket_age_hours'] = round(ticket_age, 2)
            
            # 3. Calculate dynamic SLA
            sla_target = ticket.get('sla_target_hours', 24)
            sla_remaining, sla_status = self.calculate_dynamic_sla_remaining(
                created_at, sla_target, current_time
            )
            result['sla_remaining_hours'] = round(sla_remaining, 2)
            result['sla_status'] = sla_status
            
            # SLA Risk Score
            if sla_status == "BREACHED":
                sla_score = 4
                result['reasons'].append(f"⚠️ SLA BREACHED")
            elif sla_status == "CRITICAL_RISK":
                sla_score = 3
                result['reasons'].append(f"⏰ SLA Critical: {sla_remaining:.1f}h remaining")
            elif sla_status == "HIGH_RISK":
                sla_score = 2
                result['reasons'].append(f"⏰ SLA at Risk: {sla_remaining:.1f}h remaining")
            else:
                sla_score = 0
            
            result['breakdown']['sla_score'] = sla_score
            result['final_score'] += sla_score * self.config.WEIGHT_SLA_RISK
            
            # 4. Aging Boost
            aging_boost, aging_status, aging_reason = self.calculate_aging_boost(
                ticket_age, ml_priority
            )
            result['aging_status'] = aging_status
            result['aging_boost'] = aging_boost
            result['breakdown']['aging_score'] = aging_boost
            result['final_score'] += aging_boost * self.config.WEIGHT_AGING
            
            if aging_boost > 0:
                result['reasons'].append(f"⏳ {aging_reason}")
        
        # 5. Starvation Detection
        times_bypassed = 0
        if queue_history:
            ticket_id = ticket.get('ticket_id')
            ticket_history = queue_history.get(ticket_id)
            
            # Defensive: handle both dict and int formats
            if isinstance(ticket_history, dict):
                times_bypassed = ticket_history.get('times_bypassed', 0)
            elif isinstance(ticket_history, int):
                times_bypassed = ticket_history
            else:
                times_bypassed = 0
        
        starvation_boost, starvation_status, starvation_reason = self.calculate_starvation_risk(
            times_bypassed, 
            result.get('ticket_age_hours', 0)
        )
        result['starvation_status'] = starvation_status
        result['starvation_boost'] = starvation_boost
        result['breakdown']['starvation_score'] = starvation_boost
        result['final_score'] += starvation_boost * self.config.WEIGHT_STARVATION
        
        if starvation_boost > 0:
            result['reasons'].append(f"🚨 {starvation_reason}")
        
        # 6. Impact Score
        impact_score, impact_reasons = self.calculate_impact_score(ticket)
        result['breakdown']['impact_score'] = impact_score
        result['final_score'] += impact_score * self.config.WEIGHT_IMPACT
        result['reasons'].extend([f"💼 {r}" for r in impact_reasons])
        
        # 7. Security & Urgency Score
        security_score, security_reasons = self.calculate_security_urgency_score(ticket)
        result['breakdown']['security_urgency_score'] = security_score
        result['final_score'] += security_score * self.config.WEIGHT_SECURITY
        result['reasons'].extend([f"🔒 {r}" for r in security_reasons])
        
        # 8. Determine final priority based on total score
        # Score ranges (approximately):
        # Critical: > 15
        # High: 10-15
        # Medium: 5-10
        # Low: < 5
        final_score = result['final_score']
        if final_score >= 15:
            result['final_priority'] = 'Critical'
        elif final_score >= 10:
            result['final_priority'] = 'High'
        elif final_score >= 5:
            result['final_priority'] = 'Medium'
        else:
            result['final_priority'] = 'Low'
        
        # Round final score
        result['final_score'] = round(final_score, 2)
        
        # Add summary if priority was boosted
        if result['final_priority'] != ml_priority:
            result['reasons'].insert(0, 
                f"📊 Priority boosted from {ml_priority} to {result['final_priority']}")
        
        return result
    
    def rank_tickets(self, tickets_with_scores: List[Dict]) -> List[Dict]:
        """
        Rank tickets by final score (highest first)
        
        Args:
            tickets_with_scores: List of ticket result dictionaries
            
        Returns:
            Ranked list with queue positions
        """
        # Sort by final_score descending
        ranked = sorted(tickets_with_scores, key=lambda x: x['final_score'], reverse=True)
        
        # Add queue position
        for idx, ticket in enumerate(ranked, start=1):
            ticket['queue_position'] = idx
        
        return ranked
    
    def get_next_ticket(self, ranked_tickets: List[Dict]) -> Dict:
        """
        Get the next ticket that should be solved
        
        Args:
            ranked_tickets: List of ranked tickets
            
        Returns:
            Next ticket to solve (highest priority)
        """
        if not ranked_tickets:
            return None
        
        return ranked_tickets[0]
