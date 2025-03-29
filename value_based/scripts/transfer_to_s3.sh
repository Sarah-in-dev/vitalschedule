#!/bin/bash
#SBATCH --job-name=aws_transfer
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH --partition=hpg2-compute
#SBATCH --output=../logs/aws_transfer_%j.out
#SBATCH --error=../logs/aws_transfer_%j.err

# Load AWS CLI module
module load awscli/2.11.7

# Set environment variables
ORG_NAME="predictiverx"
BASE_DIR=~/vitalschedule/value_based
PROCESSED_DIR=$BASE_DIR/processed_data
MODELS_DIR=$BASE_DIR/models
RAW_BUCKET="vbc-raw-data-$ORG_NAME"
PROCESSED_BUCKET="vbc-processed-data-$ORG_NAME"
MODELS_BUCKET="vbc-models-$ORG_NAME"

echo "Starting transfer process at $(date)"

# Create temporary file for creating directories
touch empty.tmp

# Create folder structure in S3 buckets if needed
echo "Creating folder structure in S3 buckets..."

# Create structure for processed data bucket
aws s3 cp ./empty.tmp "s3://$PROCESSED_BUCKET/patient-cohorts/empty.tmp"
echo "Created patient-cohorts/ directory"

aws s3 cp ./empty.tmp "s3://$PROCESSED_BUCKET/clinical-features/empty.tmp"
echo "Created clinical-features/ directory"

aws s3 cp ./empty.tmp "s3://$PROCESSED_BUCKET/medications/empty.tmp"
echo "Created medications/ directory"

aws s3 cp ./empty.tmp "s3://$PROCESSED_BUCKET/diagnoses/empty.tmp"
echo "Created diagnoses/ directory"

aws s3 cp ./empty.tmp "s3://$PROCESSED_BUCKET/utilization/empty.tmp"
echo "Created utilization/ directory"

aws s3 cp ./empty.tmp "s3://$PROCESSED_BUCKET/lab-results/empty.tmp"
echo "Created lab-results/ directory"

# Create structure for models bucket
aws s3 cp ./empty.tmp "s3://$MODELS_BUCKET/complexity-models/model-artifacts/empty.tmp"
echo "Created complexity-models/model-artifacts/ directory"

aws s3 cp ./empty.tmp "s3://$MODELS_BUCKET/complexity-models/metrics/empty.tmp"
echo "Created complexity-models/metrics/ directory"

aws s3 cp ./empty.tmp "s3://$MODELS_BUCKET/prediction-models/readmission/empty.tmp"
echo "Created prediction-models/readmission/ directory"

aws s3 cp ./empty.tmp "s3://$MODELS_BUCKET/prediction-models/mortality/empty.tmp"
echo "Created prediction-models/mortality/ directory"

aws s3 cp ./empty.tmp "s3://$MODELS_BUCKET/prediction-models/utilization/empty.tmp"
echo "Created prediction-models/utilization/ directory"

aws s3 cp ./empty.tmp "s3://$MODELS_BUCKET/feature-importance/empty.tmp"
echo "Created feature-importance/ directory"

# Remove temporary file
rm empty.tmp

# Transfer processed data files
echo "Transferring processed data files..."

# Patient cohorts data
if [ -f "$PROCESSED_DIR/patient_cohort.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/patient_cohort.csv" "s3://$PROCESSED_BUCKET/patient-cohorts/"
  echo "Transferred patient_cohort.csv"
fi

if [ -f "$PROCESSED_DIR/patients_processed.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/patients_processed.csv" "s3://$PROCESSED_BUCKET/patient-cohorts/"
  echo "Transferred patients_processed.csv"
fi

# Clinical features data
if [ -f "$PROCESSED_DIR/patients_with_clinical.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/patients_with_clinical.csv" "s3://$PROCESSED_BUCKET/clinical-features/"
  echo "Transferred patients_with_clinical.csv"
fi

# Medications data
if [ -f "$PROCESSED_DIR/patients_with_medications.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/patients_with_medications.csv" "s3://$PROCESSED_BUCKET/medications/"
  echo "Transferred patients_with_medications.csv"
fi

if [ -f "$PROCESSED_DIR/medication_counts.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/medication_counts.csv" "s3://$PROCESSED_BUCKET/medications/"
  echo "Transferred medication_counts.csv"
fi

if [ -f "$PROCESSED_DIR/unique_medications.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/unique_medications.csv" "s3://$PROCESSED_BUCKET/medications/"
  echo "Transferred unique_medications.csv"
fi

# Diagnoses data
if [ -f "$PROCESSED_DIR/patients_with_conditions.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/patients_with_conditions.csv" "s3://$PROCESSED_BUCKET/diagnoses/"
  echo "Transferred patients_with_conditions.csv"
fi

if [ -f "$PROCESSED_DIR/diagnoses_with_conditions.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/diagnoses_with_conditions.csv" "s3://$PROCESSED_BUCKET/diagnoses/"
  echo "Transferred diagnoses_with_conditions.csv"
fi

# Utilization data
if [ -f "$PROCESSED_DIR/admissions_processed.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/admissions_processed.csv" "s3://$PROCESSED_BUCKET/utilization/"
  echo "Transferred admissions_processed.csv"
fi

if [ -f "$PROCESSED_DIR/icustays_processed.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/icustays_processed.csv" "s3://$PROCESSED_BUCKET/utilization/"
  echo "Transferred icustays_processed.csv"
fi

if [ -f "$PROCESSED_DIR/services_processed.csv" ]; then
  aws s3 cp "$PROCESSED_DIR/services_processed.csv" "s3://$PROCESSED_BUCKET/utilization/"
  echo "Transferred services_processed.csv"
fi

# Lab results - if any specific lab files are missing from your list
# (none identified in your file structure but leaving as a placeholder)

# Transfer model files
echo "Transferring model files..."

# Complexity models
if [ -f "$MODELS_DIR/patients_with_complexity.csv" ]; then
  aws s3 cp "$MODELS_DIR/patients_with_complexity.csv" "s3://$MODELS_BUCKET/complexity-models/"
  echo "Transferred patients_with_complexity.csv"
fi

if [ -f "$MODELS_DIR/readmission_model.joblib" ]; then
  aws s3 cp "$MODELS_DIR/readmission_model.joblib" "s3://$MODELS_BUCKET/complexity-models/model-artifacts/"
  echo "Transferred readmission_model.joblib"
fi

if [ -f "$MODELS_DIR/model_metrics.csv" ]; then
  aws s3 cp "$MODELS_DIR/model_metrics.csv" "s3://$MODELS_BUCKET/complexity-models/metrics/"
  echo "Transferred model_metrics.csv"
fi

# Prediction models - Readmission models
# Since we put the readmission model in the complexity-models directory, 
# this section might be empty or have additional readmission models

# Prediction models - Mortality models
if [ -f "$MODELS_DIR/mortality_model.joblib" ]; then
  aws s3 cp "$MODELS_DIR/mortality_model.joblib" "s3://$MODELS_BUCKET/prediction-models/mortality/"
  echo "Transferred mortality_model.joblib"
fi

if [ -f "$MODELS_DIR/mortality_feature_importance.csv" ]; then
  aws s3 cp "$MODELS_DIR/mortality_feature_importance.csv" "s3://$MODELS_BUCKET/prediction-models/mortality/"
  echo "Transferred mortality_feature_importance.csv"
fi

if [ -f "$MODELS_DIR/mortality_interventions.csv" ]; then
  aws s3 cp "$MODELS_DIR/mortality_interventions.csv" "s3://$MODELS_BUCKET/prediction-models/mortality/"
  echo "Transferred mortality_interventions.csv"
fi

# Prediction models - Utilization models
# ICU Stay models
if [ -f "$MODELS_DIR/extended_icu_stay_model.joblib" ]; then
  aws s3 cp "$MODELS_DIR/extended_icu_stay_model.joblib" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred extended_icu_stay_model.joblib"
fi

if [ -f "$MODELS_DIR/extended_icu_stay_feature_importance.csv" ]; then
  aws s3 cp "$MODELS_DIR/extended_icu_stay_feature_importance.csv" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred extended_icu_stay_feature_importance.csv"
fi

if [ -f "$MODELS_DIR/extended_icu_stay_interventions.csv" ]; then
  aws s3 cp "$MODELS_DIR/extended_icu_stay_interventions.csv" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred extended_icu_stay_interventions.csv"
fi

# High Utilizer models
if [ -f "$MODELS_DIR/high_utilizer_model.joblib" ]; then
  aws s3 cp "$MODELS_DIR/high_utilizer_model.joblib" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred high_utilizer_model.joblib"
fi

if [ -f "$MODELS_DIR/high_utilizer_feature_importance.csv" ]; then
  aws s3 cp "$MODELS_DIR/high_utilizer_feature_importance.csv" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred high_utilizer_feature_importance.csv"
fi

if [ -f "$MODELS_DIR/high_utilizer_interventions.csv" ]; then
  aws s3 cp "$MODELS_DIR/high_utilizer_interventions.csv" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred high_utilizer_interventions.csv"
fi

# Emergency Utilizer models
if [ -f "$MODELS_DIR/emergency_utilizer_model.joblib" ]; then
  aws s3 cp "$MODELS_DIR/emergency_utilizer_model.joblib" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred emergency_utilizer_model.joblib"
fi

if [ -f "$MODELS_DIR/emergency_utilizer_feature_importance.csv" ]; then
  aws s3 cp "$MODELS_DIR/emergency_utilizer_feature_importance.csv" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred emergency_utilizer_feature_importance.csv"
fi

if [ -f "$MODELS_DIR/emergency_utilizer_interventions.csv" ]; then
  aws s3 cp "$MODELS_DIR/emergency_utilizer_interventions.csv" "s3://$MODELS_BUCKET/prediction-models/utilization/"
  echo "Transferred emergency_utilizer_interventions.csv"
fi

# Feature importance
if [ -f "$MODELS_DIR/feature_importance.csv" ]; then
  aws s3 cp "$MODELS_DIR/feature_importance.csv" "s3://$MODELS_BUCKET/feature-importance/"
  echo "Transferred feature_importance.csv"
fi

if [ -f "$MODELS_DIR/model_summary.csv" ]; then
  aws s3 cp "$MODELS_DIR/model_summary.csv" "s3://$MODELS_BUCKET/feature-importance/"
  echo "Transferred model_summary.csv"
fi

# Verify transfer by listing bucket contents
echo "Verifying transfers..."
echo "Processed data bucket contents:"
aws s3 ls "s3://$PROCESSED_BUCKET/" --recursive | wc -l

echo "Models bucket contents:"
aws s3 ls "s3://$MODELS_BUCKET/" --recursive | wc -l

echo "Transfer process completed at $(date)"
