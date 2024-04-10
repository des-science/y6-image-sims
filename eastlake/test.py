#!/usr/bin/env python

import argparse
# import hashlib
import os
from pathlib import Path
import subprocess


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "config",
        type=str,
        help="configuration file [yaml]",
    )
    parser.add_argument(
        "tile",
        type=str,
        help="DES tile [yaml]",
    )
    parser.add_argument(
        "seed",
        type=int,
        help="RNG seed [int]",
    )
    parser.add_argument(
        "output",
        type=str,
        help="top-level output directory [path]",
    )

    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        required=False,
        help="verbosity [int; 1]",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="flag to resume previous run",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="run a smaller scale test",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="do a dry run without running anything",
    )

    parser.add_argument(
        "--shear",
        type=float,
        nargs=2,
        required=False,
        default=None,
        help="shear to apply (g1, g2) [float; None]",
    )
    parser.add_argument(
        "--redshift",
        type=float,
        nargs=2,
        required=False,
        default=None,
        help="redshift range in which to apply shear [float; None]",
    )

    # shear_group = parser.add_argument_group("shear")
    # shear_group.add_argument(
    #     "--g1",
    #     type=float,
    #     required=False,
    #     default=0.,
    #     help="shear along g1 axis [float; 0.]",
    # )
    # shear_group.add_argument(
    #     "--g2",
    #     type=float,
    #     required=False,
    #     default=0.,
    #     help="shear along g2 axis [float; 0.]",
    # )

    # redshift_group = parser.add_argument_group("redshift")
    # redshift_group.add_argument(
    #     "--zmin",
    #     type=float,
    #     required=False,
    #     default=None,
    #     help="lower limit of redshift range in which to apply shear [float; None]",
    # )
    # redshift_group.add_argument(
    #     "--zmax",
    #     type=float,
    #     required=False,
    #     default=None,
    #     help="upper limit of redshift range in which to apply shear [float; None]",
    # )

    return parser.parse_args()


def main():
    args = get_args()

    config_path = Path(args.config)
    config_name = config_path.with_suffix("").name

    tile_name = args.tile

    print(f"config: {config_name}")
    print(f"tile: {tile_name}")

    if args.shear is not None:
        g1 = args.shear[0]
        g2 = args.shear[1]
    else:
        g1 = 0.00
        g2 = 0.00

    # if args.seed is not None:
    #     seed = args.seed
    # else:
    #     hash = hashlib.sha256()
    #     hash.update(config_name.encode("UTF-8"))
    #     hash.update(tile_name.encode("UTF-8"))

    #     seed = int(
    #         hash.hexdigest(),
    #         16
    #     ) & 0xFFFFFFFF

    seed = args.seed
    if seed < 0:
        raise ValueError(f"Invalid seed")
    print(f"seed: {seed}")

    # output_path = Path(
    #     os.environ.get("SCRATCH", ".")
    # ) / "y6-image-sims" / config_name / tile_name / str(seed)
    # output_path = Path(args.output) / config_name / tile_name / str(seed)
    output_path = Path(args.output)

    # if args.redshift is not None:
    #     zmin = args.redshift[0]
    #     zmax = args.redshift[1]
    #     if zmin >= zmax:
    #         raise ValueError(f"Invalid redshift range")

    #     output_path /= f"g1={g1:2.2f}_g2={g2:2.2f}_zmin={zmin:2.2f}_zmax={zmax:2.2f}"
    # if (args.zmin is not None) and (args.zmax is not None):
    #     zmin = args.zmin
    #     zmax = args.zmax
    #     if zmin >= zmax:
    #         raise ValueError(f"Invalid redshift range")
    #     output_path /= f"g1={g1:2.2f}_g2={g2:2.2f}_zmin={zmin:2.2f}_zmax={zmax:2.2f}"
    # else:
    #     output_path /= f"g1={g1:2.2f}_g2={g2:2.2f}"

    if args.redshift is not None:
        zmin = args.redshift[0]
        zmax = args.redshift[1]
        if zmin >= zmax:
            raise ValueError(f"Invalid redshift range")

        output_path /= f"g1={g1:2.2f}_g2={g2:2.2f}_zmin={zmin:2.2f}_zmax={zmax:2.2f}"
    else:
        output_path /= f"g1={g1:2.2f}_g2={g2:2.2f}"

    print(f"output: {output_path}")

    print(f"config: {config_path}")

    job_record = output_path / "job_record.pkl"
    job_resumable = job_record.is_file()
    if job_resumable:
        print(f"job record found: {job_record}")

    process_args = [
        "run-eastlake-sim",
        "--verbosity", str(args.verbosity),
        "--seed", str(seed),
        config_path,
        output_path,
        f"stamp.shear.g1={g1:2.2f}",
        f"stamp.shear.g2={g2:2.2f}",
        f"output.tilename={tile_name}",
    ]

    if args.test:
        process_args.append(f"pizza_cutter.n_jobs=8")
        process_args.append(f"metadetect.n_jobs=8")
        process_args.append(f"output.nproc=1")
        process_args.append(f"output.n_se_test=1")
        process_args.append(f"output.bands=r")
        process_args.append(f"pipeline.steps=[galsim_montara, pizza_cutter, metadetect]")

    if args.resume:
        if job_resumable:
            process_args.append("--resume")
        else:
            print(f"could not find job record; running from the top")

    if args.dry_run:
        process_args.insert(0, "echo")
    else:
        output_path.mkdir(parents=True, exist_ok=True)

    print(f"subprocess:", *process_args)
    print(f">>>>>>>>")

    finished = subprocess.run(process_args)

    print(f"<<<<<<<<")
    print(f"subprocess completed with status {finished.returncode}")


if __name__ == "__main__":
    main()

