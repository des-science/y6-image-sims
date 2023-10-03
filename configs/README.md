# configs

## scripts

`test.sh` -- quickly test a config
```
bash test.sh -c grid-bright/config.yaml -t DES2205+0126 -s $RANDOM
```

`run.sh` -- run a full simulation pair
```
sbatch run.sh -c grid-bright/config.yaml -t DES2205+0126 -s $RANDOM
```
