import os
import sys
import pandas as pd

# Get the current directory and set up paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)

# Add the project root to the path
sys.path.insert(0, project_root)

# Import directly from local file (assumes data_processing.py is in same directory)
from data_processing import load_mimic_tables, create_readmission_dataset

def test_data_loading():
    """Test loading a small subset of the MIMIC-IV data"""
    print("Testing MIMIC-IV data loading...")
    
    mimic_dir = os.path.join(project_root, 'data', 'raw', 'mimic-iv')
    
    # Check if the directory exists
    if not os.path.exists(mimic_dir):
        print(f"Error: MIMIC-IV directory not found at {mimic_dir}")
        print("Please download the dataset first using scripts/download_mimic.sh")
        return False
    
    try:
        # Try loading just the patients table first
        print("Loading patients table for testing...")
        patients_path = os.path.join(mimic_dir, 'hosp', 'patients.csv.gz')
        if not os.path.exists(patients_path):
            print(f"Error: File not found: {patients_path}")
            return False
            
        patients = pd.read_csv(patients_path, nrows=100)  # Just load 100 rows for testing
        
        print(f"Successfully loaded patients table sample with {len(patients)} rows")
        print(f"Columns: {patients.columns.tolist()}")
        
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def test_readmission_processing():
    """Test the readmission dataset creation with a small subset"""
    print("\nTesting readmission dataset creation...")
    
    mimic_dir = os.path.join(project_root, 'data', 'raw', 'mimic-iv')
    
    try:
        # Load just enough data for testing
        tables = {}
        
        # Load a sample of patients
        patients_path = os.path.join(mimic_dir, 'hosp', 'patients.csv.gz')
        tables['patients'] = pd.read_csv(patients_path, nrows=1000)
        
        # Load a sample of admissions for these patients
        admissions_path = os.path.join(mimic_dir, 'hosp', 'admissions.csv.gz')
        all_admissions = pd.read_csv(admissions_path)
        
        # Filter admissions for the patients we loaded
        patient_ids = tables['patients']['subject_id'].tolist()
        tables['admissions'] = all_admissions[all_admissions['subject_id'].isin(patient_ids)]
        
        # Convert datetime columns
        date_cols = ['admittime', 'dischtime', 'deathtime', 'edregtime', 'edouttime']
        for col in date_cols:
            if col in tables['admissions'].columns:
                tables['admissions'][col] = pd.to_datetime(tables['admissions'][col])
        
        # Create a mini readmission dataset
        readmission_data = create_readmission_dataset(tables)
        
        print(f"Created test readmission dataset with {len(readmission_data)} rows")
        print(f"Readmission rate in sample: {readmission_data['is_readmission'].mean():.2%}")
        
        return True
    except Exception as e:
        print(f"Error processing readmission data: {e}")
        return False

if __name__ == "__main__":
    # Run the tests
    print(f"Project root: {project_root}")
    data_loaded = test_data_loading()
    
    if data_loaded:
        test_readmission_processing()
    else:
        print("Skipping readmission processing test as data loading failed")
