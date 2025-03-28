#!/bin/bash
#SBATCH --job-name=test_job
#SBATCH --time=5:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --output=test_job_%j.out
#SBATCH --error=test_job_%j.err

# Print current directory
pwd

# Print environment information
echo "User: $USER"
echo "Host: $HOSTNAME"
echo "Date: $(date)"

# Create a test directory
mkdir -p test_output

# List the current directory contents
ls -la

# Sleep for a minute
sleep 60

echo "Job completed successfully"
