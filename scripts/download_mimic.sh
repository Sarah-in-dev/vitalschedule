# In scripts/download_mimic.sh
#!/bin/bash

# Set target directory
MIMIC_DIR="$HOME/vitalschedule/data/raw/mimic-iv"
mkdir -p $MIMIC_DIR

# Download MIMIC-IV data
cd $MIMIC_DIR
wget -r -N -c -np --user sarahindev --ask-password https://physionet.org/files/mimiciv/3.1/

# Once downloaded, organize files
mv physionet.org/files/mimiciv/3.1/* .
rm -rf physionet.org

echo "MIMIC-IV download complete."
