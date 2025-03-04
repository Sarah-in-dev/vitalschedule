import pandas as pd
import numpy as np

def generate_zip_census_data(n_zips=100):
    """
    Generate synthetic census data by ZIP code
    
    Parameters:
    -----------
    n_zips : int
        Number of ZIP codes to generate
        
    Returns:
    --------
    pandas.DataFrame
        Synthetic census data by ZIP
    """
    zips = []
    
    for i in range(n_zips):
        zip_code = f"{10000 + i:05d}"
        
        # Median household income
        median_income = np.random.lognormal(mean=10.8, sigma=0.5)
        
        # Public transit access score (0-10)
        transit_score = np.random.beta(2, 2) * 10
        
        # Population density (people per square mile)
        pop_density = np.random.lognormal(mean=7, sigma=1.5)
        
        # Poverty rate (percentage)
        poverty_rate = np.random.beta(2, 7) * 100
        
        # Median age
        median_age = np.random.normal(38, 5)
        
        # Percentage with health insurance
        health_insurance_rate = (100 - poverty_rate/2) + np.random.normal(0, 5)
        health_insurance_rate = max(0, min(100, health_insurance_rate))
        
        zips.append({
            'zip_code': zip_code,
            'median_income': median_income,
            'transit_score': transit_score,
            'population_density': pop_density,
            'poverty_rate': poverty_rate,
            'median_age': median_age,
            'health_insurance_rate': health_insurance_rate
        })
    
    return pd.DataFrame(zips)

def assign_patient_zips(patient_df, zip_census_df):
    """
    Assign ZIP codes to patients based on their socioeconomic score
    
    Parameters:
    -----------
    patient_df : pandas.DataFrame
        DataFrame containing patient data with 'ses_score' column
    zip_census_df : pandas.DataFrame
        DataFrame containing ZIP census data
        
    Returns:
    --------
    pandas.DataFrame
        Patient dataframe with ZIP code added
    """
    # Create probability weights for each ZIP based on income
    # Higher SES patients more likely to be in higher income ZIPs
    result_df = patient_df.copy()
    
    zip_income_rank = zip_census_df['median_income'].rank(pct=True)
    
    for i, row in result_df.iterrows():
        ses_score_pct = row['ses_score'] / 10.0  # Convert to 0-1 scale
        
        # Find closest matching ZIP by income rank
        # Add some noise to make it probabilistic
        target_rank = ses_score_pct + np.random.normal(0, 0.1)
        target_rank = max(0, min(1, target_rank))
        
        closest_zip_idx = (zip_income_rank - target_rank).abs().idxmin()
        assigned_zip = zip_census_df.loc[closest_zip_idx, 'zip_code']
        
        result_df.at[i, 'zip_code'] = assigned_zip
    
    return result_df
