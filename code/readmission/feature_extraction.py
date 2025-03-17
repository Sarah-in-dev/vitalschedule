# code/readmission/feature_extraction.py
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Dictionary of ICD-9 codes for Elixhauser comorbidities
# This is a simplified version - in practice, you'd want a more comprehensive mapping
ELIXHAUSER_ICD9 = {
    'CHF': ['39891', '4280', '4281', '42820', '42821', '42822', '42823', '42830', '42831', '42832', '42833', '42840', '42841', '42842', '42843', '4289'],
    'Arrhythmia': ['4260', '42610', '42611', '42612', '42613', '4262', '4263', '4264', '42650', '42651', '42652', '42653', '42654', '4266', '4267', '4268', '4269', '4270', '4271', '4272', '42731', '42760', '4279', '7850', 'V450', 'V533'],
    'Valvular': ['0932', '394', '395', '396', '397', '424', '7463', '7464', '7465', '7466', 'V422', 'V433'],
    'PHTN': ['4150', '4151', '4159', '4168', '4169', '5181', '5182', '5183', '5184', '5185', '5186', '5187', '5188', '5189'],
    'PVD': ['0930', '4373', '440', '441', '4431', '4432', '4433', '4434', '4435', '4436', '4437', '4438', '4439', '4471', '5571', '5579', 'V434'],
    'HTN': ['401', '402', '403', '404', '405'],
    'HTN_C': ['402', '403', '404'],
    'Para': ['342', '343', '3441', '3442', '3443', '3444', '3445', '3446', '3449'],
    'NeuroO': ['331', '332', '333', '334', '335', '336', '337', '338', '339', '340', '341', '345', '3483', '7803', '7843'],
    'COPD': ['4168', '4169', '490', '491', '492', '493', '494', '495', '496', '500', '501', '502', '503', '504', '505', '5064', '5081', '5088'],
    'Diabetes': ['2500', '2501', '2502', '2503', '2504', '2505', '2506', '2507', '2508', '2509'],
    'Diabetes_C': ['2504', '2505', '2506', '2507', '2508', '2509'],
    'Hypothyroidism': ['243', '2440', '2441', '2442', '2443', '2448', '2449'],
    'Renal': ['585', '586', '5880', 'V420', 'V451', 'V4511', 'V4512', 'V562', 'V568'],
    'Liver': ['070', '0706', '0709', '5712', '5714', '5715', '5716', '5718', '5719', '5723', '5728', '5734', '5735', '5738', '5739', 'V427'],
    'Ulcer': ['531', '532', '533', '534'],
    'AIDS': ['042', '043', '044'],
    'Lymphoma': ['200', '201', '202', '2030', '2386'],
    'Mets': ['196', '197', '198', '199'],
    'Tumor': ['140', '141', '142', '143', '144', '145', '146', '147', '148', '149', '150', '151', '152', '153', '154', '155', '156', '157', '158', '159', '160', '161', '162', '163', '164', '165', '166', '167', '168', '169', '170', '171', '172', '174', '175', '176', '177', '178', '179', '180', '181', '182', '183', '184', '185', '186', '187', '188', '189', '190', '191', '192', '193', '194', '195'],
    'Arthritis': ['714', '7141', '7142', '71481', '725'],
    'Coag': ['286', '2871', '2873', '2874', '2875', '2878', '2879', '7827'],
    'Obesity': ['2780', '27800', '27801', '2781', '2788', '27881'],
    'WeightLoss': ['260', '261', '262', '263', '2630', '2638', '2639', '7832', '7994'],
    'Anemia': ['2800', '2801', '2802', '2803', '2804', '2805', '2806', '2807', '2808', '2809', '281', '282', '283', '284', '285'],
    'Alcohol': ['2910', '2911', '2912', '2913', '2914', '2915', '2918', '2919', '303', '3050', '3575', '4255', '5711', '5712', '5713', '980', 'V113'],
    'Drug': ['292', '304', '3052', '3053', '3054', '3055', '3056', '3057', '3058', '3059', 'V6542'],
    'Psychosis': ['2938', '295', '297', '298', '299'],
    'Depression': ['2962', '2963', '2965', '3004']
}

def extract_features(dataset, tables=None):
    """
    Extract features for readmission prediction
    
    Parameters:
    -----------
    dataset : pandas.DataFrame
        Dataset with admissions and basic features
    tables : dict, optional
        Dictionary of raw MIMIC tables for additional feature extraction
        
    Returns:
    --------
    pandas.DataFrame
        Dataset with extracted features
    """
    print("Extracting features for readmission prediction...")
    
    # Create a copy to avoid modifying the original
    df = dataset.copy()
    
    # Demographic features
    df['age_group'] = pd.cut(df['anchor_age'], bins=[0, 18, 30, 50, 70, 100], 
                            labels=['0-18', '19-30', '31-50', '51-70', '71+'])
    df['male'] = (df['gender'] == 'M').astype(int)
    
    # Admission features
    df['weekend_admission'] = df['admittime'].dt.dayofweek.isin([5, 6]).astype(int)
    df['month'] = df['admittime'].dt.month
    df['hour_of_admission'] = df['admittime'].dt.hour
    
    # Group admission hour into periods
    df['admission_period'] = pd.cut(df['hour_of_admission'], 
                                   bins=[0, 6, 12, 18, 24], 
                                   labels=['Night', 'Morning', 'Afternoon', 'Evening'])
    
    # Length of stay features
    df['long_los'] = (df['length_of_stay'] > 7).astype(int)
    df['los_group'] = pd.cut(df['length_of_stay'], 
                            bins=[0, 1, 3, 7, 14, float('inf')], 
                            labels=['0-1 day', '1-3 days', '3-7 days', '7-14 days', '14+ days'])
    
    # Previous utilization features
    df['has_previous_admission'] = (df['prev_admissions_count'] > 0).astype(int)
    df['frequent_admissions'] = (df['prev_admissions_count'] >= 3).astype(int)
    
    # Extract comorbidities if diagnoses are available
    if 'icd_code' in df.columns and 'icd_version' in df.columns:
        df = extract_comorbidities(df)
    
    # Calculate Elixhauser score
    if all(comorbidity in df.columns for comorbidity in ELIXHAUSER_ICD9.keys()):
        print("Calculating Elixhauser comorbidity score...")
        # Simple unweighted score - sum of all comorbidities
        df['elixhauser_score'] = df[list(ELIXHAUSER_ICD9.keys())].sum(axis=1)
    
    # Add service-related features
    if 'curr_service' in df.columns:
        print("Adding service-related features...")
        # One-hot encode the service
        services_dummies = pd.get_dummies(df['curr_service'], prefix='service')
        df = pd.concat([df, services_dummies], axis=1)
    
    # Add discharge-related features
    if 'discharge_location' in df.columns:
        print("Adding discharge location features...")
        # Flag for discharge to care facility
        is_facility = df['discharge_location'].isin(
            ['SKILLED NURSING FACILITY', 'REHAB', 'LONG TERM CARE HOSPITAL', 'NURSING HOME']
        )
        df['discharge_to_facility'] = is_facility.fillna(False).astype(int)
        
        # Flag for discharge to home
        contains_home = df['discharge_location'].str.contains('HOME', case=False, na=False)
        df['discharge_to_home'] = contains_home.astype(int)
    
    # Drop unnecessary columns to save space
    df = df.drop(['admittime', 'dischtime', 'deathtime', 'edregtime', 'edouttime', 'next_admittime'], 
                errors='ignore')
    
    print(f"Feature extraction complete. Dataset now has {df.shape[1]} columns.")
    return df

def extract_comorbidities(dataset):
    """
    Extract comorbidity indicators based on ICD codes
    
    Parameters:
    -----------
    dataset : pandas.DataFrame
        Dataset with ICD codes
        
    Returns:
    --------
    pandas.DataFrame
        Dataset with added comorbidity indicators
    """
    print("Extracting comorbidity features...")
    df = dataset.copy()
    
    # Initialize comorbidity columns
    for comorbidity in ELIXHAUSER_ICD9.keys():
        df[comorbidity] = 0
    
    # Process only rows with valid ICD codes
    valid_icd = df.dropna(subset=['icd_code'])
    
    # Extract comorbidities from ICD-9 codes
    for comorbidity, codes in ELIXHAUSER_ICD9.items():
        # For ICD-9 codes
        icd9_rows = valid_icd[valid_icd['icd_version'] == 9]
        matching_rows = icd9_rows[icd9_rows['icd_code'].str.startswith(tuple(codes))]
        
        if len(matching_rows) > 0:
            # Set the flag for matching rows
            df.loc[matching_rows.index, comorbidity] = 1
    
    # For ICD-10 codes we'd need a separate mapping, not implemented in this example
    
    print(f"Extracted {len(ELIXHAUSER_ICD9)} comorbidity indicators")
    return df

def add_lab_features(dataset, lab_events, selected_items=None):
    """
    Add laboratory test features to the dataset
    
    Parameters:
    -----------
    dataset : pandas.DataFrame
        Dataset with admissions
    lab_events : pandas.DataFrame
        Laboratory events data
    selected_items : list, optional
        List of lab item IDs to include (if None, uses common labs)
        
    Returns:
    --------
    pandas.DataFrame
        Dataset with added lab features
    """
    print("Adding laboratory test features...")
    
    if selected_items is None:
        # Common lab tests associated with readmission risk
        # This would need to be adapted based on the actual itemid values in MIMIC-IV
        selected_items = [
            50912,  # Creatinine
            50971,  # Potassium
            50983,  # Sodium
            50802,  # Glucose
            51006,  # Urea Nitrogen
            51221,  # Hematocrit
            51301   # White Blood Cell Count
        ]
    
    # Filter for selected lab items and only include those taken near discharge
    lab_near_discharge = lab_events[
        (lab_events['itemid'].isin(selected_items))
    ]
    
    # Pivot to create one column per lab test (using the latest value for each admission)
    lab_features = lab_near_discharge.pivot_table(
        index=['subject_id', 'hadm_id'],
        columns='itemid',
        values='valuenum',
        aggfunc='last'
    ).reset_index()
    
    # Rename columns for clarity
    lab_names = {
        50912: 'last_creatinine',
        50971: 'last_potassium',
        50983: 'last_sodium',
        50802: 'last_glucose',
        51006: 'last_bun',
        51221: 'last_hematocrit',
        51301: 'last_wbc'
    }
    
    lab_features.rename(columns=lab_names, inplace=True)
    
    # Merge with dataset
    result = dataset.merge(lab_features, on=['subject_id', 'hadm_id'], how='left')
    
    print(f"Added {len(selected_items)} lab features")
    return result

def save_features(features_df, output_dir, filename='readmission_features.csv'):
    """
    Save the extracted features to disk
    
    Parameters:
    -----------
    features_df : pandas.DataFrame
        Dataset with extracted features
    output_dir : str
        Directory to save the dataset
    filename : str
        Name of the output file
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    # Save to CSV
    features_df.to_csv(output_path, index=False)
    print(f"Features saved to {output_path}")
    
    # Save feature info
    feature_info = pd.DataFrame({
        'feature': features_df.columns,
        'dtype': features_df.dtypes.astype(str),
        'missing_pct': features_df.isnull().mean() * 100,
        'unique_values': [features_df[col].nunique() if col in features_df.columns else None 
                          for col in features_df.columns]
    })
    
    feature_info_path = os.path.join(output_dir, "feature_info.csv")
    feature_info.to_csv(feature_info_path, index=False)
    print(f"Feature information saved to {feature_info_path}")

if __name__ == "__main__":
    # Example usage
    data_dir = os.path.join(os.getcwd(), 'data', 'processed', 'readmission')
    output_dir = data_dir
    
    # Load processed dataset
    dataset_path = os.path.join(data_dir, 'readmission_data.csv')
    if os.path.exists(dataset_path):
        dataset = pd.read_csv(dataset_path)
        
        # Convert date columns back to datetime
        date_cols = ['admittime', 'dischtime', 'deathtime', 'edregtime', 'edouttime', 'next_admittime']
        for col in date_cols:
            if col in dataset.columns:
                dataset[col] = pd.to_datetime(dataset[col])
        
        # Extract features
        features_df = extract_features(dataset)
        
        # Save features
        save_features(features_df, output_dir)
    else:
        print(f"Dataset not found at {dataset_path}")
