# measure

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
