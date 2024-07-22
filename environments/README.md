# environments

## v3 and above conda environment files w/ conda-lock

For these envs, the `*.yaml` files are the abstract requirements for the environment. To actually make the environment,
use need to use `conda-lock` with the `*.lock` files.

To generate the lock files, use the following command:

```bash
python lock-des-envs.py v3/<name of env>.yaml
```

To create an environment from a lock file, use this command:

```bash
conda-lock install -n <name of env> <path to lock file>
```

The name of the environment can be different than that of the lockfile.

## v2 conda environment files

These files were generated via `conda list --explicit` on the envs at NERSC on 2024-07-19.

To create the environment, run

```bash
conda create --name <env> --file <this file>
```

## v1 conda environment files

note: an older version of numpy was required for running fitvd as done by desdm; specifically,

```yaml
name: des-y6-fitvd
channels:
- conda-forge
- default
dependencies:
- des-fitvd
- shredx
- numpy=1.23.5
```
