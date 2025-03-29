import os
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_patient_data(data_dir):
    """
    Load patient cohort with clinical and complexity data
    
    Parameters:
    -----------
    data_dir : str
        Path to the processed data directory
    
    Returns:
    --------
    pd.DataFrame
        Dataframe containing patient data
    """
    try:
        # Try loading from models directory first (for complexity data)
        complexity_path = os.path.join(data_dir, '..', 'models', 'patients_with_complexity.csv')
        if os.path.exists(complexity_path):
            return pd.read_csv(complexity_path)
        
        # If not found, try loading from processed_data
        patient_path = os.path.join(data_dir, 'patient_cohort.csv')
        if os.path.exists(patient_path):
            patient_data = pd.read_csv(patient_path)
            
            # Try to merge with conditions data if available
            conditions_path = os.path.join(data_dir, 'patients_with_conditions.csv')
            if os.path.exists(conditions_path):
                conditions_data = pd.read_csv(conditions_path)
                patient_data = patient_data.merge(
                    conditions_data[['subject_id', 'unique_chronic_conditions', 'multiple_chronic_conditions']], 
                    on='subject_id', 
                    how='left'
                )
            
            # Try to merge with medications data if available
            meds_path = os.path.join(data_dir, 'patients_with_medications.csv')
            if os.path.exists(meds_path):
                meds_data = pd.read_csv(meds_path)
                patient_data = patient_data.merge(
                    meds_data[['subject_id', 'unique_medication_count', 'polypharmacy_flag']], 
                    on='subject_id', 
                    how='left'
                )
            
            # Try to merge with clinical data if available
            clinical_path = os.path.join(data_dir, 'patients_with_clinical.csv')
            if os.path.exists(clinical_path):
                clinical_data = pd.read_csv(clinical_path)
                clinical_cols = [col for col in clinical_data.columns if col not in patient_data.columns]
                patient_data = patient_data.merge(
                    clinical_data[['subject_id'] + clinical_cols], 
                    on='subject_id', 
                    how='left'
                )
            
            return patient_data
        
        # If neither found, return None
        return None
    
    except Exception as e:
        st.error(f"Error loading patient data: {str(e)}")
        return None

@st.cache_data
def load_model_results(models_dir):
    """
    Load model results and feature importance
    
    Parameters:
    -----------
    models_dir : str
        Path to the models directory
    
    Returns:
    --------
    dict
        Dictionary containing model results
    """
    results = {}
    
    try:
        # Model summary
        summary_path = os.path.join(models_dir, 'model_summary.csv')
        if os.path.exists(summary_path):
            results['summary'] = pd.read_csv(summary_path)
        
        # Feature importance for readmission model
        feature_importance_path = os.path.join(models_dir, 'feature_importance.csv')
        if os.path.exists(feature_importance_path):
            results['readmission_importance'] = pd.read_csv(feature_importance_path)
        
        # Feature importance for other models
        for model_type in ['readmission', 'mortality', 'high_utilizer', 'emergency_utilizer', 'extended_icu_stay']:
            importance_path = os.path.join(models_dir, f'{model_type}_feature_importance.csv')
            if os.path.exists(importance_path):
                results[f'{model_type}_importance'] = pd.read_csv(importance_path)
            
            # Load intervention recommendations if available
            intervention_path = os.path.join(models_dir, f'{model_type}_interventions.csv')
            if os.path.exists(intervention_path):
                results[f'{model_type}_interventions'] = pd.read_csv(intervention_path)
        
        return results
    
    except Exception as e:
        st.error(f"Error loading model results: {str(e)}")
        return {}

def prepare_filter_options(patient_data):
    """
    Prepare filter options for the dashboard based on available data
    
    Parameters:
    -----------
    patient_data : pd.DataFrame
        Dataframe containing patient data
    
    Returns:
    --------
    dict
        Dictionary containing filter options
    """
    filter_options = {}
    
    if patient_data is None:
        return filter_options
    
    # Age group options
    if 'age_group' in patient_data.columns:
        filter_options['age_groups'] = sorted(patient_data['age_group'].unique())
    
    # Gender options
    if 'gender' in patient_data.columns:
        filter_options['genders'] = sorted(patient_data['gender'].unique())
    
    # Chronic condition options
    chronic_condition_cols = [col for col in patient_data.columns if col in [
        'hypertension', 'diabetes', 'chf', 'copd', 'ckd', 
        'liver_disease', 'cancer', 'depression', 'dementia'
    ]]
    if chronic_condition_cols:
        filter_options['chronic_conditions'] = chronic_condition_cols
    
    # Complexity tier options
    if 'complexity_tier' in patient_data.columns:
        filter_options['complexity_tiers'] = sorted(patient_data['complexity_tier'].unique())
    
    return filter_options

def filter_patient_data(patient_data, filters):
    """
    Filter patient data based on selected filters
    
    Parameters:
    -----------
    patient_data : pd.DataFrame
        Dataframe containing patient data
    filters : dict
        Dictionary containing filter selections
    
    Returns:
    --------
    pd.DataFrame
        Filtered dataframe
    """
    if patient_data is None:
        return None
    
    filtered_data = patient_data.copy()
    
    # Apply age group filter
    if 'age_group' in filters and filters['age_group']:
        filtered_data = filtered_data[filtered_data['age_group'].isin(filters['age_group'])]
    
    # Apply gender filter
    if 'gender' in filters and filters['gender']:
        filtered_data = filtered_data[filtered_data['gender'].isin(filters['gender'])]
    
    # Apply chronic condition filters
    for condition in filters.get('conditions', []):
        if condition in filtered_data.columns:
            filtered_data = filtered_data[filtered_data[condition] == 1]
    
    # Apply complexity tier filter
    if 'complexity_tier' in filters and filters['complexity_tier']:
        filtered_data = filtered_data[filtered_data['complexity_tier'].isin(filters['complexity_tier'])]
    
    # Apply risk threshold filter
    if 'risk_threshold' in filters and 'complexity_score' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['complexity_score'] >= filters['risk_threshold']]
    
    return filtered_data
