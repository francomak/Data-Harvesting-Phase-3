#!/bin/bash
# This helps prevent errors in later steps if an earlier one fails
set -Eeuo pipefail

# ------- Prerequisites ---------------------------------------

## 1. Ensure language models have been created or is available
## 2. Update config file found at: conformer_ctc2/scripts/main_config.yaml

# ------- Configuration Section ---------------------------------------

# Define input directory paths
CONFORMER_DIR="/development/models/Kaldi_2/conformer_ctc2"  # Path to model directory

# ------- Script Execution Section ------------------------------------
cd $CONFORMER_DIR

echo "Running Lhotse Data Preparation"
python scripts/Lhotse_data_preparation.py  # Run this for feature extraction

echo "Running train.py"
python scripts/train.py  # Main training script

exit 0
