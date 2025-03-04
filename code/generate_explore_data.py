import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys

# Add the code directory to the path
sys.path.append('code')

# Import project modules
from synthetic_data import generate_synthetic_data
from feature_engineering import create_temporal_features, create_patient_history_features, create_environmental_features
from census_data import generate_zip_census_data, assign_patient_zips
from weather_data import add_weather_data
from config import DATA_DIR, PROCESSED_DATA_DIR

# Create directories if they don't exist
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Set plotting style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)

def generate_full_dataset(n_patients=1000, n_appointments=5000, save=True):
    """
    Generate a complete synthetic dataset by combining all data sources
    
    Parameters:
    -----------
    n_patients : int
        Number of patients to generate
    n_appointments : int
        Number of appointments to generate
    save : bool
        Whether to save the dataset to disk
        
    Returns:
    --------
    pandas.DataFrame
        Complete synthetic dataset
    """
    print(f"Generating synthetic data with {n_patients} patients and {n_appointments} appointments...")
    
    # Generate base appointment data
    base_data = generate_synthetic_data(n_patients, n_appointments)
    print(f"Base data generated: {base_data.shape[0]} rows, {base_data.shape[1]} columns")
    
    # Generate census data and assign to patients
    print("Generating ZIP code census data...")
    zip_data = generate_zip_census_data(n_zips=100)
    
    # Add census data to patient records
    print("Assigning ZIP codes to patients...")
    patient_columns = ['patient_id', 'age', 'gender', 'distance', 'insurance', 'ses_score', 'transport_score', 'prev_noshow_rate']
    patients_df = base_data[patient_columns].drop_duplicates('patient_id')
    patients_with_zips = assign_patient_zips(patients_df, zip_data)
    
    # Merge ZIP data back to main dataset
    print("Merging ZIP data with appointments...")
    data_with_zips = base_data.merge(patients_with_zips[['patient_id', 'zip_code']], on='patient_id')
    data_with_census = data_with_zips.merge(zip_data, on='zip_code')
    
    # Add weather data
    print("Adding weather data...")
    data_with_weather = add_weather_data(data_with_census)
    
    # Create derived features
    print("Creating temporal features...")
    data_with_temporal = create_temporal_features(data_with_weather)
    
    print("Creating patient history features...")
    data_with_history = create_patient_history_features(data_with_temporal)
    
    print("Creating environmental features...")
    final_data = create_environmental_features(data_with_history)
    
    # Save to disk if requested
    if save:
        output_path = os.path.join(PROCESSED_DATA_DIR, 'synthetic_full_dataset.csv')
        final_data.to_csv(output_path, index=False)
        print(f"Dataset saved to {output_path}")
    
    print(f"Final dataset shape: {final_data.shape[0]} rows, {final_data.shape[1]} columns")
    return final_data

def create_exploratory_visualizations(data, output_dir=None):
    """
    Create exploratory visualizations of the dataset
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Dataset to visualize
    output_dir : str, optional
        Directory to save visualizations to
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 1. No-show distribution
    plt.figure(figsize=(10, 6))
    show_counts = data['is_noshow'].value_counts()
    ax = sns.barplot(x=show_counts.index, y=show_counts.values)
    plt.title('Distribution of No-shows vs. Attended Appointments')
    plt.xlabel('No-show Status (1 = No-show, 0 = Attended)')
    plt.ylabel('Count')
    for i, count in enumerate(show_counts.values):
        ax.text(i, count + 100, f'{count} ({count/sum(show_counts.values):.1%})', 
                ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '01_noshow_distribution.png'))
    plt.show()
    
    # 2. No-show rate by appointment type
    plt.figure(figsize=(12, 7))
    appt_type_noshow = data.groupby('appointment_type')['is_noshow'].mean().sort_values(ascending=False)
    ax = sns.barplot(x=appt_type_noshow.index, y=appt_type_noshow.values)
    plt.title('No-show Rate by Appointment Type')
    plt.xlabel('Appointment Type')
    plt.ylabel('No-show Rate')
    plt.ylim(0, max(appt_type_noshow.values) * 1.2)
    for i, rate in enumerate(appt_type_noshow.values):
        ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '02_noshow_by_appt_type.png'))
    plt.show()
    
    # 3. No-show rate by day of week
    plt.figure(figsize=(12, 7))
    day_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    data['day_name'] = data['day_of_week'].map(day_mapping)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_noshow = data.groupby('day_name')['is_noshow'].mean()
    day_noshow = day_noshow.reindex(day_order)
    ax = sns.barplot(x=day_noshow.index, y=day_noshow.values)
    plt.title('No-show Rate by Day of Week')
    plt.xlabel('Day of Week')
    plt.ylabel('No-show Rate')
    plt.ylim(0, max(day_noshow.values) * 1.2)
    for i, rate in enumerate(day_noshow.values):
        ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '03_noshow_by_day.png'))
    plt.close()
    
    # 4. No-show rate by hour of day
    plt.figure(figsize=(14, 7))
    hour_noshow = data.groupby('hour_of_day')['is_noshow'].mean()
    ax = sns.lineplot(x=hour_noshow.index, y=hour_noshow.values, marker='o', linewidth=2)
    plt.title('No-show Rate by Hour of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('No-show Rate')
    plt.xticks(hour_noshow.index)
    plt.ylim(0, max(hour_noshow.values) * 1.2)
    for i, rate in enumerate(hour_noshow.values):
        ax.text(hour_noshow.index[i], rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '04_noshow_by_hour.png'))
    plt.show()
    
    # 5. No-show rate by lead time (binned)
    plt.figure(figsize=(14, 7))
    # Create lead time bins
    bins = [0, 1, 3, 7, 14, 30, 60, 90, float('inf')]
    labels = ['Same day', '1-3 days', '4-7 days', '1-2 weeks', '2-4 weeks', '1-2 months', '2-3 months', '3+ months']
    data['lead_time_bin'] = pd.cut(data['lead_time'], bins=bins, labels=labels)
    lead_noshow = data.groupby('lead_time_bin')['is_noshow'].mean()
    ax = sns.barplot(x=lead_noshow.index, y=lead_noshow.values)
    plt.title('No-show Rate by Appointment Lead Time')
    plt.xlabel('Lead Time')
    plt.ylabel('No-show Rate')
    plt.xticks(rotation=45)
    plt.ylim(0, max(lead_noshow.values) * 1.2)
    for i, rate in enumerate(lead_noshow.values):
        ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '05_noshow_by_leadtime.png'))
    plt.show()
    
    # 6. No-show rate by distance (binned)
    plt.figure(figsize=(14, 7))
    # Create distance bins
    bins = [0, 5, 10, 15, 20, 30, 50]
    labels = ['0-5 miles', '5-10 miles', '10-15 miles', '15-20 miles', '20-30 miles', '30+ miles']
    data['distance_bin'] = pd.cut(data['distance'], bins=bins, labels=labels)
    distance_noshow = data.groupby('distance_bin')['is_noshow'].mean()
    ax = sns.barplot(x=distance_noshow.index, y=distance_noshow.values)
    plt.title('No-show Rate by Distance from Clinic')
    plt.xlabel('Distance')
    plt.ylabel('No-show Rate')
    plt.ylim(0, max(distance_noshow.values) * 1.2)
    for i, rate in enumerate(distance_noshow.values):
        ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '06_noshow_by_distance.png'))
    plt.show()
    
    # 7. No-show rate by insurance type
    plt.figure(figsize=(12, 7))
    insurance_noshow = data.groupby('insurance')['is_noshow'].mean().sort_values(ascending=False)
    ax = sns.barplot(x=insurance_noshow.index, y=insurance_noshow.values)
    plt.title('No-show Rate by Insurance Type')
    plt.xlabel('Insurance Type')
    plt.ylabel('No-show Rate')
    plt.ylim(0, max(insurance_noshow.values) * 1.2)
    for i, rate in enumerate(insurance_noshow.values):
        ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '07_noshow_by_insurance.png'))
    plt.show()
    
    # 8. No-show rate by weather condition
    plt.figure(figsize=(12, 7))
    weather_noshow = data.groupby('condition')['is_noshow'].mean().sort_values(ascending=False)
    ax = sns.barplot(x=weather_noshow.index, y=weather_noshow.values)
    plt.title('No-show Rate by Weather Condition')
    plt.xlabel('Weather Condition')
    plt.ylabel('No-show Rate')
    plt.ylim(0, max(weather_noshow.values) * 1.2)
    for i, rate in enumerate(weather_noshow.values):
        ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '08_noshow_by_weather.png'))
    plt.show()
    
    # 9. No-show rate by age group
    plt.figure(figsize=(12, 7))
    # Create age bins
    bins = [0, 18, 30, 45, 65, 100]
    labels = ['<18', '18-30', '31-45', '46-65', '65+']
    data['age_group'] = pd.cut(data['age'], bins=bins, labels=labels)
    age_noshow = data.groupby('age_group')['is_noshow'].mean()
    ax = sns.barplot(x=age_noshow.index, y=age_noshow.values)
    plt.title('No-show Rate by Age Group')
    plt.xlabel('Age Group')
    plt.ylabel('No-show Rate')
    plt.ylim(0, max(age_noshow.values) * 1.2)
    for i, rate in enumerate(age_noshow.values):
        ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '09_noshow_by_age.png'))
    plt.show()
    
    # 10. No-show rate by previous no-show history
    plt.figure(figsize=(12, 7))
    # Create history bins
    bins = [-0.01, 0, 0.25, 0.5, 0.75, 1]
    labels = ['No history', '1-25%', '26-50%', '51-75%', '76-100%']
    data['noshow_history_bin'] = pd.cut(data['historical_noshow_rate'], bins=bins, labels=labels)
    history_noshow = data.groupby('noshow_history_bin')['is_noshow'].mean()
    ax = sns.barplot(x=history_noshow.index, y=history_noshow.values)
    plt.title('No-show Rate by Historical No-show Rate')
    plt.xlabel('Historical No-show Rate')
    plt.ylabel('No-show Rate')
    plt.ylim(0, max(history_noshow.values) * 1.2)
    for i, rate in enumerate(history_noshow.values):
        ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '10_noshow_by_history.png'))
    plt.show()
    
    # 11. Correlation heatmap of numerical features
    plt.figure(figsize=(16, 12))
    # Select numerical columns
    numerical_cols = ['age', 'distance', 'lead_time', 'ses_score', 'transport_score', 
                      'prev_noshow_rate', 'historical_noshow_rate', 'is_noshow',
                      'median_income', 'transit_score', 'population_density',
                      'poverty_rate', 'health_insurance_rate', 'temperature']
    # Create correlation matrix
    corr_matrix = data[numerical_cols].corr()
    # Create heatmap
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, cmap='RdBu_r', vmin=-1, vmax=1, 
                annot=True, fmt='.2f', square=True, linewidths=0.5)
    plt.title('Correlation Matrix of Numerical Features')
    if output_dir:
        plt.savefig(os.path.join(output_dir, '11_correlation_matrix.png'))
    plt.show()
    
    # 12. Pair plot of key features
    key_features = ['age', 'distance', 'lead_time', 'transport_score', 'is_noshow']
    sns.pairplot(data[key_features], hue='is_noshow', palette='viridis')
    plt.suptitle('Pairwise Relationships Between Key Features', y=1.02)
    if output_dir:
        plt.savefig(os.path.join(output_dir, '12_pairplot.png'))
    plt.show()
    
    print("Exploratory visualizations complete!")

# Function to identify key factors associated with no-shows
def analyze_noshow_factors(data):
    """
    Analyze key factors associated with no-shows and their relative importance
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Dataset to analyze
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with feature importance metrics
    """
    print("Analyzing factors associated with no-shows...")
    
    # Calculate absolute difference in no-show rate for each feature
    factors = []
    
    # Categorical features
    categorical_features = [
        'appointment_type', 'day_name', 'time_of_day', 'insurance',
        'condition', 'age_group', 'lead_time_bin', 'distance_bin',
        'noshow_history_bin', 'gender'
    ]
    
    for feature in categorical_features:
        if feature in data.columns:
            # Calculate no-show rate for each category
            group_rates = data.groupby(feature)['is_noshow'].mean()
            
            # Calculate the range of rates (max - min)
            rate_range = group_rates.max() - group_rates.min()
            
            # Store the feature and its importance
            factors.append({
                'feature': feature,
                'importance': rate_range,
                'max_category': group_rates.idxmax(),
                'max_rate': group_rates.max(),
                'min_category': group_rates.idxmin(),
                'min_rate': group_rates.min()
            })
    
    # Convert to DataFrame and sort by importance
    factors_df = pd.DataFrame(factors).sort_values('importance', ascending=False)
    
    # Display the results
    print("\nKey factors influencing no-show rates (by rate range):")
    for i, row in factors_df.iterrows():
        print(f"{row['feature']}: {row['importance']:.2f} - Highest in {row['max_category']} ({row['max_rate']:.1%}), Lowest in {row['min_category']} ({row['min_rate']:.1%})")
    
    return factors_df

# Main execution
if __name__ == "__main__":
    # Generate dataset
    data = generate_full_dataset(n_patients=1000, n_appointments=5000)
    
    # Create visualizations folder
    viz_dir = os.path.join('visualization', 'exploratory')
    
    # Create visualizations
    create_exploratory_visualizations(data, viz_dir)
    
    # Analyze key factors
    factors_df = analyze_noshow_factors(data)
    
    print("\nExploratory data analysis complete!")
