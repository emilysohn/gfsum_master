#Define Cycle to process,format must be 'MMDD' (as a string in quotes)
export PYCYCLE='0716'

#Define all variables to process
#export PYARG="m01s00i002" #u winds
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s00i003" #v winds
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
export PYARG="m01s00i004" #Theta (air)
sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s00i010" #q (specific humidity)
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s00i150" #w winds
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s00i254" #Liquid Water Content
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s00i408" #Air Pressure
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s00i266" #tcdc
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s16i202" #HGT
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh

#export PYARG="m01s03i073" #Height of BL
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s05i226" #Total Precipitation Amount
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s16i256" #relative humidity
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s09i203" #CF low
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s09i204" #CF med
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s09i205" #CF high
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh

#export PYARG="m01s16i202" #Geopotential Height
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
#export PYARG="m01s16i222" #Air Pressure at mean sea level
#sbatch -p RM-shared -n 20 -t 120 --mail-type=ALL --export=ALL,PYARG,PYCYCLE /ocean/projects/atm200005p/esohn1/gfsum_master/um_pipeline/download/python_workflow.sh
