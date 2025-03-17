# In scripts/run_readmission.sh
#!/bin/bash
#SBATCH --job-name=readmission_model
#SBATCH --time=8:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --output=outputs/readmission/logs/%j.out

# Load modules and activate environment
module load conda
conda activate vitalschedule

# Run the readmission pipeline
python code/readmission/run_pipeline.py
