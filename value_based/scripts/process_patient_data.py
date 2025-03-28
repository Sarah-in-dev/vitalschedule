#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import argparse
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='Process MIMIC-IV patient data')
    parser.add_argument('--mimic_dir', type=str, required=True, help='Path to MIMIC-IV directory')
    parser.add_argument('--output_dir', type=str, required=True, help='Path to output directory')
    parser.add_argument('--tables', nargs='+', default=['patients', 'admissions', 'icustays'], 
                        help='Tables to process')
    return parser.parse_args()

def load_patients(mimic_dir):
    """Load and process patients table"""
    print("Loading patients data...")
    patients_path = os.path.join(mimic_dir, 'hosp', 'patients.csv.gz')
    patients = pd.read_csv(patients_path)
    
    # Process dates
    patients['dod'] = pd.to_datetime(patients['dod'], errors='coerce')
    
    # Create age categories
    age_bins = [0, 18, 35, 50, 65, 80, 200]
    age_labels = ['0-18', '19-35', '36-50', '51-65', '66-80', '80+']
    patients['age_group'] = pd.cut(patients['anchor_age'], bins=age_bins, labels=age_labels)
    
    print(f"Processed {len(patients)} patients")
    return patients

def load_admissions(mimic_dir):
    """Load and process admissions table"""
    print("Loading admissions data...")
    admissions_path = os.path.join(mimic_dir, 'hosp', 'admissions.csv.gz')
    admissions = pd.read_csv(admissions_path)
    
    # Process dates
    date_columns = ['admittime', 'dischtime', 'deathtime', 'edregtime', 'edouttime']
    for col in date_columns:
        admissions[col] = pd.to_datetime(admissions[col], errors='coerce')
    
    # Calculate length of stay
    admissions['los_days'] = (admissions['dischtime'] - admissions['admittime']).dt.total_seconds() / (24 * 3600)
    
    # Process admission types and locations
    admissions['is_emergency'] = admissions['admission_type'].str.contains('EMER', case=False, na=False).astype(int)
    
    print(f"Processed {len(admissions)} admissions")
    return admissions

def load_icustays(mimic_dir):
    """Load and process ICU stays table"""
    print("Loading ICU stays data...")
    icustays_path = os.path.join(mimic_dir, 'icu', 'icustays.csv.gz')
    icustays = pd.read_csv(icustays_path)
    
    # Process dates
    icustays['intime'] = pd.to_datetime(icustays['intime'], errors='coerce')
    icustays['outtime'] = pd.to_datetime(icustays['outtime'], errors='coerce')
    
    print(f"Processed {len(icustays)} ICU stays")
    return icustays

def load_services(mimic_dir):
    """Load and process services table"""
    print("Loading services data...")
    services_path = os.path.join(mimic_dir, 'hosp', 'services.csv.gz')
    services = pd.read_csv(services_path)
    
    # Process dates
    services['transfertime'] = pd.to_datetime(services['transfertime'], errors='coerce')
    
    print(f"Processed {len(services)} service records")
    return services

def process_patient_cohort(patients, admissions, icustays=None, services=None):
    """Process data to create a patient cohort with utilization metrics"""
    print("Creating patient cohort with utilization metrics...")
    
    # Count admissions per patient
    admission_counts = admissions.groupby('subject_id').size().reset_index(name='admission_count')
    
    # Count ICU stays per patient
    if icustays is not None:
        icu_counts = icustays.groupby('subject_id').size().reset_index(name='icu_stay_count')
        
        # Calculate average ICU LOS
        icu_los = icustays.groupby('subject_id')['los'].mean().reset_index(name='avg_icu_los')
    else:
        icu_counts = pd.DataFrame({'subject_id': patients['subject_id'].unique(), 'icu_stay_count': 0})
        icu_los = pd.DataFrame({'subject_id': patients['subject_id'].unique(), 'avg_icu_los': 0})
    
    # Calculate average length of stay
    los_avg = admissions.groupby('subject_id')['los_days'].mean().reset_index(name='avg_los_days')
    
    # Count emergency visits
    emergency_counts = admissions.groupby('subject_id')['is_emergency'].sum().reset_index(name='emergency_count')
    
    # Count unique services per patient (if available)
    if services is not None:
        service_counts = services.groupby('subject_id')['curr_service'].nunique().reset_index(name='unique_services')
    else:
        service_counts = pd.DataFrame({'subject_id': patients['subject_id'].unique(), 'unique_services': 0})
    
    # Merge all patient metrics
    patient_cohort = patients[['subject_id', 'gender', 'anchor_age', 'age_group', 'dod']]
    patient_cohort = patient_cohort.merge(admission_counts, on='subject_id', how='left')
    patient_cohort = patient_cohort.merge(icu_counts, on='subject_id', how='left')
    patient_cohort = patient_cohort.merge(icu_los, on='subject_id', how='left')
    patient_cohort = patient_cohort.merge(los_avg, on='subject_id', how='left')
    patient_cohort = patient_cohort.merge(emergency_counts, on='subject_id', how='left')
    patient_cohort = patient_cohort.merge(service_counts, on='subject_id', how='left')
    
    # Fill NA values
    patient_cohort = patient_cohort.fillna({
        'admission_count': 0,
        'icu_stay_count': 0,
        'avg_icu_los': 0,
        'avg_los_days': 0,
        'emergency_count': 0,
        'unique_services': 0
    })
    
    # Calculate mortality flag
    patient_cohort['mortality_flag'] = (~patient_cohort['dod'].isna()).astype(int)
    
    print(f"Created patient cohort with {len(patient_cohort)} patients")
    return patient_cohort

def main():
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load tables based on arguments
    tables = {}
    for table in args.tables:
        if table == 'patients':
            tables['patients'] = load_patients(args.mimic_dir)
        elif table == 'admissions':
            tables['admissions'] = load_admissions(args.mimic_dir)
        elif table == 'icustays':
            tables['icustays'] = load_icustays(args.mimic_dir)
        elif table == 'services':
            tables['services'] = load_services(args.mimic_dir)
    
    # Process patient cohort
    if 'patients' in tables and 'admissions' in tables:
        patient_cohort = process_patient_cohort(
            tables['patients'], 
            tables['admissions'],
            tables.get('icustays'),
            tables.get('services')
        )
        
        # Save patient cohort
        output_path = os.path.join(args.output_dir, 'patient_cohort.csv')
        patient_cohort.to_csv(output_path, index=False)
        print(f"Patient cohort saved to {output_path}")
        
        # Save tables for later use
        for name, table in tables.items():
            output_path = os.path.join(args.output_dir, f'{name}_processed.csv')
            table.to_csv(output_path, index=False)
            print(f"Processed {name} saved to {output_path}")
    else:
        print("Error: Both patients and admissions tables are required.")

if __name__ == "__main__":
    main()
