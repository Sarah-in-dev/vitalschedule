#!/bin/bash
#SBATCH --job-name=readmission_prediction
#SBATCH --time=48:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=your.email@ufl.edu
#SBATCH --output=readmission_job_%j.out

# Load required modules
module load conda

# Activate your environment
conda activate vitalschedule

# Navigate to project directory
cd /home/sdavidson2/vitalschedule

# Run the pipeline
python code/readmission/run_pipeline.py
