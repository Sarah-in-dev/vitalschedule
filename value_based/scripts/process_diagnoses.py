#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Process MIMIC-IV diagnoses data')
    parser.add_argument('--mimic_dir', type=str, required=True, help='Path to MIMIC-IV directory')
    parser.add_argument('--output_dir', type=str, required=True, help='Path to output directory')
    parser.add_argument('--patient_cohort', type=str, required=True, help='Path to patient cohort file')
    return parser.parse_args()

def load_diagnoses(mimic_dir):
    """Load diagnoses and ICD code mappings"""
    print("Loading diagnoses data...")
    diagnoses_path = os.path.join(mimic_dir, 'hosp', 'diagnoses_icd.csv.gz')
    diagnoses = pd.read_csv(diagnoses_path)
    
    # Load ICD code descriptions
    icd_path = os.path.join(mimic_dir, 'hosp', 'd_icd_diagnoses.csv.gz')
    icd_codes = pd.read_csv(icd_path)
    
    return diagnoses, icd_codes

# Define chronic conditions based on ICD-9 and ICD-10 codes
# This is a simplified list - in practice, you'd want a more comprehensive mapping
CHRONIC_CONDITIONS = {
    'hypertension': {
        'icd9': ['401', '402', '403', '404', '405'],
        'icd10': ['I10', 'I11', 'I12', 'I13', 'I15']
    },
    'diabetes': {
        'icd9': ['250'],
        'icd10': ['E08', 'E09', 'E10', 'E11', 'E13']
    },
    'chf': {  # Congestive Heart Failure
        'icd9': ['428'],
        'icd10': ['I50']
    },
    'copd': {  # Chronic Obstructive Pulmonary Disease
        'icd9': ['490', '491', '492', '493', '494', '495', '496'],
        'icd10': ['J40', 'J41', 'J42', 'J43', 'J44', 'J45', 'J46', 'J47']
    },
    'ckd': {  # Chronic Kidney Disease
        'icd9': ['585'],
        'icd10': ['N18']
    },
    'liver_disease': {
        'icd9': ['571'],
        'icd10': ['K70', 'K71', 'K72', 'K73', 'K74', 'K76']
    },
    'cancer': {
        'icd9': ['140', '141', '142', '143', '144', '145', '146', '147', '148', '149',
                 '150', '151', '152', '153', '154', '155', '156', '157', '158', '159',
                 '160', '161', '162', '163', '164', '165', '166', '167', '168', '169',
                 '170', '171', '172', '173', '174', '175', '176', '177', '178', '179',
                 '180', '181', '182', '183', '184', '185', '186', '187', '188', '189',
                 '190', '191', '192', '193', '194', '195', '196', '197', '198', '199',
                 '200', '201', '202', '203', '204', '205', '206', '207', '208', '209'],
        'icd10': ['C']  # All codes starting with C
    },
    'depression': {
        'icd9': ['296.2', '296.3', '300.4', '311'],
        'icd10': ['F32', 'F33']
    },
    'dementia': {
        'icd9': ['290', '291.2', '294.1', '294.2', '331.0'],
        'icd10': ['F01', 'F02', 'F03', 'G30']
    }
}

def identify_chronic_conditions(diagnoses, icd_codes=None):
    """Identify chronic conditions from diagnosis codes"""
    print("Identifying chronic conditions...")
    
    # Prepare the diagnoses dataframe
    diagnoses_df = diagnoses.copy()
    
    # Initialize condition columns
    for condition in CHRONIC_CONDITIONS.keys():
        diagnoses_df[condition] = 0
    
    # Check for each chronic condition
    for condition, codes in CHRONIC_CONDITIONS.items():
        # Check ICD-9 codes
        if 'icd9' in codes and len(codes['icd9']) > 0:
            icd9_mask = (diagnoses_df['icd_version'] == 9) & (diagnoses_df['icd_code'].str.startswith(tuple(codes['icd9']), na=False))
            diagnoses_df.loc[icd9_mask, condition] = 1
        
        # Check ICD-10 codes
        if 'icd10' in codes and len(codes['icd10']) > 0:
            icd10_mask = (diagnoses_df['icd_version'] == 10) & (diagnoses_df['icd_code'].str.startswith(tuple(codes['icd10']), na=False))
            diagnoses_df.loc[icd10_mask, condition] = 1
    
    # Add a count of total chronic conditions
    diagnoses_df['chronic_condition_count'] = diagnoses_df[list(CHRONIC_CONDITIONS.keys())].sum(axis=1)
    
    return diagnoses_df

def aggregate_patient_conditions(diagnoses_with_conditions, patient_cohort):
    """Aggregate conditions to patient level"""
    print("Aggregating conditions to patient level...")
    
    # Get unique patients
    patients = pd.read_csv(patient_cohort)
    
    # Group by patient and get maximum value for each condition (1 if any diagnosis has the condition)
    condition_cols = list(CHRONIC_CONDITIONS.keys()) + ['chronic_condition_count']
    patient_conditions = diagnoses_with_conditions.groupby('subject_id')[condition_cols].max().reset_index()
    
    # Count unique conditions per patient
    patient_conditions['unique_chronic_conditions'] = patient_conditions[list(CHRONIC_CONDITIONS.keys())].sum(axis=1)
    
    # Merge with patient cohort
    patients_with_conditions = patients.merge(patient_conditions, on='subject_id', how='left')
    
    # Fill NAs for patients with no diagnoses
    for col in condition_cols + ['unique_chronic_conditions']:
        patients_with_conditions[col] = patients_with_conditions[col].fillna(0)
    
    # Flag for multiple chronic conditions (2+)
    patients_with_conditions['multiple_chronic_conditions'] = (patients_with_conditions['unique_chronic_conditions'] >= 2).astype(int)
    
    return patients_with_conditions

def main():
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load diagnoses data
    diagnoses, icd_codes = load_diagnoses(args.mimic_dir)
    
    # Identify chronic conditions
    diagnoses_with_conditions = identify_chronic_conditions(diagnoses, icd_codes)
    
    # Save processed diagnoses
    diagnoses_output_path = os.path.join(args.output_dir, 'diagnoses_with_conditions.csv')
    diagnoses_with_conditions.to_csv(diagnoses_output_path, index=False)
    print(f"Diagnoses with conditions saved to {diagnoses_output_path}")
    
    # Aggregate to patient level
    patients_with_conditions = aggregate_patient_conditions(diagnoses_with_conditions, args.patient_cohort)
    
    # Save patient with conditions
    patients_output_path = os.path.join(args.output_dir, 'patients_with_conditions.csv')
    patients_with_conditions.to_csv(patients_output_path, index=False)
    print(f"Patients with conditions saved to {patients_output_path}")

if __name__ == "__main__":
    main()
