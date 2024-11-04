# DES Y6 Image Sims

utilities, scripts, and configs for running [eastlake](https://github.com/des-science/eastlake) for the DES Y6 image simulations

## paths to input data at NERSC

 - `MEDS_DIR`/`IMSIM_DATA`:  `/global/cfs/cdirs/desbalro/des-pizza-slices-y6/`
 - star catalogs: `/global/cfs/projectdirs/des/atong/y6kp-shear/starsim/catalogs/merged_y6/`
 - input cosmos catalog: `/global/cfs/cdirs/des/y3-image-sims/input_cosmos_v4.fits`

The final data products are available in the desbalro space:
- `/global/cfs/cdirs/desbalro/input_cosmos_v4_montara_simcat_v7_seed42.fits` -- cosmos with bright end resampling for deep field image sims
- `/global/cfs/cdirs/desbalro/cosmos_simcat/` -- per-tile cosmos catalogs with bright end resampling
- `/global/cfs/cdirs/desbalro/starsim/catalogs/merged_y6/` -- star sim catalogs

## paths to output data at NERSC

### fiducial (400 tiles)

- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=-0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=0.0__zhigh=0.3/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=0.3__zhigh=0.6/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=0.6__zhigh=0.9/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=0.9__zhigh=1.2/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=1.2__zhigh=1.5/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=1.5__zhigh=1.8/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=1.8__zhigh=2.1/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=2.1__zhigh=2.4/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=2.4__zhigh=2.7/metadetect_cutsv6_all.h5`
- `/global/cfs/cdirs/des/y6-image-sims/fiducial-400/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=2.7__zhigh=6.0/metadetect_cutsv6_all.h5`

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
