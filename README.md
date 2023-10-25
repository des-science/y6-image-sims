# DES Y6 Image Sims

utilities, scripts, and configs for running [eastlake](https://github.com/des-science/eastlake) for the DES Y6 image simulations

## tiles

`run-query.sh` -- query easyaccess for tiles
```
bash tiles/run-query.sh -f tiles-y6.txt
```

## meds

`run-download.sh` -- download meds for tiles via rsync
```
bash meds/run-download.sh -f tiles-y6.txt
```

## eastlake

`test.sh` -- quickly test a config
```
bash eastlake/test.sh -c configs/grid-bright/config.yaml -t DES2205+0126 -s $RANDOM
```

`run.sh` -- run a full simulation pair
```
sbatch eastlake/run.sh -c configs/grid-bright/config.yaml -t DES2205+0126 -s $RANDOM
```

`run-all.sh` -- run a full simulation pair for all tiles
```
bash eastlake/run-all.sh -c configs/grid-bright/config.yaml -f tiles-y6.txt -s $RANDOM
```

## analysis

`compute_bias.py` -- compute multiplicative and additive shear bias for output sims
```
python analysis/compute_bias.py $SCRATCH/y6-image-sims/grid-bright --seed $RANDOM
```
