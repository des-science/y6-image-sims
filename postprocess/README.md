# postprocess

scripts to run https://github.com/esheldon/pizza-patches

adapted from https://github.com/beckermr/des-y6-analysis/tree/main/2023_12_21_v6cuts_hdf5cat

## usage

`step_00_make_flist.sh` -- make the list of input metadetect catalog files
```
bash postprocess/step_00_make_flist.sh -c $config -s $shear
```

`step_01_make_uids.sh` -- make the mapping of uids across input files
```
bash postprocess/step_01_make_uids.sh -c $config -s $shear
```

`step_02_make_cuts.sh` -- make files with metadetect cuts
```
bash postprocess/step_02_make_cuts.sh -c $config -s $shear
```

`step_03_make_hdf5.sh` -- make concatenated hdf5 catalog file
```
bash postprocess/step_03_make_hdf5.sh -c $config -s $shear
```

`run-all.sh` -- run postprocess steps to apply cuts and create HDF5 catalog
```
bash postprocess/run-all.sh -c $config -s $shear
```
