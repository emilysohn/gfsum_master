gfsum_master – GFS and UM Weather Analysis Toolkit
A modular pipeline to process, visualize, and compare GFS forecast data and Unified Model (UM) actual data for the HALO-South field campaign. This package includes automated download scripts, standardized plotting utilities, and MP4 generation.

gfsum_master/
├── gfs_actual_pipeline/
│   ├── config.yaml #only for GFS pipelines
│   ├── download/ #this is different for UM pipeline, scripts from Eric
│   │   ├── download.py
│   │   ├── convert.py
│   │   └── run_download.slurm
│   ├── plotting/
│   │   ├── plot_driver.py
│   │   ├── utils.py
│   │   ├── color_config.py
│   │   └── ├── special/ #standalone scripts not covered by the standard pipeline
│   │       ├──tcdc_pres.py
│   │       └── rgb_tcdc.py
│   ├── stats/
│   │   ├── cdc_stats.py 
        ├── hpbl_stats.py
        ├── spfh_stats.py
        ├── tmp_stats.py
        ├── plot_cdc_stats.py 
        ├── plot_hpbl_stats.py
        ├── plot_spfh_stats.py
        └── plot_tmp_stats.py
│   └── scripts/
        └── run_plot_driver_array.slurm
├── gfs_forecasted_pipeline/
│   └── (same structure)
├── um_pipeline/
│   └── (same structure)
├── scripts/
│   ├── compare_gfs_um.py
│   └── make_mp4s.py
├── data/
│   ├── gfs_actual/
│   ├── gfs_forecasted/
│   └── um/
├── plots/
│   ├── gfs_actual/
│   ├── gfs_forecasted/
│   ├── um/
│   └── comparison/
├── mp4s/
│   ├── gfs_actual/
│   ├── gfs_forecasted/
│   ├── um/
│   └── comparison/
└── stats/
    ├── gfs_actual/
    ├── gfs_forecasted/
    └── um/


Modular Pipeline Design
Separate pipelines for GFS actual, GFS forecasted, and UM data.

Each pipeline contains:
download/ – GRIB or PP file retrieval + conversion to NetCDF
plotting/ – Consistent drivers for 2D maps and vertical slices
stats/ – Scripts to compute daily statistics (e.g., mean TMP, min/max SPFH)

All pipelines use shared utilities and configurations to maintain consistency.

Configuration
  The GFS pipelines have a config.yaml file that defines:
  - Forecast hours, date ranges, and step size
  - Input/output paths for raw and processed data
  - Variables and levels to extract

  This allows for customization of NetCDF files that are downloaded from GFS data
  Modify this file to adjust your experiment or analysis setup.

Plotting Script
  plot_driver.py
  - Core plotting script for shaded variable + optional contour + wind quivers.
  - Takes arguments from CLI or run_plot_driver_array.slurm using:
  python -m gfs_actual_pipeline.plotting.plot_driver

Terminal Plotting Commands
  Standard Use (GFS or UM)
  Run from the repository root(cd gfsum_master):

  export MAIN_VAR="SPFH" # variable you would like to plot
  export MAIN_LEVEL="1000mb" # pressure level
  export CONTOUR_VAR="HGT" # contour, or you can just say None
  export QUIVER=False # True or False depending on if you want wind quivers
  python -m {pipeline}.plotting.plot_driver 

  Notes:
  If the variable is a single-level field, pass:
  "surface" → for variables like HPBL, MSLET, PRES
  "column" → for integrated fields like LWC (liquid water content) - this only applies for UM data 

SLURM Batch Plotting
  Use sbatch run_plot_driver_array.slurm for batch plotting:

  run_plot_driver_array.slurm has the following code:
  #!/bin/bash
  #SBATCH --array=0-1 # edit the size of the array depending on how many different plots you want - so if you have 3 types, you would put 0-2. 

  CONFIGS=(
  "POT 500mb HGT False"
  "RH 850mb HGT True"
    ...
  )

  CONFIG="${CONFIGS[$SLURM_ARRAY_TASK_ID]}"
  read MAIN_VAR MAIN_LEVEL CONTOUR_VAR QUIVER <<< "$CONFIG"
  export MAIN_VAR MAIN_LEVEL CONTOUR_VAR QUIVER

  python -m {pipeline}.plotting.plot_driver #submits batch jobs using the plot driver and the inputs from configs


Utility Functions Script
  utils.py
  Includes helper functions such as:
  setup_map, format_title, plot_quivers, and load_main_variable
  - these help with standardizing all plots and making sure the logic for plotting
  is consistent

Color Configuration File
  color_config.py
  Contains:
  - Custom color bounds, colormaps, units, and labels for each variable used
  - Optional contour styling based on variable pairings

Statistics Scripts
  Scripts in the stats/ folder compute daily summaries such as:
  -Mean, max, min specific humidity (SPFH)
  -Typical boundary layer height (HPBL)
  -Daily average temperature (TMP)
  -Dominant cloud types (TCDC, LCDC, MCDC, HCDC)
  Output is saved as CSVs and summary plots.

MP4 Animation
  Run make_mp4s.py, which loops recursively over the input directory to convert  PNGs into animations over a series of timestamps:
  cd /ocean/projects/atm200005p/esohn1/gfsum_master/scripts
  python make_mp4s.py

Comparing GFS vs UM
  To generate side-by-side comparisons:
  python scripts/compare_gfs_um.py
  - Searches for matching timestamps and overlays outputs from both models.
  - uses GFS actual plots and UM plots for simplicity.


Requirements
conda create -n gfs_env python=3.10
conda activate gfs_env
pip install -r requirements.txt

Dependencies include:
xarray, netCDF4, matplotlib, cartopy, scipy, pandas, ffmpeg-python



Notes
- Data is sourced from AWS GFS archives and UM PP files provided by collaborators.
- All plots and stats focus on the HALO-South campaign region (Southern Ocean).
- Designed for use on HPC environments (e.g., Bridges-2) with SLURM scheduling.

