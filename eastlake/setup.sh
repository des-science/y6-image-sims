#!/bin/bash

module load conda
conda activate /global/common/software/des/mambaforge/envs/des-y6
# conda activate /global/common/software/des/mambaforge/envs/des-y6-imsims-dev

# export IMSIM_DATA=/global/cfs/cdirs/des/y6-image-sims
# export MEDS_DIR=/global/cfs/cdirs/des/y6-image-sims
export IMSIM_DATA=/global/cfs/cdirs/desbalro
export MEDS_DIR=/global/cfs/cdirs/desbalro

# export PYTHONPATH=~/software/galsim_extra:$PYTHONPATH
# export PYTHONPATH=~/software/montara:$PYTHONPATH
# export PYTHONPATH=~/software/eastlake:$PYTHONPATH

# see https://joblib.readthedocs.io/en/latest/parallel.html#avoiding-over-subscription-of-cpu-resources
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
