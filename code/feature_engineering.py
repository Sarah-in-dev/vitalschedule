import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_temporal_features(df, datetime_col='appointment_datetime'):
    """
    Create time-based features from appointment datetime
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing appointment data
    datetime_col : str
        Name of the column containing appointment datetime
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with additional temporal features
    """
    result = df.copy()
    
    # Ensure datetime column is datetime type
    if not pd.api.types.is_datetime64_any_dtype(result[datetime_col]):
        result[datetime_col] = pd.to_datetime(result[datetime_col])
    
    # Extract basic time components
    result['appointment_hour'] = result[datetime_col].dt.hour
    result['appointment_minute'] = result[datetime_col].dt.minute
    result['appointment_day'] = result[datetime_col].dt.day
    result['appointment_month'] = result[datetime_col].dt.month
    result['appointment_year'] = result[datetime_col].dt.year
    result['appointment_dayofweek'] = result[datetime_col].dt.dayofweek
    result['appointment_quarter'] = result[datetime_col].dt.quarter
    
    # Create derived features
    # Morning/Afternoon/Evening
    result['time_of_day'] = pd.cut(
        result['appointment_hour'],
        bins=[0, 12, 17, 24],
        labels=['Morning', 'Afternoon', 'Evening'],
        include_lowest=True
    )
    
    # Is weekend
    result['is_weekend'] = result['appointment_dayofweek'].isin([5, 6]).astype(int)
    
    # Part of month
    result['part_of_month'] = pd.cut(
        result['appointment_day'],
        bins=[0, 10, 20, 31],
        labels=['Early', 'Mid', 'Late'],
        include_lowest=True
    )
    
    # Season
    result['season'] = pd.cut(
        result['appointment_month'],
        bins=[0, 3, 6, 9, 12],
        labels=['Winter', 'Spring', 'Summer', 'Fall'],
        include_lowest=True
    )
    
    return result

def create_patient_history_features(df, patient_id_col='patient_id', datetime_col='appointment_datetime'):
    """
    Create features based on patient appointment history
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing appointment data
    patient_id_col : str
        Name of the column containing patient ID
    datetime_col : str
        Name of the column containing appointment datetime
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with additional patient history features
    """
    result = df.copy()
    
    # Ensure datetime column is datetime type
    if not pd.api.types.is_datetime64_any_dtype(result[datetime_col]):
        result[datetime_col] = pd.to_datetime(result[datetime_col])
    
    # Sort by patient and date
    result = result.sort_values([patient_id_col, datetime_col])
    
    # Calculate days since previous appointment
    result['prev_appt_date'] = result.groupby(patient_id_col)[datetime_col].shift(1)
    result['days_since_prev_appt'] = (result[datetime_col] - result['prev_appt_date']).dt.days
    
    # Calculate historical no-show rate
    result['noshow_cumcount'] = result.groupby(patient_id_col)['is_noshow'].cumsum()
    result['appt_cumcount'] = result.groupby(patient_id_col).cumcount()
    result['historical_noshow_rate'] = result['noshow_cumcount'] / result['appt_cumcount']
    result['historical_noshow_rate'] = result['historical_noshow_rate'].fillna(0)
    
    # Previous appointment outcomes
    result['prev_appt_noshow'] = result.groupby(patient_id_col)['is_noshow'].shift(1).fillna(0)
    result['second_prev_appt_noshow'] = result.groupby(patient_id_col)['is_noshow'].shift(2).fillna(0)
    
    # Recent no-show streak
    def calc_streak(group):
        streak = 0
        streaks = []
        for noshow in group:
            if noshow:
                streak += 1
            else:
                streak = 0
            streaks.append(streak)
        return streaks
    
    result['noshow_streak'] = result.groupby(patient_id_col)['is_noshow'].transform(calc_streak)
    
    return result

def create_environmental_features(df, weather_condition_col='condition', temp_col='temperature'):
    """
    Create features based on environmental factors
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing appointment and weather data
    weather_condition_col : str
        Name of the column containing weather condition
    temp_col : str
        Name of the column containing temperature
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with additional environmental features
    """
    result = df.copy()
    
    # Weather severity
    weather_severity = {
        'Clear': 0,
        'Cloudy': 1,
        'Rain': 2,
        'Snow': 3,
        'Stormy': 4
    }
    
    if weather_condition_col in result.columns:
        result['weather_severity'] = result[weather_condition_col].map(weather_severity).fillna(0)
    
    # Temperature extremes
    if temp_col in result.columns:
        result['is_extreme_temp'] = ((result[temp_col] > 90) | (result[temp_col] < 32)).astype(int)
    
    return result
