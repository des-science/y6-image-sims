# DES Y6 Image Sims

utilities, scripts, and configs for running [eastlake](https://github.com/des-science/eastlake) for the DES Y6 image simulations

## paths to data at NERSC

 - `MEDS_DIR`/`IMSIM_DATA`:  `/global/cfs/cdirs/desbalro/des-pizza-slices-y6/`
 - star catalogs: `/global/cfs/projectdirs/des/atong/y6kp-shear/starsim/catalogs/`
 - input cosmos catalog: `/global/cfs/cdirs/des/y3-image-sims/input_cosmos_v4.fits`

## tiles

`run-query.sh` -- query easyaccess for tiles
```
bash tiles/run-query.sh -f tiles-y6.txt
```
note the output `tiles-y6.txt` is committed to this repository.

## meds

`run-download.sh` -- download meds for tiles via rsync
```
bash meds/run-download.sh -f tiles-y6.txt
```

## seeds

`run.sh` -- generate list of seeds
```
bash seeds/run.sh -f seeds-y6.txt
```

`merge.sh` -- merge seeds and tiles into an arguments file
```
bash seeds/merge.sh -t tiles-y6.txt -s seeds-y6.txt
```
note the output `args-y6.txt` is committed to this repository.

## eastlake

`task.py` -- run a single eastlake simulation
```
python eastlake/task.py --verbosity 1 --resume --shear 0.02 0.00 $config $tile $seed ${output}/plus
```
note: use `--dry-run` to check the commands without running anything

`array-task.sh` -- wrapper for task to be submitted via slurm job array
```
sbatch eastlake/array-task.sh -c $config -f args-y6.txt
```

`submit-array.sh` -- submit multiple tiles via job array (e.g., for tiles 1--100)
```
bash eastlake/submit-array.sh -c configs/grid-bright.yaml -f args-y6.txt -j 1-100
```

## validate

scripts for making validate plots; e.g.,
`plot_color-color.py`
```
$ python validate/plot_mag.py --help
usage: plot_mag.py [-h] [--seed SEED] [--n_jobs N_JOBS] [--fast] imsim_dir

positional arguments:
  imsim_dir        Image simulation output directory

options:
  -h, --help       show this help message and exit
  --seed SEED      RNG seed [int]
  --n_jobs N_JOBS  Number of joblib jobs [int]
  --fast           whether to do a fast run
```

## measure

`compute_bias.py` -- compute multiplicative and additive shear bias for output sims
```
python measure/compute_bias.py $SCRATCH/y6-image-sims/grid-bright --seed $RANDOM
```

`run.sh` -- compute multiplicative and additive shear bias for output sims (via sbatch)
```
bash measure/run.sh -c configs/grid-bright.yaml -s $RANDOM -n 8
```

```
sbatch measure/run.sh -c configs/grid-bright.yaml -s $RANDOM -n 128
```
