#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Process MIMIC-IV clinical data')
    parser.add_argument('--mimic_dir', type=str, required=True, help='Path to MIMIC-IV directory')
    parser.add_argument('--output_dir', type=str, required=True, help='Path to output directory')
    parser.add_argument('--patient_cohort', type=str, required=True, help='Path to patient cohort file')
    parser.add_argument('--chunk_size', type=int, default=100000, help='Chunk size for processing large files')
    return parser.parse_args()

def load_patient_cohort(patient_cohort_path):
    """Load the patient cohort file"""
    print("Loading patient cohort...")
    patients = pd.read_csv(patient_cohort_path)
    return patients

def process_lab_data(mimic_dir, output_dir, patient_cohort, chunk_size=100000):
    """Process laboratory data in chunks"""
    print("Processing laboratory data in chunks...")
    
    lab_path = os.path.join(mimic_dir, 'hosp', 'labevents.csv.gz')
    d_labitems_path = os.path.join(mimic_dir, 'hosp', 'd_labitems.csv.gz')
    
    # Load lab item definitions
    d_labitems = pd.read_csv(d_labitems_path)
    
    # Define lab items of interest (common indicators of severity)
    lab_items_of_interest = {
        # These are examples - you would define specific lab tests based on clinical knowledge
        'creatinine': [50912],  # Kidney function
        'bun': [51006],         # Blood urea nitrogen
        'glucose': [50809, 50931],   # Blood glucose
        'potassium': [50971],   # Electrolyte
        'sodium': [50983],      # Electrolyte
        'wbc': [51301],         # White blood cell count
        'hgb': [51222],         # Hemoglobin
        'platelet': [51265]     # Platelet count
    }
    
    # Flatten the list of item IDs
    item_ids = [item for sublist in lab_items_of_interest.values() for item in sublist]
    
    # Get patient IDs from cohort
    patient_ids = set(patient_cohort['subject_id'].unique())
    
    # Initialize dictionary to store lab results
    patient_labs = {patient_id: {} for patient_id in patient_ids}
    
    # Process the file in chunks
    chunk_iterator = pd.read_csv(lab_path, chunksize=chunk_size)
    
    for i, chunk in enumerate(chunk_iterator):
        print(f"Processing lab chunk {i+1}...")
        
        # Filter for patients in our cohort and items we care about
        chunk = chunk[(chunk['subject_id'].isin(patient_ids)) & (chunk['itemid'].isin(item_ids))]
        
        # Skip if no relevant data in this chunk
        if len(chunk) == 0:
            continue
        
        # Process each lab result
        for _, row in chunk.iterrows():
            subject_id = row['subject_id']
            item_id = row['itemid']
            value = row['valuenum']
            
            # Skip if value is missing
            if pd.isna(value):
                continue
            
            # Identify which lab test this is
            lab_test = None
            for test, ids in lab_items_of_interest.items():
                if item_id in ids:
                    lab_test = test
                    break
            
            if lab_test is None:
                continue
            
            # Add to patient's lab values
            if lab_test not in patient_labs[subject_id]:
                patient_labs[subject_id][lab_test] = []
            
            patient_labs[subject_id][lab_test].append(value)
    
    # Calculate statistics for each patient's lab values
    lab_results = []
    
    for subject_id, labs in patient_labs.items():
        result = {'subject_id': subject_id}
        
        # Calculate statistics for each lab test
        for lab_test, values in labs.items():
            if values:  # If we have values for this test
                result[f'{lab_test}_min'] = min(values)
                result[f'{lab_test}_max'] = max(values)
                result[f'{lab_test}_mean'] = sum(values) / len(values)
                result[f'{lab_test}_count'] = len(values)
        
        lab_results.append(result)
    
    lab_results_df = pd.DataFrame(lab_results)
    
    return lab_results_df

def process_icu_data(mimic_dir, output_dir, patient_cohort):
    """Process ICU data including chart events"""
    print("Processing ICU data...")
    
    # Load ICU stays if not already loaded
    icustays_path = os.path.join(mimic_dir, 'icu', 'icustays.csv.gz')
    icustays = pd.read_csv(icustays_path)
    
    # Get patient IDs from cohort
    patient_ids = set(patient_cohort['subject_id'].unique())
    
    # Filter for patients in our cohort
    icustays = icustays[icustays['subject_id'].isin(patient_ids)]
    
    # Calculate ICU statistics
    icu_stats = icustays.groupby('subject_id').agg(
        icu_count=('stay_id', 'count'),
        max_icu_los=('los', 'max'),
        total_icu_los=('los', 'sum')
    ).reset_index()
    
    # Define severity flags
    icu_stats['extended_icu_stay'] = (icu_stats['max_icu_los'] > 7).astype(int)
    icu_stats['multiple_icu_stays'] = (icu_stats['icu_count'] > 1).astype(int)
    
    return icu_stats

def merge_clinical_data(patient_cohort, lab_results_df, icu_stats):
    """Merge all clinical data with patient cohort"""
    print("Merging clinical data with patient cohort...")
    
    # Merge lab results with patient cohort
    if lab_results_df is not None:
        merged_df = patient_cohort.merge(lab_results_df, on='subject_id', how='left')
    else:
        merged_df = patient_cohort.copy()
    
    # Merge ICU stats
    if icu_stats is not None:
        merged_df = merged_df.merge(icu_stats, on='subject_id', how='left')
    
    # Fill NAs for missing values
    for col in merged_df.columns:
        if col != 'subject_id' and merged_df[col].dtype in [np.float64, np.int64]:
            merged_df[col] = merged_df[col].fillna(0)
    
    # Create clinical severity score (simplified example)
    # In practice, you would use clinical knowledge to create a more sophisticated score
    severity_columns = []
    
    # Add lab abnormality flags
    if 'creatinine_max' in merged_df.columns:
        merged_df['abnormal_creatinine'] = (merged_df['creatinine_max'] > 1.2).astype(int)
        severity_columns.append('abnormal_creatinine')
    
    if 'wbc_max' in merged_df.columns:
        merged_df['abnormal_wbc'] = ((merged_df['wbc_max'] > 11) | (merged_df['wbc_max'] < 4)).astype(int)
        severity_columns.append('abnormal_wbc')
    
    if 'glucose_max' in merged_df.columns:
        merged_df['abnormal_glucose'] = ((merged_df['glucose_max'] > 180) | (merged_df['glucose_max'] < 70)).astype(int)
        severity_columns.append('abnormal_glucose')
    
    # Add ICU severity flags
    if 'extended_icu_stay' in merged_df.columns:
        severity_columns.append('extended_icu_stay')
    
    if 'multiple_icu_stays' in merged_df.columns:
        severity_columns.append('multiple_icu_stays')
    
    # Calculate clinical severity score if we have severity columns
    if severity_columns:
        merged_df['clinical_severity_score'] = merged_df[severity_columns].sum(axis=1)
    else:
        merged_df['clinical_severity_score'] = 0
    
    return merged_df

def main():
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load patient cohort
    patient_cohort = load_patient_cohort(args.patient_cohort)
    
    # Process lab data
    lab_results_df = process_lab_data(
        args.mimic_dir,
        args.output_dir,
        patient_cohort,
        args.chunk_size
    )
    
    # Process ICU data
    icu_stats = process_icu_data(args.mimic_dir, args.output_dir, patient_cohort)
    
    # Merge all clinical data
    patients_with_clinical = merge_clinical_data(patient_cohort, lab_results_df, icu_stats)
    
    # Save results
    clinical_path = os.path.join(args.output_dir, 'patients_with_clinical.csv')
    patients_with_clinical.to_csv(clinical_path, index=False)
    print(f"Patients with clinical data saved to {clinical_path}")

if __name__ == "__main__":
    main()
