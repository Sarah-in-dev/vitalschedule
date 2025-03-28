#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import argparse
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, confusion_matrix
from sklearn.pipeline import Pipeline

def parse_args():
    parser = argparse.ArgumentParser(description='Build event prediction models')
    parser.add_argument('--data_dir', type=str, required=True, help='Path to processed data directory')
    parser.add_argument('--models_dir', type=str, required=True, help='Path to models directory')
    return parser.parse_args()

def load_complexity_data(data_dir):
    """Load patient data with complexity score"""
    print("Loading patient complexity data...")
    
    complexity_path = os.path.join(data_dir, 'patients_with_complexity.csv')
    complexity_data = pd.read_csv(complexity_path)
    
    return complexity_data

def define_events(patient_data):
    """Define events we want to predict"""
    print("Defining adverse events...")
    
    events = {}
    
    # Readmission event (already defined in complexity model)
    if 'readmission_flag' in patient_data.columns:
        events['readmission'] = patient_data['readmission_flag']
    
    # Mortality event
    if 'mortality_flag' in patient_data.columns:
        events['mortality'] = patient_data['mortality_flag']
    
    # Long ICU stay event
    if 'extended_icu_stay' in patient_data.columns:
        events['extended_icu_stay'] = patient_data['extended_icu_stay']
    
    # High utilizer event
    if 'admission_count' in patient_data.columns:
        events['high_utilizer'] = (patient_data['admission_count'] >= 3).astype(int)
    
    # Emergency utilization event
    if 'emergency_count' in patient_data.columns:
        events['emergency_utilizer'] = (patient_data['emergency_count'] >= 2).astype(int)
    
    return events

def build_event_prediction_models(patient_data, events, output_dir):
    """Build prediction models for each event"""
    print("Building event prediction models...")
    
    # Define features for model
    base_features = [
        'age_group', 'gender', 'unique_chronic_conditions', 'multiple_chronic_conditions',
        'unique_medication_count', 'polypharmacy_flag',
        'admission_count', 'icu_stay_count', 'emergency_count',
        'clinical_severity_score', 'complexity_score'
    ]
    
    # Filter to valid features that exist in the dataset
    valid_features = [f for f in base_features if f in patient_data.columns]
    
    # Add categorical features
    categorical_features = ['age_group', 'gender']
    categorical_features = [f for f in categorical_features if f in valid_features]
    
    # Numeric features
    numeric_features = [f for f in valid_features if f not in categorical_features]
    
    # Results dictionary
    results = {}
    
    # Build a model for each event
    for event_name, event_values in events.items():
        print(f"Building model for {event_name}...")
        
        # Prepare data
        X = patient_data[valid_features]
        y = event_values
        
        # Handle categorical features (simple one-hot encoding)
        for feature in categorical_features:
            dummies = pd.get_dummies(X[feature], prefix=feature, drop_first=True)
            X = pd.concat([X.drop(feature, axis=1), dummies], axis=1)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        pr_auc = auc(recall, precision)
        
        print(f"{event_name} Model ROC-AUC: {roc_auc:.3f}")
        print(f"{event_name} Model PR-AUC: {pr_auc:.3f}")
        
        # Get feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Create intervention recommendations based on top features
        interventions = generate_interventions(feature_importance, event_name)
        
        # Save model
        model_path = os.path.join(output_dir, f'{event_name}_model.joblib')
        joblib.dump(model, model_path)
        
        # Save feature importance
        importance_path = os.path.join(output_dir, f'{event_name}_feature_importance.csv')
        feature_importance.to_csv(importance_path, index=False)
        
        # Save interventions
        intervention_path = os.path.join(output_dir, f'{event_name}_interventions.csv')
        interventions.to_csv(intervention_path, index=False)
        
        # Store results
        results[event_name] = {
            'roc_auc': roc_auc,
            'pr_auc': pr_auc,
            'model_path': model_path,
            'importance_path': importance_path,
            'intervention_path': intervention_path
        }
    
    # Save summary of results
    results_df = pd.DataFrame([{
        'event': event_name,
        'roc_auc': result['roc_auc'],
        'pr_auc': result['pr_auc'],
        'model_path': result['model_path']
    } for event_name, result in results.items()])
    
    summary_path = os.path.join(output_dir, 'model_summary.csv')
    results_df.to_csv(summary_path, index=False)
    print(f"Model summary saved to {summary_path}")
    
    return results

def generate_interventions(feature_importance, event_name):
    """Generate intervention recommendations based on top predictive features"""
    print(f"Generating interventions for {event_name}...")
    
    # Map features to intervention categories
    intervention_mapping = {
        'unique_chronic_conditions': 'Chronic Disease Management',
        'multiple_chronic_conditions': 'Care Coordination',
        'unique_medication_count': 'Medication Management',
        'polypharmacy_flag': 'Medication Review',
        'admission_count': 'Transitional Care',
        'icu_stay_count': 'Complex Care Management',
        'emergency_count': 'Emergency Department Diversion',
        'clinical_severity_score': 'Clinical Monitoring',
        'complexity_score': 'Complex Care Management'
    }
    
    # Generic intervention descriptions
    intervention_descriptions = {
        'Chronic Disease Management': 'Enroll patient in chronic disease management program with regular monitoring and follow-up.',
        'Care Coordination': 'Assign care coordinator to manage multiple conditions and providers.',
        'Medication Management': 'Conduct comprehensive medication review and simplify regimen when possible.',
        'Medication Review': 'Schedule pharmacist consultation to review medications for interactions and simplification.',
        'Transitional Care': 'Implement post-discharge follow-up protocol with home visits or telehealth.',
        'Complex Care Management': 'Enroll in intensive care management program with frequent touchpoints.',
        'Emergency Department Diversion': 'Provide extended hours access and same-day appointments when needed.',
        'Clinical Monitoring': 'Implement remote patient monitoring for key clinical parameters.'
    }
    
    # Get top 5 features
    top_features = feature_importance.head(5)['feature'].tolist()
    
    # Generate interventions
    interventions = []
    for feature in top_features:
        for prefix, category in intervention_mapping.items():
            if prefix in feature:
                # Check if intervention already added
                if category not in [i['category'] for i in interventions]:
                    interventions.append({
                        'event': event_name,
                        'related_feature': feature,
                        'category': category,
                        'description': intervention_descriptions.get(category, 'Custom intervention needed.')
                    })
                break
    
    # Ensure we have at least 3 interventions
    if len(interventions) < 3:
        default_interventions = [
            {'event': event_name, 'related_feature': 'default', 'category': 'Care Coordination', 
             'description': intervention_descriptions['Care Coordination']},
            {'event': event_name, 'related_feature': 'default', 'category': 'Medication Review', 
             'description': intervention_descriptions['Medication Review']},
            {'event': event_name, 'related_feature': 'default', 'category': 'Transitional Care', 
             'description': intervention_descriptions['Transitional Care']}
        ]
        
        # Add missing interventions
        for intervention in default_interventions:
            if intervention['category'] not in [i['category'] for i in interventions]:
                interventions.append(intervention)
                if len(interventions) >= 3:
                    break
    
    return pd.DataFrame(interventions)

def main():
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.models_dir, exist_ok=True)
    
    # Load patient data with complexity score
    patient_data = load_complexity_data(args.data_dir)
    
    # Define events to predict
    events = define_events(patient_data)
    
    # Build prediction models
    results = build_event_prediction_models(patient_data, events, args.models_dir)
    
    print("Event prediction models completed successfully.")

if __name__ == "__main__":
    main()
