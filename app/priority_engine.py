"""
Priority Prediction and Explanation Engine
Provides AI-powered priority predictions with human-readable explanations
"""
import pickle
import pandas as pd
from typing import Dict, List, Tuple


class PriorityEngine:
    """Main engine for ticket priority prediction and explanation"""
    
    def __init__(self, model_path='model/priority_model.pkl'):
        """Load trained model"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        print(f"Priority model loaded from {model_path}")
    
    def _preprocess_ticket(self, ticket_data: Dict) -> Dict:
        """Preprocess ticket data to match training format"""
        # Create a copy to avoid modifying original
        processed = ticket_data.copy()
        
        # Convert Yes/No to 1/0 for boolean columns
        boolean_columns = ["sla_breached", "security_related", "previous_escalation"]
        for col in boolean_columns:
            if col in processed:
                val = processed[col]
                if val == "Yes" or val == 1:
                    processed[col] = 1
                elif val == "No" or val == 0:
                    processed[col] = 0
                else:
                    processed[col] = 0
        
        # Ensure numerical columns are numeric
        numerical_cols = [
            "sla_target_hours", "sla_remaining_hours", "reopen_count",
            "customer_contact_count", "affected_users_estimate", "waiting_time_hours"
        ]
        for col in numerical_cols:
            if col in processed:
                try:
                    processed[col] = float(processed[col]) if processed[col] is not None else 0.0
                except:
                    processed[col] = 0.0
        
        # Ensure categorical columns are strings
        categorical_cols = [
            "customer_tier", "product", "product_category", "product_criticality",
            "issue_type", "channel", "current_severity", "production_impact",
            "business_impact", "customer_sentiment", "urgency_keywords",
            "status", "assigned_team"
        ]
        for col in categorical_cols:
            if col in processed:
                processed[col] = str(processed[col]) if processed[col] is not None else "Unknown"
        
        return processed
    
    def predict_priority(self, ticket_data: Dict) -> Dict:
        """
        Predict priority for a single ticket
        
        Args:
            ticket_data: Dictionary with ticket features
            
        Returns:
            Dictionary with prediction and explanation
        """
        # Preprocess ticket data
        processed_ticket = self._preprocess_ticket(ticket_data)
        
        # Convert to DataFrame
        df = pd.DataFrame([processed_ticket])
        
        # Predict
        predicted_priority = self.model.predict(df)[0]
        
        # Get probability/confidence if available
        confidence = None
        try:
            proba = self.model.predict_proba(df)[0]
            class_labels = self.model.named_steps['classifier'].classes_
            priority_idx = list(class_labels).index(predicted_priority)
            confidence = float(proba[priority_idx])
        except:
            confidence = None
        
        # Generate explanation (use original ticket data)
        reasons = self._generate_explanation(ticket_data, predicted_priority)
        
        return {
            'predicted_priority': predicted_priority,
            'confidence': confidence,
            'reasons': reasons,
            'ticket_id': ticket_data.get('ticket_id', 'N/A')
        }
    
    def _generate_explanation(self, ticket_data: Dict, predicted_priority: str) -> List[str]:
        """
        Generate human-readable explanation for the prediction
        
        This is a rule-based explanation system that identifies
        the most impactful factors based on ticket attributes.
        """
        reasons = []
        
        # Production Impact
        production_impact = ticket_data.get('production_impact', '')
        if production_impact in ['Major', 'Critical', 'Severe']:
            reasons.append(f"Major production impact ({production_impact})")
        elif production_impact == 'Moderate':
            reasons.append(f"Moderate production impact")
        
        # Business Impact
        business_impact = ticket_data.get('business_impact', '')
        if business_impact in ['High', 'Critical', 'Severe']:
            reasons.append(f"High business impact ({business_impact})")
        
        # SLA Status
        sla_breached = ticket_data.get('sla_breached', 0)
        sla_remaining = ticket_data.get('sla_remaining_hours', 999)
        if sla_breached == 1 or sla_breached == 'Yes':
            reasons.append("SLA has been breached")
        elif sla_remaining < 2:
            reasons.append(f"SLA at risk (only {sla_remaining:.1f} hours remaining)")
        elif sla_remaining < 4:
            reasons.append("Low SLA time remaining")
        
        # Affected Users
        affected_users = ticket_data.get('affected_users_estimate', 0)
        if affected_users >= 1000:
            reasons.append(f"Large number of affected users ({affected_users}+)")
        elif affected_users >= 100:
            reasons.append(f"Multiple users affected ({affected_users}+)")
        
        # Customer Tier
        customer_tier = ticket_data.get('customer_tier', '')
        if customer_tier in ['Platinum', 'Enterprise', 'Premium']:
            reasons.append(f"{customer_tier} tier customer")
        
        # Security Related
        security_related = ticket_data.get('security_related', 0)
        if security_related == 1 or security_related == 'Yes':
            reasons.append("Security-related issue")
        
        # Product Criticality
        product_criticality = ticket_data.get('product_criticality', '')
        if product_criticality in ['Critical', 'High']:
            reasons.append(f"{product_criticality} criticality product")
        
        # Current Severity
        current_severity = ticket_data.get('current_severity', '')
        if current_severity in ['Critical', 'Urgent', 'High']:
            reasons.append(f"{current_severity} severity reported")
        
        # Reopen Count
        reopen_count = ticket_data.get('reopen_count', 0)
        if reopen_count >= 3:
            reasons.append(f"Ticket reopened multiple times ({reopen_count})")
        elif reopen_count >= 1:
            reasons.append(f"Ticket has been reopened")
        
        # Customer Contact Count
        contact_count = ticket_data.get('customer_contact_count', 0)
        if contact_count >= 5:
            reasons.append(f"High customer contact frequency ({contact_count} contacts)")
        
        # Previous Escalation
        previous_escalation = ticket_data.get('previous_escalation', 0)
        if previous_escalation == 1 or previous_escalation == 'Yes':
            reasons.append("Previously escalated")
        
        # Urgency Keywords
        urgency_keywords = ticket_data.get('urgency_keywords', '')
        if urgency_keywords in ['Critical', 'Urgent', 'Emergency']:
            reasons.append(f"Urgent language detected: {urgency_keywords}")
        
        # Customer Sentiment
        sentiment = ticket_data.get('customer_sentiment', '')
        if sentiment in ['Angry', 'Very Negative', 'Frustrated']:
            reasons.append(f"Negative customer sentiment ({sentiment})")
        
        # Waiting Time
        waiting_time = ticket_data.get('waiting_time_hours', 0)
        if waiting_time >= 48:
            reasons.append(f"Extended waiting time ({waiting_time:.0f} hours)")
        elif waiting_time >= 24:
            reasons.append(f"Long waiting time ({waiting_time:.0f} hours)")
        
        # Issue Type
        issue_type = ticket_data.get('issue_type', '')
        if issue_type in ['Outage', 'Data Loss', 'Security Breach', 'System Down']:
            reasons.append(f"Critical issue type: {issue_type}")
        
        # If no specific reasons found, provide general ones
        if not reasons:
            if predicted_priority == 'Critical':
                reasons.append("Multiple high-impact factors identified")
            elif predicted_priority == 'High':
                reasons.append("Several significant factors detected")
            elif predicted_priority == 'Medium':
                reasons.append("Standard priority indicators present")
            else:
                reasons.append("No urgent factors identified")
        
        # Limit to top 5 most important reasons
        return reasons[:5]
    
    def batch_predict(self, tickets: List[Dict]) -> List[Dict]:
        """
        Predict priorities for multiple tickets
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            List of prediction results
        """
        results = []
        for ticket in tickets:
            try:
                result = self.predict_priority(ticket)
                results.append(result)
            except Exception as e:
                results.append({
                    'ticket_id': ticket.get('ticket_id', 'N/A'),
                    'error': str(e),
                    'predicted_priority': 'Error',
                    'confidence': None,
                    'reasons': [f"Prediction failed: {str(e)}"]
                })
        return results


def test_engine():
    """Test the priority engine with sample data"""
    print("="*60)
    print("Testing Priority Engine")
    print("="*60)
    
    # Load engine
    engine = PriorityEngine()
    
    # Test ticket 1: Critical scenario
    test_ticket_1 = {
        'ticket_id': 'TEST-001',
        'customer_tier': 'Platinum',
        'product': 'Core Platform',
        'product_category': 'Infrastructure',
        'product_criticality': 'Critical',
        'issue_type': 'Outage',
        'channel': 'Phone',
        'current_severity': 'Critical',
        'sla_target_hours': 4,
        'sla_remaining_hours': 1.5,
        'sla_breached': 0,
        'reopen_count': 0,
        'customer_contact_count': 3,
        'production_impact': 'Major',
        'business_impact': 'High',
        'affected_users_estimate': 5000,
        'security_related': 0,
        'customer_sentiment': 'Frustrated',
        'urgency_keywords': 'Critical',
        'waiting_time_hours': 2,
        'status': 'Open',
        'assigned_team': 'Platform',
        'previous_escalation': 0
    }
    
    print("\nTest Ticket 1 - Critical Scenario:")
    result_1 = engine.predict_priority(test_ticket_1)
    print(f"Predicted Priority: {result_1['predicted_priority']}")
    if result_1['confidence']:
        print(f"Confidence: {result_1['confidence']:.2%}")
    print("Reasons:")
    for reason in result_1['reasons']:
        print(f"  • {reason}")
    
    # Test ticket 2: Low priority scenario
    test_ticket_2 = {
        'ticket_id': 'TEST-002',
        'customer_tier': 'Standard',
        'product': 'Documentation',
        'product_category': 'Support',
        'product_criticality': 'Low',
        'issue_type': 'Question',
        'channel': 'Email',
        'current_severity': 'Low',
        'sla_target_hours': 48,
        'sla_remaining_hours': 40,
        'sla_breached': 0,
        'reopen_count': 0,
        'customer_contact_count': 1,
        'production_impact': 'None',
        'business_impact': 'Low',
        'affected_users_estimate': 1,
        'security_related': 0,
        'customer_sentiment': 'Neutral',
        'urgency_keywords': 'None',
        'waiting_time_hours': 3,
        'status': 'Open',
        'assigned_team': 'Support',
        'previous_escalation': 0
    }
    
    print("\n" + "="*60)
    print("\nTest Ticket 2 - Low Priority Scenario:")
    result_2 = engine.predict_priority(test_ticket_2)
    print(f"Predicted Priority: {result_2['predicted_priority']}")
    if result_2['confidence']:
        print(f"Confidence: {result_2['confidence']:.2%}")
    print("Reasons:")
    for reason in result_2['reasons']:
        print(f"  • {reason}")
    
    print("\n" + "="*60)
    print("Priority Engine test completed!")
    print("="*60)


if __name__ == "__main__":
    test_engine()
