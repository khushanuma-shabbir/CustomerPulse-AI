"""
Data preprocessing module for CustomerPulse AI
Prepares ticket data for ML model training and prediction
"""
import pandas as pd
from app.data_loader import load_tickets


def get_feature_columns():
    """Define which columns to use as ML features"""
    # Exclude: ticket_id, customer_id, timestamps, text fields, target, data_loss_risk
    # Investigate original_priority_score for potential leakage - excluding for now
    return [
        "customer_tier",
        "product",
        "product_category",
        "product_criticality",
        "issue_type",
        "channel",
        "current_severity",
        "sla_target_hours",
        "sla_remaining_hours",
        "sla_breached",
        "reopen_count",
        "customer_contact_count",
        "production_impact",
        "business_impact",
        "affected_users_estimate",
        "security_related",
        "customer_sentiment",
        "urgency_keywords",
        "waiting_time_hours",
        "status",
        "assigned_team",
        "previous_escalation"
    ]


def get_categorical_features():
    """Define categorical features for encoding"""
    return [
        "customer_tier",
        "product",
        "product_category",
        "product_criticality",
        "issue_type",
        "channel",
        "current_severity",
        "production_impact",
        "business_impact",
        "customer_sentiment",
        "urgency_keywords",
        "status",
        "assigned_team"
    ]


def get_numerical_features():
    """Define numerical features"""
    return [
        "sla_target_hours",
        "sla_remaining_hours",
        "sla_breached",
        "reopen_count",
        "customer_contact_count",
        "affected_users_estimate",
        "security_related",
        "waiting_time_hours",
        "previous_escalation"
    ]


def preprocess_data(df, for_training=True):
    """
    Preprocess ticket data for ML
    
    Args:
        df: DataFrame with raw ticket data
        for_training: If True, includes target column
        
    Returns:
        X: Features DataFrame
        y: Target Series (if for_training=True)
        ticket_ids: Original ticket IDs for reference
    """
    # Store ticket IDs for reference
    ticket_ids = df["ticket_id"].copy() if "ticket_id" in df.columns else None
    
    # Get feature columns
    feature_cols = get_feature_columns()
    
    # Select features
    available_features = [col for col in feature_cols if col in df.columns]
    X = df[available_features].copy()
    
    # Convert Yes/No boolean columns to 1/0
    boolean_columns = ["sla_breached", "security_related", "previous_escalation"]
    for col in boolean_columns:
        if col in X.columns:
            X[col] = X[col].map({"Yes": 1, "No": 0, 1: 1, 0: 0})
            X[col] = X[col].fillna(0).astype(int)
    
    # Handle missing values in numerical columns
    numerical_cols = get_numerical_features()
    for col in numerical_cols:
        if col in X.columns and col not in boolean_columns:
            X[col] = pd.to_numeric(X[col], errors='coerce')
            X[col] = X[col].fillna(X[col].median())
    
    # Handle missing values in categorical columns
    categorical_cols = get_categorical_features()
    for col in categorical_cols:
        if col in X.columns:
            X[col] = X[col].fillna("Unknown").astype(str)
    
    if for_training:
        # Get target variable
        y = df["ground_truth_priority"].copy()
        # Remove any rows with missing target
        valid_idx = y.notna()
        X = X[valid_idx]
        y = y[valid_idx]
        if ticket_ids is not None:
            ticket_ids = ticket_ids[valid_idx]
        return X, y, ticket_ids
    else:
        return X, ticket_ids


def load_and_preprocess_data():
    """
    Load tickets from Supabase and preprocess for training
    
    Returns:
        X: Features DataFrame
        y: Target Series
        ticket_ids: Ticket IDs
    """
    print("Loading tickets from Supabase...")
    df = load_tickets()
    
    print(f"\nOriginal shape: {df.shape}")
    print(f"Target distribution:\n{df['ground_truth_priority'].value_counts()}")
    
    print("\nPreprocessing data...")
    X, y, ticket_ids = preprocess_data(df, for_training=True)
    
    print(f"\nFinal shape: {X.shape}")
    print(f"Features: {len(X.columns)}")
    print(f"Categorical features: {len(get_categorical_features())}")
    print(f"Numerical features: {len(get_numerical_features())}")
    
    print("\nMissing values per column:")
    missing = X.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("None")
    
    return X, y, ticket_ids


if __name__ == "__main__":
    X, y, ticket_ids = load_and_preprocess_data()
    print("\n" + "="*50)
    print("Preprocessing completed successfully!")
    print("="*50)