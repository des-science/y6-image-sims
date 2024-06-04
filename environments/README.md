# environments

conda environment files

note: an older version of numpy was required for running fitvd as done by desdm; specifically,
```
name: des-y6-fitvd
channels:
- conda-forge
- default
dependencies:
- des-fitvd
- shredx
- numpy=1.23.5
```
