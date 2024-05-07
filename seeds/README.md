# seeds

`run.sh` -- generate list of seeds
```
bash seeds/run.sh -f seeds-y6.txt
```

`merge.sh` -- merge seeds and tiles into an arguments file
```
bash seeds/merge.sh -t tiles-y6.txt -s seeds-y6.txt
```
note the output `args-y6.txt` is committed to this repository.
