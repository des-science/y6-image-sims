# eastlake

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
