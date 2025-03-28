#!/bin/bash
#SBATCH --job-name=vbc_pipeline
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32gb
#SBATCH --partition=hpg-default
#SBATCH --output=../logs/vbc_pipeline_%j.out
#SBATCH --error=../logs/vbc_pipeline_%j.err

# Print start time
echo "Job started at $(date)"
echo "Running on node: $HOSTNAME"

# Load modules
module load python

# Activate virtual environment
source ~/vitalschedule/bin/activate

# Set directories
MIMIC_DIR=~/vitalschedule/data/raw/mimic-iv
OUTPUT_DIR=~/vitalschedule/value_based/processed_data
MODELS_DIR=~/vitalschedule/value_based/models

# Create output directories
mkdir -p $OUTPUT_DIR
mkdir -p $MODELS_DIR
mkdir -p ~/vitalschedule/value_based/logs

# Check if directories exist
echo "Checking directories..."
echo "MIMIC_DIR: $(ls -la $MIMIC_DIR | wc -l) files"
echo "OUTPUT_DIR: $OUTPUT_DIR"
echo "MODELS_DIR: $MODELS_DIR"

# Step 1: Extract patient cohort and core features
echo "Processing patient data and core features..."
python ./process_patient_data.py \
  --mimic_dir $MIMIC_DIR \
  --output_dir $OUTPUT_DIR \
  --tables patients admissions icustays services

# Step 2: Extract and process diagnoses for chronic condition identification
echo "Processing diagnosis data..."
python ./process_diagnoses.py \
  --mimic_dir $MIMIC_DIR \
  --output_dir $OUTPUT_DIR \
  --patient_cohort $OUTPUT_DIR/patient_cohort.csv

# Step 3: Process medication data for polypharmacy analysis
echo "Processing medication data..."
# Note: Changed from process_medications.py to process_medication.py based on your file listing
python ./process_medication.py \
  --mimic_dir $MIMIC_DIR \
  --output_dir $OUTPUT_DIR \
  --patient_cohort $OUTPUT_DIR/patient_cohort.csv

# Step 4: Process laboratory and ICU data for clinical severity
echo "Processing lab and ICU data..."
python ./process_clinical_data.py \
  --mimic_dir $MIMIC_DIR \
  --output_dir $OUTPUT_DIR \
  --patient_cohort $OUTPUT_DIR/patient_cohort.csv

# Step 5: Build the complexity score model
echo "Building patient complexity model..."
python ./build_complexity_model.py \
  --data_dir $OUTPUT_DIR \
  --output_dir $MODELS_DIR

# Step 6: Event prediction model development
echo "Building event prediction models..."
python ./build_prediction_models.py \
  --data_dir $OUTPUT_DIR \
  --models_dir $MODELS_DIR

echo "Pipeline completed at $(date)"
