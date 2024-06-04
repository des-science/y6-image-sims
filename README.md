# DES Y6 Image Sims

utilities, scripts, and configs for running [eastlake](https://github.com/des-science/eastlake) for the DES Y6 image simulations

## paths to data at NERSC

 - `MEDS_DIR`/`IMSIM_DATA`:  `/global/cfs/cdirs/desbalro/des-pizza-slices-y6/`
 - star catalogs: `/global/cfs/projectdirs/des/atong/y6kp-shear/starsim/catalogs/`
 - input cosmos catalog: `/global/cfs/cdirs/des/y3-image-sims/input_cosmos_v4.fits`

## [environments](./environments/README.md)

configs for conda environments

## [tiles](./tiles/README.md)

scripts for querying lists of DES tiles via easyaccess

## [meds](./meds/README.md)

scripts for downloading meds for DES tiles via rsync

## [seeds](./seeds/README.md)

script for generating list of seeds for each tile

## [eastlake](./eastlake/README.md)

scripts for running image simulations with eastlake

## [campaigns](./campaigns/README.md)

scripts for image simulation campaigns

## [postprocess](./postprocess/README.md)

create a concatenated hdf5 file of the metadetect catalogs for the image simulations

## [validate](./validate/README.md)

scripts for making validation plots

## [measure](./measure/README.md)

scripts for measuring multiplicative and additive bias of image simulations
