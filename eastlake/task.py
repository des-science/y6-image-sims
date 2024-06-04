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
        help="output directory [path]",
    )

    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        required=False,
        help="verbosity [int; 1]",
    )
    parser.add_argument(
        "--attempt_resume",
        action="store_true",
        help="flag to attempt resumption of previous run",
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

    # parser.add_argument(
    #     "--shear",
    #     type=float,
    #     nargs=2,
    #     required=False,
    #     default=None,
    #     help="shear to apply (g1, g2) [float; None]",
    # )
    # parser.add_argument(
    #     "--redshift",
    #     type=float,
    #     nargs=2,
    #     required=False,
    #     default=None,
    #     help="redshift range in which to apply shear [float; None]",
    # )

    shear_group = parser.add_argument_group("shear")
    shear_group.add_argument(
        "--shear_slice",
        action="store_true",
        help="apply shear in redshift slice",
    )
    shear_group.add_argument(
        "--g1",
        type=float,
        required=False,
        default=0.,
        help="shear along g1 axis [float; 0.]",
    )
    shear_group.add_argument(
        "--g2",
        type=float,
        required=False,
        default=0.,
        help="shear along g2 axis [float; 0.]",
    )
    shear_group.add_argument(
        "--g1_slice",
        type=float,
        required=False,
        default=0.,
        help="shear along g1 axis inside of redshift slice [float; 0.]",
    )
    shear_group.add_argument(
        "--g2_slice",
        type=float,
        required=False,
        default=0.,
        help="shear along g2 axis inside of redshift slice [float; 0.]",
    )
    shear_group.add_argument(
        "--g1_other",
        type=float,
        required=False,
        default=0.,
        help="shear along g1 axis outside of redshift slice [float; 0.]",
    )
    shear_group.add_argument(
        "--g2_other",
        type=float,
        required=False,
        default=0.,
        help="shear along g2 axis outside of redshift slice [float; 0.]",
    )
    shear_group.add_argument(
        "--zlow",
        type=float,
        required=False,
        default=0.,
        help="lower limit of redshift slice which to apply shear [float; 0.]",
    )
    shear_group.add_argument(
        "--zhigh",
        type=float,
        required=False,
        default=3.,
        help="upper limit of redshift slice which to apply shear [float; 3.]",
    )

    return parser.parse_args()


def main():
    args = get_args()

    config_path = Path(args.config)
    config_name = config_path.with_suffix("").name

    tile_name = args.tile

    print(f"config: {config_name}")
    print(f"tile: {tile_name}")

    shear_slice = args.shear_slice
    if not shear_slice:
        g1 = args.g1
        g2 = args.g2
    else:
        g1_slice = args.g1_slice
        g2_slice = args.g2_slice
        g1_other = args.g1_other
        g2_other = args.g2_other
        zlow = args.zlow
        zhigh = args.zhigh
        if (zlow < 0) or (zlow >= zhigh):
            raise ValueError(f"Invalid redshift range")


    seed = args.seed
    if seed < 0:
        raise ValueError(f"Invalid seed")
    print(f"seed: {seed}")

    output_path = Path(args.output)

    print(f"output: {output_path}")
    print(f"config: {config_path}")

    process_args = [
        "run-eastlake-sim",
        "--verbosity", str(args.verbosity),
        "--seed", str(seed),
        config_path,
        output_path,
        f"output.tilename={tile_name}",
        f"eval_variables.seastlake_seed={seed}",
    ]

    if not shear_slice:
        process_args.append(f"stamp.shear.g1={g1}")
        process_args.append(f"stamp.shear.g2={g2}")
    else:
        process_args.append(f"stamp.shear.g1_slice={g1_slice}")
        process_args.append(f"stamp.shear.g2_slice={g2_slice}")
        process_args.append(f"stamp.shear.g1_other={g1_other}")
        process_args.append(f"stamp.shear.g2_other={g2_other}")
        process_args.append(f"stamp.shear.zlow={zlow}")
        process_args.append(f"stamp.shear.zhigh={zhigh}")


    if args.test:
        process_args.append(f"pizza_cutter.n_jobs=8")
        process_args.append(f"metadetect.n_jobs=8")
        process_args.append(f"output.nproc=1")
        process_args.append(f"output.n_se_test=1")
        process_args.append(f"output.bands=r")
        process_args.append(f"pipeline.steps=[galsim_montara, pizza_cutter, metadetect]")

    if args.attempt_resume:
        job_record = output_path / "job_record.pkl"
        job_resumable = job_record.is_file()
        if job_resumable:
            print(f"job record found: {job_record}")
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

