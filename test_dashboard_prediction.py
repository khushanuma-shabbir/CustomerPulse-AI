"""
Test script to verify dashboard predictions work correctly
"""
import pickle
from app.data_loader import load_tickets

# Load model
print("Loading model...")
with open('model/priority_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load a sample ticket from database
print("Loading sample ticket...")
df = load_tickets()
sample_ticket = df.iloc[0].to_dict()

print(f"\nSample ticket ID: {sample_ticket.get('ticket_id')}")
print(f"Ground truth priority: {sample_ticket.get('ground_truth_priority')}")

# Show boolean column values before preprocessing
print("\nBoolean columns BEFORE preprocessing:")
print(f"  sla_breached: {sample_ticket.get('sla_breached')} (type: {type(sample_ticket.get('sla_breached'))})")
print(f"  security_related: {sample_ticket.get('security_related')} (type: {type(sample_ticket.get('security_related'))})")
print(f"  previous_escalation: {sample_ticket.get('previous_escalation')} (type: {type(sample_ticket.get('previous_escalation'))})")

# Preprocess ticket data
def preprocess_ticket(ticket_data):
    """Preprocess ticket data to match training format"""
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

# Preprocess
processed = preprocess_ticket(sample_ticket)

print("\nBoolean columns AFTER preprocessing:")
print(f"  sla_breached: {processed.get('sla_breached')} (type: {type(processed.get('sla_breached'))})")
print(f"  security_related: {processed.get('security_related')} (type: {type(processed.get('security_related'))})")
print(f"  previous_escalation: {processed.get('previous_escalation')} (type: {type(processed.get('previous_escalation'))})")

# Try prediction
print("\nMaking prediction...")
import pandas as pd
df_pred = pd.DataFrame([processed])

try:
    predicted_priority = model.predict(df_pred)[0]
    proba = model.predict_proba(df_pred)[0]
    class_labels = model.named_steps['classifier'].classes_
    priority_idx = list(class_labels).index(predicted_priority)
    confidence = float(proba[priority_idx])
    
    print(f"\n✓ SUCCESS!")
    print(f"Predicted priority: {predicted_priority}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Ground truth: {sample_ticket.get('ground_truth_priority')}")
    
    if predicted_priority == sample_ticket.get('ground_truth_priority'):
        print("✓ Prediction matches ground truth!")
    else:
        print("⚠ Prediction differs from ground truth (this is normal)")
    
except Exception as e:
    print(f"\n✗ FAILED!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
