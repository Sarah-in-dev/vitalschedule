"""
Configuration settings for the VitalSchedule project.
"""

# Paths
DATA_DIR = "../data"
RAW_DATA_DIR = f"{DATA_DIR}/raw"
PROCESSED_DATA_DIR = f"{DATA_DIR}/processed"
MODEL_DIR = "../models"

# Model parameters
RANDOM_SEED = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Features configuration
CATEGORICAL_FEATURES = [
    'gender', 
    'insurance', 
    'appointment_type',
    'time_of_day',
    'season'
]

NUMERICAL_FEATURES = [
    'age',
    'distance',
    'lead_time',
    'transport_score',
    'ses_score',
    'days_since_prev_appt',
    'historical_noshow_rate'
]

TARGET = 'is_noshow'
