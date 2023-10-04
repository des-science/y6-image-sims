# scripts

`test.sh` -- quickly test a config
```
bash scripts/test.sh -c configs/grid-bright/config.yaml -t DES2205+0126 -s $RANDOM
```

`run.sh` -- run a full simulation pair
```
sbatch scripts/run.sh -c configs/grid-bright/config.yaml -t DES2205+0126 -s $RANDOM
```

`run_all.sh` -- run a full simulation pair for all tiles
```
bash scripts/run_all.sh -c configs/grid-bright/config.yaml
```
