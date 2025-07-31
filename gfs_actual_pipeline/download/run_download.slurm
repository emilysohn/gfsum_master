#!/bin/bash
#SBATCH --job-name=gfs_download
#SBATCH --output=/ocean/projects/atm200005p/esohn1/logs/download_%j.out
#SBATCH --error=/ocean/projects/atm200005p/esohn1/logs/download_%j.err
#SBATCH --time=01:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1

source ~/.bashrc
conda activate gfs_env

python /ocean/projects/atm200005p/esohn1/gfsum_master/gfs_actual_pipeline/download/download.py
python /ocean/projects/atm200005p/esohn1/gfsum_master/gfs_actual_pipeline/download/convert.py
