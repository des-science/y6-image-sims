# eastlake

`task.py` -- run a single eastlake simulation
```
usage: task.py [-h] [--verbosity VERBOSITY] [--attempt_resume] [--test] [--dry-run] [--shear_slice] [--g1 G1] [--g2 G2] [--g1_slice G1_SLICE] [--g2_slice G2_SLICE] [--g1_other G1_OTHER] [--g2_other G2_OTHER] [--zlow ZLOW] [--zhigh ZHIGH]
               config tile seed output

positional arguments:
  config                configuration file [yaml]
  tile                  DES tile [yaml]
  seed                  RNG seed [int]
  output                output directory [path]

options:
  -h, --help            show this help message and exit
  --verbosity VERBOSITY
                        verbosity [int; 1]
  --attempt_resume      attempt resumption from job record
  --test                run a smaller scale test
  --dry-run             do a dry run without running anything

shear:
  --shear_slice         apply shear in redshift slice
  --g1 G1               shear along g1 axis [float; 0.]
  --g2 G2               shear along g2 axis [float; 0.]
  --g1_slice G1_SLICE   shear along g1 axis inside of redshift slice [float; 0.]
  --g2_slice G2_SLICE   shear along g2 axis inside of redshift slice [float; 0.]
  --g1_other G1_OTHER   shear along g1 axis outside of redshift slice [float; 0.]
  --g2_other G2_OTHER   shear along g2 axis outside of redshift slice [float; 0.]
  --zlow ZLOW           lower limit of redshift slice which to apply shear [float; 0.]
  --zhigh ZHIGH         upper limit of redshift slice which to apply shear [float; 3.]

```

`array-task.sh` -- wrapper for task to be submitted via slurm job array
```
sbatch eastlake/array-task.sh -c $config -f args-y6.txt
```

`submit-array.sh` -- submit multiple tiles via job array (e.g., for tiles 1--100)
```
bash eastlake/submit-array.sh -c configs/grid-bright.yaml -f args-y6.txt -j 1-100
```
