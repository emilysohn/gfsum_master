#!/bin/bash
#SBATCH --job-name=um_all
#SBATCH --time=00:02:00
#SBATCH --mem=1G
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/um_all.out
#SBATCH --error=logs/um_all.err

# Submit the first job and store its job ID
PLOT_JOB_ID=$(sbatch --parsable run_plot_driver_array.slurm)

# Submit the second job to run only after the first job finishes successfully
sbatch --dependency=afterok:$PLOT_JOB_ID run_special_plots.slurm
