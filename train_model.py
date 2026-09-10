"""
ML Model Training Pipeline for CustomerPulse AI
Trains a Random Forest classifier to predict ticket priority
"""
import pandas as pd
import numpy as np
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from app.preprocess import (
    load_and_preprocess_data,
    get_categorical_features,
    get_numerical_features
)

# Set random state for reproducibility
RANDOM_STATE = 42


def create_preprocessing_pipeline():
    """Create sklearn preprocessing pipeline"""
    categorical_features = get_categorical_features()
    numerical_features = get_numerical_features()
    
    # OneHotEncoder for categorical features
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', 'passthrough', numerical_features)
        ],
        remainder='drop'
    )
    
    return preprocessor


def train_random_forest(X_train, y_train):
    """Train Random Forest Classifier"""
    print("\n" + "="*60)
    print("Training Random Forest Classifier")
    print("="*60)
    
    preprocessor = create_preprocessing_pipeline()
    
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            class_weight='balanced',
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ])
    
    model.fit(X_train, y_train)
    return model


def train_logistic_regression(X_train, y_train):
    """Train Logistic Regression"""
    print("\n" + "="*60)
    print("Training Logistic Regression")
    print("="*60)
    
    preprocessor = create_preprocessing_pipeline()
    
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ])
    
    model.fit(X_train, y_train)
    return model


def train_decision_tree(X_train, y_train):
    """Train Decision Tree Classifier"""
    print("\n" + "="*60)
    print("Training Decision Tree Classifier")
    print("="*60)
    
    preprocessor = create_preprocessing_pipeline()
    
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', DecisionTreeClassifier(
            max_depth=12,
            min_samples_split=10,
            min_samples_leaf=4,
            class_weight='balanced',
            random_state=RANDOM_STATE
        ))
    ])
    
    model.fit(X_train, y_train)
    return model


def train_gradient_boosting(X_train, y_train):
    """Train Histogram-based Gradient Boosting Classifier"""
    print("\n" + "="*60)
    print("Training Gradient Boosting Classifier")
    print("="*60)
    
    preprocessor = create_preprocessing_pipeline()
    
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', HistGradientBoostingClassifier(
            max_iter=200,
            max_depth=10,
            learning_rate=0.1,
            random_state=RANDOM_STATE
        ))
    ])
    
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test, model_name="Model"):
    """Evaluate model performance"""
    y_pred = model.predict(X_test)
    
    print(f"\n{'='*60}")
    print(f"{model_name} - Evaluation Results")
    print(f"{'='*60}")
    
    # Overall metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    # Per-class metrics
    precision = precision_score(y_test, y_pred, average=None, labels=['Critical', 'High', 'Medium', 'Low'], zero_division=0)
    recall = recall_score(y_test, y_pred, average=None, labels=['Critical', 'High', 'Medium', 'Low'], zero_division=0)
    f1 = f1_score(y_test, y_pred, average=None, labels=['Critical', 'High', 'Medium', 'Low'], zero_division=0)
    
    # Macro averages
    macro_precision = precision_score(y_test, y_pred, average='macro', zero_division=0)
    macro_recall = recall_score(y_test, y_pred, average='macro', zero_division=0)
    macro_f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    
    print(f"\nAccuracy: {accuracy:.4f}")
    print(f"Macro Precision: {macro_precision:.4f}")
    print(f"Macro Recall: {macro_recall:.4f}")
    print(f"Macro F1-Score: {macro_f1:.4f}")
    
    print("\nPer-Class Metrics:")
    print(f"{'Priority':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 48)
    priorities = ['Critical', 'High', 'Medium', 'Low']
    for i, priority in enumerate(priorities):
        print(f"{priority:<12} {precision[i]:<12.4f} {recall[i]:<12.4f} {f1[i]:<12.4f}")
    
    print("\n" + "="*60)
    print("Classification Report")
    print("="*60)
    print(classification_report(y_test, y_pred, zero_division=0))
    
    print("\n" + "="*60)
    print("Confusion Matrix")
    print("="*60)
    cm = confusion_matrix(y_test, y_pred, labels=['Critical', 'High', 'Medium', 'Low'])
    cm_df = pd.DataFrame(cm, 
                         index=['Critical', 'High', 'Medium', 'Low'],
                         columns=['Critical', 'High', 'Medium', 'Low'])
    print(cm_df)
    
    # Return metrics dictionary
    metrics = {
        'accuracy': float(accuracy),
        'macro_precision': float(macro_precision),
        'macro_recall': float(macro_recall),
        'macro_f1': float(macro_f1),
        'per_class': {
            priorities[i]: {
                'precision': float(precision[i]),
                'recall': float(recall[i]),
                'f1': float(f1[i])
            }
            for i in range(len(priorities))
        },
        'confusion_matrix': cm.tolist()
    }
    
    return metrics


def get_feature_importance(model, feature_names, top_n=20):
    """Extract feature importance from trained model"""
    try:
        if hasattr(model.named_steps['classifier'], 'feature_importances_'):
            importances = model.named_steps['classifier'].feature_importances_
            
            # Get feature names after preprocessing
            preprocessor = model.named_steps['preprocessor']
            feature_names_transformed = preprocessor.get_feature_names_out()
            
            # Create importance DataFrame
            importance_df = pd.DataFrame({
                'feature': feature_names_transformed,
                'importance': importances
            }).sort_values('importance', ascending=False).head(top_n)
            
            print(f"\n{'='*60}")
            print(f"Top {top_n} Most Important Features")
            print(f"{'='*60}")
            print(importance_df.to_string(index=False))
            
            return importance_df
    except Exception as e:
        print(f"\nFeature importance not available for this model: {e}")
        return None


def main():
    """Main training pipeline"""
    print("="*60)
    print("CustomerPulse AI - Model Training Pipeline")
    print("="*60)
    
    # Load and preprocess data
    X, y, ticket_ids = load_and_preprocess_data()
    
    # Train-test split with stratification
    print(f"\nSplitting data (80% train, 20% test) with stratification...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=RANDOM_STATE,
        stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    print(f"\nTraining set distribution:\n{y_train.value_counts()}")
    print(f"\nTest set distribution:\n{y_test.value_counts()}")
    
    # Train models
    models = {
        'Random Forest': train_random_forest(X_train, y_train),
        'Logistic Regression': train_logistic_regression(X_train, y_train),
        'Decision Tree': train_decision_tree(X_train, y_train),
        'Gradient Boosting': train_gradient_boosting(X_train, y_train)
    }
    
    # Evaluate all models
    all_metrics = {}
    for model_name, model in models.items():
        metrics = evaluate_model(model, X_test, y_test, model_name)
        all_metrics[model_name] = metrics
        
        # Show feature importance for tree-based models
        if model_name in ['Random Forest', 'Decision Tree', 'Gradient Boosting']:
            get_feature_importance(model, X.columns.tolist())
    
    # Select best model (based on macro F1-score)
    best_model_name = max(all_metrics.keys(), key=lambda k: all_metrics[k]['macro_f1'])
    best_model = models[best_model_name]
    best_metrics = all_metrics[best_model_name]
    
    print("\n" + "="*60)
    print(f"BEST MODEL: {best_model_name}")
    print(f"Macro F1-Score: {best_metrics['macro_f1']:.4f}")
    print("="*60)
    
    # Save best model
    print("\nSaving model and metrics...")
    with open('model/priority_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    
    with open('model/model_metrics.json', 'w') as f:
        json.dump({
            'best_model': best_model_name,
            'metrics': best_metrics,
            'all_model_metrics': all_metrics,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'features_used': X.columns.tolist(),
            'random_state': RANDOM_STATE
        }, f, indent=2)
    
    print("\n✓ Model saved to: model/priority_model.pkl")
    print("✓ Metrics saved to: model/model_metrics.json")
    
    print("\n" + "="*60)
    print("Training completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
