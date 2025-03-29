#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Process MIMIC-IV medication data')
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

def process_prescriptions_in_chunks(mimic_dir, output_dir, patient_cohort, chunk_size=100000):
    """Process prescriptions file in chunks due to size"""
    print("Processing prescriptions data in chunks...")
    
    prescriptions_path = os.path.join(mimic_dir, 'hosp', 'prescriptions.csv.gz')
    patient_ids = set(patient_cohort['subject_id'].unique())
    
    # Initialize a dictionary to store medication counts by patient
    patient_med_counts = {}
    unique_medications = set()
    
    # Process the file in chunks
    chunk_iterator = pd.read_csv(prescriptions_path, chunksize=chunk_size,low_memory=False)
    
    for i, chunk in enumerate(chunk_iterator):
        print(f"Processing chunk {i+1}...")

# Convert problematic columns to string to avoid mixed type issues
        if 'drug' in chunk.columns:
            chunk['drug'] = chunk['drug'].astype(str)
        
        # Filter for patients in our cohort
        chunk = chunk[chunk['subject_id'].isin(patient_ids)]

# Skip if no relevant data in this chunk
        if len(chunk) == 0:
            continue
        
        # Count medications per patient
        for _, row in chunk.iterrows():
            subject_id = row['subject_id']
            drug = row['drug']
            
            if subject_id not in patient_med_counts:
                patient_med_counts[subject_id] = set()
            
            patient_med_counts[subject_id].add(drug)
            unique_medications.add(drug)
    
    # Convert to DataFrame
    print("Converting medication data to DataFrame...")
    med_counts = []
    
    for subject_id, medications in patient_med_counts.items():
        med_counts.append({
            'subject_id': subject_id,
            'unique_medication_count': len(medications),
            'polypharmacy_flag': 1 if len(medications) >= 5 else 0
        })
    
    med_counts_df = pd.DataFrame(med_counts)
    
    # Save unique medications list
    unique_meds_df = pd.DataFrame(list(unique_medications), columns=['medication'])
    unique_meds_path = os.path.join(output_dir, 'unique_medications.csv')
    unique_meds_df.to_csv(unique_meds_path, index=False)
    
    return med_counts_df

def merge_with_patient_cohort(patient_cohort, med_counts_df):
    """Merge medication data with patient cohort"""
    print("Merging medication data with patient cohort...")
    
    # Merge with patient cohort
    merged_df = patient_cohort.merge(med_counts_df, on='subject_id', how='left')
    
    # Fill NAs for patients with no medications
    merged_df['unique_medication_count'] = merged_df['unique_medication_count'].fillna(0)
    merged_df['polypharmacy_flag'] = merged_df['polypharmacy_flag'].fillna(0)
    
    return merged_df

def main():
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load patient cohort
    patient_cohort = load_patient_cohort(args.patient_cohort)
    
    # Process prescriptions data
    med_counts_df = process_prescriptions_in_chunks(
        args.mimic_dir, 
        args.output_dir, 
        patient_cohort,
        args.chunk_size
    )
    
    # Save medication counts
    med_counts_path = os.path.join(args.output_dir, 'medication_counts.csv')
    med_counts_df.to_csv(med_counts_path, index=False)
    print(f"Medication counts saved to {med_counts_path}")
    
    # Merge with patient cohort
    patients_with_meds = merge_with_patient_cohort(patient_cohort, med_counts_df)
    
    # Save patient data with medication info
    output_path = os.path.join(args.output_dir, 'patients_with_medications.csv')
    patients_with_meds.to_csv(output_path, index=False)
    print(f"Patients with medication data saved to {output_path}")

if __name__ == "__main__":
    main()
