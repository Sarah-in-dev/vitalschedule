# explore_vbc_data.py
import os
import pandas as pd
import numpy as np
import sys

def explore_table(file_path, sample_size=1000):
    """Explore a MIMIC-IV table and print summary information"""
    table_name = os.path.basename(file_path)
    print(f"\n{'='*50}")
    print(f"Exploring {table_name}:")
    print(f"{'='*50}")
    
    try:
        # Load a sample of the data
        df = pd.read_csv(file_path, compression='gzip', nrows=sample_size)
        
        # Print basic info
        print(f"Columns: {df.columns.tolist()}")
        print(f"Sample size: {len(df)} rows")
        print(f"Memory usage: {df.memory_usage().sum() / 1024 / 1024:.2f} MB")
        
        # Print column types and null counts
        print("\nColumn info:")
        for col in df.columns:
            print(f"  {col}: {df[col].dtype}, {df[col].isna().sum()} nulls")
            
            # For categorical columns, show value distribution
            if df[col].dtype == 'object' and df[col].nunique() < 20:
                print(f"    Values: {df[col].value_counts().head(5).to_dict()}")
        
        # Print a few sample rows for context
        print("\nSample data (first 2 rows):")
        print(df.head(2))
        
    except Exception as e:
        print(f"Error exploring {file_path}: {str(e)}")

def main():
    mimic_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Define tables relevant to complex patient identification in value-based care
    complexity_dimensions = {
        "Demographics": ["hosp/patients.csv.gz"],
        "Chronic Conditions": ["hosp/diagnoses_icd.csv.gz", "hosp/d_icd_diagnoses.csv.gz"],
        "Medications": ["hosp/prescriptions.csv.gz", "hosp/pharmacy.csv.gz"],
        "Healthcare Utilization": ["hosp/admissions.csv.gz", "hosp/transfers.csv.gz"],
        "Care Coordination": ["hosp/services.csv.gz", "hosp/provider.csv.gz"],
        "Procedures": ["hosp/procedures_icd.csv.gz"],
        "Lab Results": ["hosp/labevents.csv.gz", "hosp/d_labitems.csv.gz"],
        "ICU Data": ["icu/icustays.csv.gz", "icu/chartevents.csv.gz", "icu/outputevents.csv.gz"]
    }
    
    # Tables that are too large for full exploration
    large_tables = [
        "hosp/labevents.csv.gz", 
        "hosp/prescriptions.csv.gz", 
        "hosp/pharmacy.csv.gz",
        "icu/chartevents.csv.gz",
        "icu/outputevents.csv.gz"
    ]
    
    # Explore tables by complexity dimension
    for dimension, tables in complexity_dimensions.items():
        print(f"\n\n{'#'*80}")
        print(f"# DIMENSION: {dimension}")
        print(f"{'#'*80}")
        
        for table in tables:
            file_path = os.path.join(mimic_dir, table)
            
            # Use smaller sample size for large tables
            if table in large_tables:
                explore_table(file_path, sample_size=100)
            else:
                explore_table(file_path)
    
if __name__ == "__main__":
    main()
