# code/readmission/data_processing.py
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_mimic_tables(mimic_dir):
    """
    Load the necessary MIMIC-IV tables for readmission prediction
    
    Parameters:
    -----------
    mimic_dir : str
        Path to the MIMIC-IV dataset directory
        
    Returns:
    --------
    dict
        Dictionary of pandas DataFrames containing the loaded tables
    """
    print(f"Loading MIMIC-IV tables from {mimic_dir}...")
    
    # Define paths to key files
    hosp_dir = os.path.join(mimic_dir, 'hosp')
    icu_dir = os.path.join(mimic_dir, 'icu')
    
    # Load core tables
    tables = {}
    
    # Patient demographics
    print("Loading patients table...")
    tables['patients'] = pd.read_csv(os.path.join(hosp_dir, 'patients.csv.gz'))
    
    # Admissions data
    print("Loading admissions table...")
    tables['admissions'] = pd.read_csv(os.path.join(hosp_dir, 'admissions.csv.gz'))
    
    # Convert date columns to datetime
    date_cols = ['admittime', 'dischtime', 'deathtime', 'edregtime', 'edouttime']
    for col in date_cols:
        if col in tables['admissions'].columns:
            tables['admissions'][col] = pd.to_datetime(tables['admissions'][col])
    
    # Load diagnoses
    print("Loading diagnoses table...")
    tables['diagnoses'] = pd.read_csv(os.path.join(hosp_dir, 'diagnoses_icd.csv.gz'))
    
    # Load procedures
    print("Loading procedures table...")
    tables['procedures'] = pd.read_csv(os.path.join(hosp_dir, 'procedures_icd.csv.gz'))
    
    # Load hospital services
    print("Loading services table...")
    tables['services'] = pd.read_csv(os.path.join(hosp_dir, 'services.csv.gz'))
    
    # Load transfers (ward movements)
    print("Loading transfers table...")
    tables['transfers'] = pd.read_csv(os.path.join(hosp_dir, 'transfers.csv.gz'))
    
    # Convert transfer date columns
    if 'transfers' in tables:
        for col in ['intime', 'outtime']:
            if col in tables['transfers'].columns:
                tables['transfers'][col] = pd.to_datetime(tables['transfers'][col])
    
    # Load lab results
    try:
        print("Loading lab events table (sample)...")
        # Load just a sample of lab events as the full table is very large
        tables['labevents'] = pd.read_csv(os.path.join(hosp_dir, 'labevents.csv.gz'), nrows=100000)
    except Exception as e:
        print(f"Warning: Could not load lab events: {e}")
    
    print("Tables loaded successfully.")
    return tables

def create_readmission_dataset(tables, readmission_window=30):
    """
    Create a dataset identifying index admissions and readmissions
    
    Parameters:
    -----------
    tables : dict
        Dictionary of pandas DataFrames containing MIMIC-IV tables
    readmission_window : int
        Number of days to consider for readmission (default: 30)
        
    Returns:
    --------
    pandas.DataFrame
        Dataset with readmission outcome and key features
    """
    print(f"Creating readmission dataset with {readmission_window}-day window...")
    
    # Get admissions table
    admissions = tables['admissions'].copy()
    patients = tables['patients'].copy()
    
    # Sort admissions by patient and time
    admissions = admissions.sort_values(['subject_id', 'admittime'])
    
    # For each patient, find the next admission time
    admissions['next_admittime'] = admissions.groupby('subject_id')['admittime'].shift(-1)
    
    # Calculate days until next admission
    admissions['days_to_readmission'] = (admissions['next_admittime'] - admissions['dischtime']).dt.total_seconds() / (24 * 3600)
    
    # Flag readmissions within the specified window
    admissions['is_readmission'] = (admissions['days_to_readmission'] <= readmission_window) & (admissions['days_to_readmission'] > 0)
    
    # Exclude patients who died during the index admission
    admissions = admissions[admissions['hospital_expire_flag'] != 1]
    
    # Merge with patient demographics
    dataset = admissions.merge(patients[['subject_id', 'gender', 'anchor_age']], on='subject_id')
    
    # Calculate length of stay
    dataset['length_of_stay'] = (dataset['dischtime'] - dataset['admittime']).dt.total_seconds() / (24 * 3600)
    
    # Add admission type and discharge location
    dataset['emergency'] = (dataset['admission_type'] == 'emergency').astype(int)
    
    # Add service information if available
    if 'services' in tables:
        # Get the first service for each admission (usually the main service)
        services = tables['services'].sort_values(['subject_id', 'hadm_id', 'transfertime'])
        first_service = services.drop_duplicates(['subject_id', 'hadm_id'], keep='first')
        
        # Merge with dataset
        dataset = dataset.merge(
            first_service[['subject_id', 'hadm_id', 'curr_service']], 
            on=['subject_id', 'hadm_id'], 
            how='left'
        )
    
    # Add diagnosis information
    if 'diagnoses' in tables:
        # Get primary diagnoses
        diagnoses = tables['diagnoses']
        primary_dx = diagnoses[diagnoses['seq_num'] == 1]
        
        # Merge with dataset
        dataset = dataset.merge(
            primary_dx[['subject_id', 'hadm_id', 'icd_code', 'icd_version']], 
            on=['subject_id', 'hadm_id'], 
            how='left'
        )
    
    # Calculate number of previous admissions
    admissions_count = admissions.groupby('subject_id').cumcount()
    admissions = admissions.copy()
    admissions['prev_admissions_count'] = admissions_count
    dataset = dataset.merge(admissions[['subject_id', 'hadm_id', 'prev_admissions_count']], 
                           on=['subject_id', 'hadm_id'], how='left')
    
    print(f"Dataset created with {len(dataset)} admissions.")
    print(f"Overall readmission rate: {dataset['is_readmission'].mean():.2%}")
    
    return dataset

def get_common_diagnoses(tables, n=20):
    """Extract the most common diagnoses from the dataset"""
    if 'diagnoses' not in tables:
        print("Diagnoses table not available")
        return None
    
    diagnoses = tables['diagnoses']
    
    # Count occurrences of each diagnosis code
    dx_counts = diagnoses['icd_code'].value_counts().reset_index()
    dx_counts.columns = ['icd_code', 'count']
    
    return dx_counts.head(n)

def get_common_procedures(tables, n=20):
    """Extract the most common procedures from the dataset"""
    if 'procedures' not in tables:
        print("Procedures table not available")
        return None
    
    procedures = tables['procedures']
    
    # Count occurrences of each procedure code
    proc_counts = procedures['icd_code'].value_counts().reset_index()
    proc_counts.columns = ['icd_code', 'count']
    
    return proc_counts.head(n)

def save_processed_data(dataset, output_dir, filename='readmission_data.csv'):
    """
    Save the processed dataset to disk
    
    Parameters:
    -----------
    dataset : pandas.DataFrame
        Processed dataset to save
    output_dir : str
        Directory to save the dataset
    filename : str
        Name of the output file
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    # Save to CSV
    dataset.to_csv(output_path, index=False)
    print(f"Dataset saved to {output_path}")
    
    # Save a smaller sample for exploration
    sample = dataset.sample(min(5000, len(dataset)))
    sample_path = os.path.join(output_dir, f"sample_{filename}")
    sample.to_csv(sample_path, index=False)
    print(f"Sample dataset saved to {sample_path}")
    
    # Save summary statistics
    summary = dataset.describe(include='all')
    summary_path = os.path.join(output_dir, "summary_statistics.csv")
    summary.to_csv(summary_path)
    print(f"Summary statistics saved to {summary_path}")

if __name__ == "__main__":
    # Example usage
    mimic_dir = os.path.join(os.getcwd(), 'data', 'raw', 'mimic-iv')
    output_dir = os.path.join(os.getcwd(), 'data', 'processed', 'readmission')
    
    tables = load_mimic_tables(mimic_dir)
    dataset = create_readmission_dataset(tables)
    save_processed_data(dataset, output_dir)
    
    # Print some common diagnoses and procedures
    common_dx = get_common_diagnoses(tables)
    if common_dx is not None:
        print("\nMost common diagnoses:")
        print(common_dx)
    
    common_proc = get_common_procedures(tables)
    if common_proc is not None:
        print("\nMost common procedures:")
        print(common_proc)
