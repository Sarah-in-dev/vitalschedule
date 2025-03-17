# Hospital Readmission Prediction

## Overview

This module provides a machine learning pipeline for predicting hospital readmissions using the MIMIC-IV dataset. It identifies patients at risk of readmission within a specified time window (default: 30 days) after discharge, enabling targeted interventions to reduce readmission rates.

## Features

- **Data Processing**: Load and process MIMIC-IV data to identify index admissions and subsequent readmissions
- **Feature Engineering**: Extract clinical, demographic, and utilization features known to predict readmission risk
- **Model Training**: Train and evaluate multiple predictive models (logistic regression, random forest, XGBoost)
- **Comprehensive Evaluation**: Measure model performance across different patient subgroups
- **Pipeline Automation**: End-to-end workflow from raw data to trained models

## Directory Structure

vitalschedule/
├── code/
│   └── readmission/            # Readmission prediction code
│       ├── data_processing.py  # Data loading and preprocessing
│       ├── feature_extraction.py # Feature engineering
│       ├── model_training.py   # Model training and tuning
│       ├── evaluation.py       # Performance evaluation
│       └── run_pipeline.py     # Main pipeline script
├── data/
│   ├── raw/
│   │   └── mimic-iv/           # Raw MIMIC-IV data (not included in repo)
│   └── processed/
│       └── readmission/        # Processed datasets
├── models/
│   └── readmission/            # Trained models
└── outputs/
└── readmission/            # Results and visualizations

## Getting Started

### Prerequisites

- Python 3.9+
- MIMIC-IV dataset access (requires PhysioNet credentials)
- Required Python packages: pandas, numpy, scikit-learn, xgboost, matplotlib, seaborn

### Data Setup

1. Download the MIMIC-IV dataset:
   ```bash
   cd data/raw
   wget -r -N -c -np --user YOUR_PHYSIONET_USER --ask-password https://physionet.org/files/mimiciv/3.1/

Process the data:
bashCopypython code/readmission/run_pipeline.py --skip_model_training


Running the Pipeline
To run the full pipeline:
bashCopypython code/readmission/run_pipeline.py
Options:

--readmission_window DAYS: Set the readmission window in days (default: 30)
--tune_models: Perform hyperparameter tuning
--skip_data_processing: Skip data processing step
--skip_feature_extraction: Skip feature extraction step

Model Features
The pipeline extracts the following types of features:

Demographics: Age, gender
Clinical: Comorbidities, Elixhauser score
Visit Characteristics: Length of stay, admission type
Utilization History: Previous admissions, emergency visits
Discharge Information: Discharge location, discharge against medical advice

Performance
Initial evaluation shows promising results for predicting 30-day readmissions:

AUC: ~0.70-0.75
Key predictors: Previous admissions, length of stay, comorbidity count

Future Improvements

Integration with intervention recommendation system
Enhanced feature engineering with more detailed clinical data
Model explainability components
Real-time risk scoring API

References

MIMIC-IV Dataset: Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV (version 2.2). PhysioNet. https://doi.org/10.13026/6mm1-ek67
Readmission Risk Factors: Kansagara, D., et al. (2011). Risk prediction models for hospital readmission: a systematic review. Jama, 306(15), 1688-1698.
