#!/bin/bash
module load anaconda3
conda activate iris-env
python /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/makenetcdf.py $PYARG $PYCYCLE
