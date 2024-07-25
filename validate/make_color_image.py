# from https://github.com/beckermr/des-y6-analysis/blob/main/2022_09_28_color_images/make_color_image.py
import argparse
import subprocess
import glob
import os
import sys
import fitsio
import numpy as np
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "tilename",
    #     type=str,
    #     help="tilename",
    # )
    parser.add_argument(
        "imsim_dir",
        type=str,
        help="Image simulation output directory",
    )
    return parser.parse_args()

def main():
    args = get_args()

    imsim_path = Path(args.imsim_dir)

    bands = ["g", "r", "i"]
    coadds = {}

    for band in bands:
        for tile_dir in (imsim_path / "des-pizza-slices-y6").glob("DES*"):
            tile = tile_dir.stem
            fname_coadd = imsim_path / "des-pizza-slices-y6" / tile / f"{tile}_{band}_des-pizza-slices-y6-v15_meds-pizza-slices.fits.fz"
            continue

        coadds[band] = fname_coadd

    # coadd_path = "/pscratch/sd/s/smau/coadds"
    image_path = "/pscratch/sd/s/smau/images"

    # os.makedirs(coadd_path, exist_ok=True)
    os.makedirs(image_path, exist_ok=True)

    for band, fname_coadd in coadds.items():
        subprocess.run(
            [
                f"make-coadd-image-from-slices",
                f"{fname_coadd}",
                f"--output-path={image_path}/{tile}-{band}.fits.fz",
            ],
            check=True,
        )

    output_path = f"{image_path}/{tile}-coadd-gri.jpg"
    output_path_crop = f"{image_path}/{tile}-coadd-gri-crop.jpg"

    subprocess.run(
        [
            f"des-make-image-fromfiles",
            output_path,
            f"{image_path}/{tile}-g.fits.fz",
            f"{image_path}/{tile}-r.fits.fz",
            f"{image_path}/{tile}-i.fits.fz",
        ],
        check=True,
    )
    os.remove(f"{image_path}/{tile}-g.fits.fz")
    os.remove(f"{image_path}/{tile}-r.fits.fz")
    os.remove(f"{image_path}/{tile}-i.fits.fz")

    subprocess.run(
        [
            f"magick",
            output_path,
            f"-crop",
            f"1000x1000+4500+4500",
            output_path_crop,
        ],
        check=True,
    )


if __name__ == "__main__":
    main()

