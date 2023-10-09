# DES Y6 Image Sims

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

## scripts

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
bash scripts/run_all.sh -c configs/grid-bright/config.yaml -f tiles-y6.txt
```
