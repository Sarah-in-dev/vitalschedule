import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

def fetch_historical_weather(lat, lon, date):
    """
    Placeholder function to fetch historical weather
    In a real implementation, this would call a weather API
    
    For now, we'll simulate weather data
    """
    # Simulate weather data
    # In production, use an API like OpenWeatherMap or Visual Crossing
    
    # Generate random temperature based on month
    month = date.month
    base_temp = 50 + 20 * np.sin((month - 1) * np.pi / 6)  # Seasonal variation
    temp = base_temp + np.random.normal(0, 10)  # Add random variation
    
    # Generate precipitation probability
    precip_prob = np.random.beta(2, 5) if month in [4, 5, 6, 9, 10, 11] else np.random.beta(1, 3)
    
    # Generate weather condition
    conditions = ['Clear', 'Cloudy', 'Rain', 'Snow', 'Stormy']
    weights = [0.4, 0.3, 0.2, 0.05, 0.05]
    if month in [12, 1, 2]:  # Winter
        weights = [0.3, 0.3, 0.1, 0.25, 0.05]
    elif month in [6, 7, 8]:  # Summer
        weights = [0.5, 0.2, 0.2, 0, 0.1]
    
    condition = np.random.choice(conditions, p=weights)
    
    return {
        'date': date,
        'temperature': temp,
        'precipitation_probability': precip_prob,
        'condition': condition,
        'is_extreme_weather': condition in ['Snow', 'Stormy'] or temp > 95 or temp < 10
    }

def add_weather_data(appointments_df, lat=40.7128, lon=-74.0060):
    """
    Add synthetic weather data to appointment dataframe
    
    Parameters:
    -----------
    appointments_df : pandas.DataFrame
        DataFrame containing appointments with 'appointment_datetime' column
    lat, lon : float
        Latitude and longitude for weather data
        
    Returns:
    --------
    pandas.DataFrame
        Original dataframe with weather columns added
    """
    weather_data = []
    
    for _, row in appointments_df.iterrows():
        appt_date = row['appointment_datetime']
        weather = fetch_historical_weather(lat, lon, appt_date)
        weather_data.append(weather)
    
    weather_df = pd.DataFrame(weather_data)
    
    # Add weather data to appointments
    result_df = pd.concat([appointments_df.reset_index(drop=True), 
                           weather_df.reset_index(drop=True)], axis=1)
    
    return result_df
