#!/bin/bash
#SBATCH --job-name=gfs_actual_plot_driver
#SBATCH --output=/ocean/projects/atm200005p/esohn1/logs/gfs_actual_plot_driver_%A_%a.out
#SBATCH --error=/ocean/projects/atm200005p/esohn1/logs/gfs_actual_plot_driver_%A_%a.err
#SBATCH --array=0-21
#SBATCH --time=00:30:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1

module purge
source /jet/home/esohn1/miniconda3/etc/profile.d/conda.sh
conda activate gfs_env

cd /ocean/projects/atm200005p/esohn1/gfsum_master

# === Define the list of configs ===
CONFIGS=(
  "POT 300mb HGT False"
  "POT 500mb HGT False"
  "POT 700mb HGT False"
  "POT 850mb HGT False"
  "RH 300mb HGT True"
  "RH 500mb HGT True"
  "RH 700mb HGT True"
  "RH 850mb HGT True"
  "SPFH 1000mb None False"
  "SPFH 300mb None False"
  "SPFH 500mb None False"
  "SPFH 700mb None False"
  "SPFH 850mb None False"
  "SPFH 925mb None False"
  "UGRD 300mb HGT True"
  "UGRD 500mb HGT True"
  "UGRD 700mb HGT True"
  "UGRD 850mb HGT True"
  "TMP 300mb HGT True"
  "TMP 500mb HGT True"
  "TMP 700mb HGT True"
  "TMP 850mb HGT True"
)

# === Parse the config for this array task ===
CONFIG="${CONFIGS[$SLURM_ARRAY_TASK_ID]}"
read MAIN_VAR MAIN_LEVEL CONTOUR_VAR QUIVER <<< "$CONFIG"

# === Export as environment variables ===
export MAIN_VAR MAIN_LEVEL CONTOUR_VAR QUIVER

# === Run the plot driver ===
python -m gfs_actual_pipeline.plotting.plot_driver
