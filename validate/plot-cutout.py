import argparse
from pathlib import Path
import os

import joblib
import tqdm
import h5py
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import Divider, Size
from mpl_toolkits.axes_grid1 import make_axes_locatable
import fitsio
import yaml

from esutil.pbar import PBar
from ngmix.medsreaders import NGMixMEDS
from pizza_cutter_metadetect.masks import get_slice_bounds


import plotting


def read_meds(fname):
    coadd_dims = (10_000, 10_000)

    m = NGMixMEDS(fname)

    obj_data = m.get_cat()
    meta = m.get_meta()
    pz_config = yaml.safe_load(meta['config'][0])
    buffer_size = int(pz_config['coadd']['buffer_size'])
    central_size = int(pz_config['coadd']['central_size'])

    full_image = np.zeros(coadd_dims, dtype=np.float32)

    for slice_ind in PBar(range(m.size), desc="reading slices"):
        obslist = m.get_obslist(slice_ind)
        scol = obj_data["orig_start_col"][slice_ind, 0]
        srow = obj_data["orig_start_row"][slice_ind, 0]
        slice_bnds = get_slice_bounds(
            orig_start_col=scol,
            orig_start_row=srow,
            central_size=central_size,
            buffer_size=buffer_size,
            coadd_dims=coadd_dims,
        )
        if len(obslist) > 0:
            img = obslist[0].image
            full_image[
                slice_bnds["min_row"]+srow:slice_bnds["max_row"]+srow,
                slice_bnds["min_col"]+scol:slice_bnds["max_col"]+scol,
            ] = img[
                slice_bnds["min_row"]:slice_bnds["max_row"],
                slice_bnds["min_col"]:slice_bnds["max_col"],
            ]
        else:
            full_image[
                slice_bnds["min_row"]+srow:slice_bnds["max_row"]+srow,
                slice_bnds["min_col"]+scol:slice_bnds["max_col"]+scol,
            ] = np.nan

    return full_image


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "imsim_dir",
        type=str,
        help="Image simulation output directory",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="whether to save the plot",
    )
    parser.add_argument(
        "--mask",
        action="store_true",
        help="whether to overplot the mask",
    )
    parser.add_argument(
        "--truth",
        action="store_true",
        help="whether to overplot the truth",
    )
    parser.add_argument(
        "--zoom",
        action="store_true",
        help="whether to zoom the axes",
    )
    return parser.parse_args()


def main():

    args = get_args()

    imsim_path = Path(args.imsim_dir)
    config_name = imsim_path.name

    band = "r"

    for tile_dir in (imsim_path / "des-pizza-slices-y6").glob("DES*"):
        tile = tile_dir.stem
        fname_coadd = imsim_path / "des-pizza-slices-y6" / tile / f"{tile}_{band}_des-pizza-slices-y6-v15_meds-pizza-slices.fits.fz"
        if args.mask:
            fname_mask = imsim_path / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000-mask.fits.fz"
        if args.truth:
            fname_truth = imsim_path / "truth_files" / f"{tile}-truthfile.fits"

    if not (
        os.path.exists(fname_coadd)
    ):
        raise ValueError(f"Coadd file does not exist")
    if args.mask and not (
        os.path.exists(fname_mask)
    ):
        raise ValueError(f"Mask file does not exist")
    if args.truth and not (
        os.path.exists(fname_truth)
    ):
        raise ValueError(f"Truth file does not exist")

    coadd = read_meds(fname_coadd)
    if args.mask:
        mask = fitsio.read(fname_mask)
    if args.truth:
        truth = fitsio.read(fname_truth)
        truth = truth[(truth["band"] == band)]
        truth_stars = truth[(truth["obj_type"] == "s")]
        truth_gals = truth[(truth["obj_type"] == "g")]


    plotting.setup()

    fig, axs = plotting.make_axes(
        1, 1,
        width=2,
        height=2,
        x_margin=1,
        y_margin=0.5,
        gutter=1,
        fig_width=4,
        fig_height=3,
    )

    plotting.imshow(axs[0, 0], np.arcsinh(coadd), origin="lower")
    axs[0, 0].set_xlabel("x_coadd [pixels]")
    axs[0, 0].set_ylabel("y_coadd [pixels]")
    if args.truth:
        axs[0, 0].scatter(truth_stars["x_coadd"], truth_stars["y_coadd"], s=6, c="b")
        axs[0, 0].scatter(truth_gals["x_coadd"], truth_gals["y_coadd"], s=6, c="k")
    if args.mask:
        plotting.imshow(axs[0, 0], np.arcsinh(mask), origin="lower", cmap="Reds", alpha=0.5)
    # axs[0, 0].set_title(f"{config_name}")

    if args.zoom:
        axs[0, 0].set_xlim(4500, 5500)
        axs[0, 0].set_ylim(4500, 5500)

    if args.save:
        fig.savefig("cutout.pdf")

    plt.show()


if __name__ == "__main__":
    main()
