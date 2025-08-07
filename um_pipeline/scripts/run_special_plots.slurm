#!/bin/bash
#SBATCH --job-name=um_specials
#SBATCH --time=01:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/um_specials.out
#SBATCH --error=logs/um_specials.err

module purge
source /jet/home/esohn1/miniconda3/etc/profile.d/conda.sh
conda activate gfs_env

cd /ocean/projects/atm200005p/esohn1/gfsum_master

# Run RGB cloud cover + pressure
python -m um_pipeline.plotting.special.rgb_tcdc

# Run cloud level plots with pressure contours
python -m um_pipeline.plotting.special.cdc_pres

#Make mp4s of everything
python scripts/make_mp4s.py
