#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import argparse
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, confusion_matrix

def parse_args():
    parser = argparse.ArgumentParser(description='Build patient complexity model')
    parser.add_argument('--data_dir', type=str, required=True, help='Path to processed data directory')
    parser.add_argument('--output_dir', type=str, required=True, help='Path to output directory')
    return parser.parse_args()

def load_patient_data(data_dir):
    """Load all patient data files and merge them"""
    print("Loading patient data files...")
    
    # Load patient cohort with clinical data
    clinical_path = os.path.join(data_dir, 'patients_with_clinical.csv')
    patient_clinical = pd.read_csv(clinical_path)
    
    # Load patient cohort with conditions
    conditions_path = os.path.join(data_dir, 'patients_with_conditions.csv')
    patient_conditions = pd.read_csv(conditions_path)
    
    # Load patient cohort with medications
    medications_path = os.path.join(data_dir, 'patients_with_medications.csv')
    patient_medications = pd.read_csv(medications_path)
    
    # Merge all data
    merged_df = patient_clinical.merge(
        patient_conditions[['subject_id', 'unique_chronic_conditions', 'multiple_chronic_conditions']], 
        on='subject_id', 
        how='left'
    )
    
    merged_df = merged_df.merge(
        patient_medications[['subject_id', 'unique_medication_count', 'polypharmacy_flag']], 
        on='subject_id', 
        how='left'
    )
    
    # Fill missing values
    cols_to_fill = ['unique_chronic_conditions', 'multiple_chronic_conditions', 
                    'unique_medication_count', 'polypharmacy_flag']
    
    for col in cols_to_fill:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(0)
    
    return merged_df

def create_complexity_score(patient_data):
    """Create a complexity score based on multiple dimensions"""
    print("Creating patient complexity score...")
    
    # Define complexity dimensions
    complexity_dimensions = {
        'chronic_condition': ['unique_chronic_conditions', 'multiple_chronic_conditions'],
        'utilization': ['admission_count', 'icu_stay_count', 'emergency_count'],
        'medications': ['unique_medication_count', 'polypharmacy_flag'],
        'clinical': ['clinical_severity_score']
    }
    
    # Calculate dimension scores
    for dimension, features in complexity_dimensions.items():
        valid_features = [f for f in features if f in patient_data.columns]
        
        if valid_features:
            # Normalize each feature to 0-1 scale
            scaler = StandardScaler()
            
            # Get only numeric columns
            numeric_features = [f for f in valid_features if patient_data[f].dtype in [np.float64, np.int64]]
            
            if numeric_features:
                patient_data[f'{dimension}_score'] = patient_data[numeric_features].sum(axis=1)
                
                # Scale the dimension score
                patient_data[f'{dimension}_score_scaled'] = scaler.fit_transform(
                    patient_data[[f'{dimension}_score']]
                )
    
    # Create overall complexity score (average of dimension scores)
    dimension_score_cols = [f'{dim}_score_scaled' for dim in complexity_dimensions.keys() 
                           if f'{dim}_score_scaled' in patient_data.columns]
    
    if dimension_score_cols:
        patient_data['complexity_score'] = patient_data[dimension_score_cols].mean(axis=1)
        
        # Create complexity tiers
        patient_data['complexity_tier'] = pd.qcut(
            patient_data['complexity_score'], 
            q=[0, 0.5, 0.85, 1.0], 
            labels=['Low', 'Medium', 'High']
        )
    
    return patient_data

def build_readmission_model(patient_data):
    """Build a model to predict readmissions"""
    print("Building readmission prediction model...")
    
    # Define readmission flag based on multiple admissions
    patient_data['readmission_flag'] = (patient_data['admission_count'] > 1).astype(int)
    
    # Define features for the model
    features = [
        'unique_chronic_conditions', 'multiple_chronic_conditions',
        'unique_medication_count', 'polypharmacy_flag',
        'admission_count', 'icu_stay_count', 'emergency_count',
        'clinical_severity_score', 'complexity_score'
    ]
    
    # Filter to valid features that exist in the dataset
    valid_features = [f for f in features if f in patient_data.columns]
    
    # Split data
    X = patient_data[valid_features]
    y = patient_data['readmission_flag']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    pr_auc = auc(recall, precision)
    
    print(f"Readmission Model ROC-AUC: {roc_auc:.3f}")
    print(f"Readmission Model PR-AUC: {pr_auc:.3f}")
    
    # Get feature importance
    feature_importance = pd.DataFrame({
        'feature': valid_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return model, feature_importance, roc_auc, pr_auc

def main():
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load patient data
    patient_data = load_patient_data(args.data_dir)
    
    # Create complexity score
    patient_data = create_complexity_score(patient_data)
    
    # Save patient data with complexity score
    complexity_path = os.path.join(args.output_dir, 'patients_with_complexity.csv')
    patient_data.to_csv(complexity_path, index=False)
    print(f"Patients with complexity score saved to {complexity_path}")
    
    # Build readmission model
    readmission_model, feature_importance, roc_auc, pr_auc = build_readmission_model(patient_data)
    
    # Save model
    model_path = os.path.join(args.output_dir, 'readmission_model.joblib')
    joblib.dump(readmission_model, model_path)
    print(f"Readmission model saved to {model_path}")
    
    # Save feature importance
    importance_path = os.path.join(args.output_dir, 'feature_importance.csv')
    feature_importance.to_csv(importance_path, index=False)
    print(f"Feature importance saved to {importance_path}")
    
    # Save model metrics
    metrics = {
        'roc_auc': roc_auc,
        'pr_auc': pr_auc
    }
    
    metrics_path = os.path.join(args.output_dir, 'model_metrics.csv')
    pd.DataFrame([metrics]).to_csv(metrics_path, index=False)
    print(f"Model metrics saved to {metrics_path}")

if __name__ == "__main__":
    main()
