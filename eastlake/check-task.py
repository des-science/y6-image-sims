#!/usr/bin/env python

import argparse
import os
import pickle
import sys


# steps = record["step_names"]
# # ['galsim_montara', 'coadd_nwgint', 'swarp', 'src_extractor', 'desdm_meds', 'pizza_cutter', 'metadetect', 'fitvd', 'delete_images', 'delete_sources']
# completed_steps = record["completed_step_names"]
# # [('galsim_montara', 0), ('coadd_nwgint', 0), ('swarp', 0), ('src_extractor', 0), ('desdm_meds', 0), ('pizza_cutter', 0), ('metadetect', 0), ('fitvd', 0), ('delete_images', 0), ('delete_sources', 0)]


def check_completed(output_path):
    print(f"checking steps for {output_path}")
    status = 0
    job_record = os.path.join(output_path, "job_record.pkl")
    if os.path.isfile(job_record):
        with open(job_record, "rb") as fp:
            record = pickle.load(fp)
            steps = record["step_names"]
            completed_steps = record["completed_step_names"]
            for step in steps:
                if (step, 0) not in completed_steps:
                    print(f"{step} incomplete")
                    status += 1
                else:
                    print(f"{step} complete")
    return status


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "output",
        type=str,
        help="output directory [path]",
    )

    return parser.parse_args()


def main():
    args = get_args()

    status = check_completed(args.output)
    sys.exit(status)


if __name__ == "__main__":
    main()

