#!/bin/bash

module load texlive
module load conda
conda activate /global/common/software/des/mambaforge/envs/des-y6

# for downloading meds for desdm
export DES_RSYNC_PASSFILE=/global/cfs/cdirs/des/y6-image-sims/rsync_pass-smau.txt
export DESREMOTE_RSYNC=smau@desar2.cosmology.illinois.edu::ALLDESFiles/new_archive/desarchive/

# used for meds download, eastlake, etc.
export IMSIM_DATA=/global/cfs/cdirs/desbalro
export MEDS_DIR=/global/cfs/cdirs/desbalro
export FITVD_ENV=/global/common/software/des/mambaforge/envs/des-y6-fitvd

# see https://joblib.readthedocs.io/en/latest/parallel.html#avoiding-over-subscription-of-cpu-resources
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
