# postprocess

scripts to run https://github.com/esheldon/pizza-patches

adapted from https://github.com/beckermr/des-y6-analysis/tree/main/2023_12_21_v6cuts_hdf5cat

## usage

```
bash postprocess/step_00_make_flist.sh -c configs/fiducial.yaml -s plus
bash postprocess/step_01_make_uids.sh -c configs/fiducial.yaml -s plus -n 1
bash postprocess/step_02_make_cuts.sh -c configs/fiducial.yaml -s plus
bash postprocess/step_03_make_hdf5.sh -c configs/fiducial.yaml -s plus
```
