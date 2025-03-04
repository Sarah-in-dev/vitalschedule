import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_realistic_synthetic_data(n_patients=1000, n_appointments=5000, target_noshow_rate=0.25):
    """
    Generate synthetic appointment data with a more realistic no-show rate
    
    Parameters:
    -----------
    n_patients : int
        Number of unique patients to generate
    n_appointments : int
        Total number of appointments to generate
    target_noshow_rate : float
        Target no-show rate (0.20-0.30 is realistic for many healthcare settings)
    
    Returns:
    --------
    pandas.DataFrame
        Synthetic appointment data
    """
    # Create patient demographics
    patients = []
    for i in range(n_patients):
        age = np.random.normal(45, 15)  # Mean age 45, std 15
        age = max(18, min(90, int(age)))  # Bound between 18-90
        
        # Gender distribution
        gender = np.random.choice(['M', 'F'], p=[0.45, 0.55])
        
        # Distance from clinic - lognormal distribution
        distance = np.random.lognormal(mean=1.5, sigma=1.0)
        distance = min(50, distance)  # Cap at 50 miles
        
        # Insurance type
        insurance = np.random.choice(['Medicaid', 'Medicare', 'Private', 'Self-Pay', 'None'], 
                                   p=[0.4, 0.25, 0.2, 0.1, 0.05])
        
        # Socioeconomic score (proxy for various SDOH)
        # Lower values indicate more barriers
        ses_score = np.random.beta(2, 2) * 10  
        
        # Transportation access
        # Correlated with SES and distance
        transport_score = max(0, min(10, ses_score * 0.7 + np.random.normal(0, 1) - distance/20))
        
        # Previous no-show rate (0-1) - adjusted to be more realistic
        prev_noshow_rate = max(0, min(0.8, 0.3 - ses_score/25 + np.random.normal(0, 0.1)))
        
        patients.append({
            'patient_id': f'P{i:04d}',
            'age': age,
            'gender': gender,
            'distance': distance,
            'insurance': insurance,
            'ses_score': ses_score,
            'transport_score': transport_score,
            'prev_noshow_rate': prev_noshow_rate
        })
    
    patients_df = pd.DataFrame(patients)
    
    # Generate appointments
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    
    appointments = []
    
    # Calculate global scaling factor to achieve target no-show rate
    # This will be adjusted later based on actual results
    global_scale_factor = target_noshow_rate / 0.7  # Initial estimate
    
    for i in range(n_appointments):
        # Randomly select a patient
        patient_idx = np.random.randint(0, n_patients)
        patient = patients_df.iloc[patient_idx]
        
        # Appointment date and time
        days_offset = int(np.random.randint(0, 365))
        hour = int(np.random.choice(range(8, 17)))
        minute = int(np.random.choice([0, 15, 30, 45]))
        appt_datetime = start_date + timedelta(days=days_offset, hours=hour, minutes=minute)
        
        # Day of week effect
        day_of_week = appt_datetime.weekday()
        # Monday and Friday have higher no-show rates
        dow_factor = 1.2 if day_of_week in [0, 4] else 1.0
        
        # Time of day effect (early morning and late afternoon have higher no-show)
        tod_factor = 1.2 if hour < 10 or hour > 15 else 1.0
        
        # Appointment type
        appt_type = np.random.choice(['Primary Care', 'Behavioral Health', 'Dental', 'Specialty'], 
                                  p=[0.6, 0.2, 0.15, 0.05])
        
        # Type effect (behavioral health has higher no-show)
        type_factor = 1.3 if appt_type == 'Behavioral Health' else 1.0
        
        # Lead time (days between scheduling and appointment)
        lead_time = np.random.lognormal(mean=2.5, sigma=0.8)
        lead_time = min(90, int(lead_time))
        
        # Lead time effect (longer lead times have higher no-show)
        lead_factor = min(1.5, 1.0 + lead_time/60)  # Reduced impact
        
        # Weather effect (random proxy)
        weather_factor = np.random.uniform(0.9, 1.1)  # Reduced impact
        
        # Calculate no-show probability
        base_prob = patient['prev_noshow_rate']
        noshow_prob = base_prob * dow_factor * tod_factor * type_factor * lead_factor * weather_factor
        
        # Adjust based on transport score (lower score means higher no-show)
        transport_effect = max(0.9, 1.5 - patient['transport_score']/10)  # Reduced impact
        noshow_prob *= transport_effect
        
        # Apply global scaling factor to achieve target rate
        noshow_prob *= global_scale_factor
        
        # Cap probability between 0 and 1
        noshow_prob = max(0, min(1, noshow_prob))
        
        # Determine outcome
        noshow = np.random.random() < noshow_prob
        
        appointments.append({
            'appointment_id': f'A{i:06d}',
            'patient_id': patient['patient_id'],
            'appointment_datetime': appt_datetime,
            'appointment_type': appt_type,
            'lead_time': lead_time,
            'day_of_week': day_of_week,
            'hour_of_day': hour,
            'noshow_probability': noshow_prob,
            'is_noshow': noshow,
            'scheduling_date': appt_datetime - timedelta(days=lead_time)
        })
    
    appointments_df = pd.DataFrame(appointments)
    
    # Merge with patient data
    full_df = appointments_df.merge(patients_df, on='patient_id')
    
    # Check actual no-show rate and adjust if needed
    actual_rate = full_df['is_noshow'].mean()
    print(f"Generated data with no-show rate: {actual_rate:.2%}")
    
    # If the actual rate is too far from target, we could re-run with an adjusted scale factor
    if abs(actual_rate - target_noshow_rate) > 0.05:
        print(f"Adjusting no-show rate to match target of {target_noshow_rate:.2%}...")
        # Determine how many no-shows to flip to achieve target rate
        current_no_shows = full_df['is_noshow'].sum()
        target_no_shows = int(target_noshow_rate * len(full_df))
        
        if current_no_shows > target_no_shows:
            # Need to flip some no-shows to shows
            no_show_indices = full_df[full_df['is_noshow'] == True].index
            num_to_flip = current_no_shows - target_no_shows
            indices_to_flip = np.random.choice(no_show_indices, size=num_to_flip, replace=False)
            full_df.loc[indices_to_flip, 'is_noshow'] = False
        else:
            # Need to flip some shows to no-shows
            show_indices = full_df[full_df['is_noshow'] == False].index
            num_to_flip = target_no_shows - current_no_shows
            indices_to_flip = np.random.choice(show_indices, size=num_to_flip, replace=False)
            full_df.loc[indices_to_flip, 'is_noshow'] = True
        
        # Verify the new rate
        adjusted_rate = full_df['is_noshow'].mean()
        print(f"Adjusted no-show rate: {adjusted_rate:.2%}")
    
    return full_df

if __name__ == "__main__":
    # Generate and save synthetic data
    data = generate_realistic_synthetic_data(n_patients=2000, n_appointments=10000, target_noshow_rate=0.25)
    data.to_csv('../data/realistic_synthetic_appointments.csv', index=False)
    print(f"Generated {len(data)} synthetic appointments with {data['is_noshow'].mean():.2%} no-show rate")
