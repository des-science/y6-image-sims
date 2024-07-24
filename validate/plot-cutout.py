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
import util


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
        "--band",
        type=str,
        default="r",
        help="DES bandpass",
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
        "--source",
        action="store_true",
        help="whether to overplot the source",
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
    parser.add_argument(
        "--detection",
        action="store_true",
        help="whether to plot detections",
    )
    return parser.parse_args()


def main():

    args = get_args()

    imsim_path = Path(args.imsim_dir)
    shear = imsim_path.parts[-1]
    seed = imsim_path.parts[-2]
    tilename = imsim_path.parts[-3]
    config = imsim_path.parts[-4]

    band = args.band

    for tile_dir in (imsim_path / "des-pizza-slices-y6").glob("DES*"):
        tile = tile_dir.stem
        fname_coadd = imsim_path / "des-pizza-slices-y6" / tile / f"{tile}_{band}_des-pizza-slices-y6-v15_meds-pizza-slices.fits.fz"
        if args.mask:
            fname_mask = imsim_path / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000-mask.fits.fz"
        if args.truth:
            fname_truth = imsim_path / "truth_files" / f"{tile}-truthfile.fits"
        if args.detection:
            fname_detection = imsim_path / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000.fits"

        if args.source:
            fname_source_stars = f"/dvs_ro/cfs/projectdirs/des/atong/y6kp-shear/starsim/catalogs/merged_y6/{tile}.fits"
            fname_source_gals = f"/pscratch/sd/b/beckermr/cosmos_simcat_v7_{tile}_seed{seed}.fits"

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

        band_selection = (truth["band"] == band)
        star_selection = (truth["obj_type"] == "s")
        gal_selection = (truth["obj_type"] == "g")

        truth_stars = truth[star_selection & band_selection]
        truth_gals = truth[gal_selection & band_selection]

    if args.source:
        wcs = util.load_wcs(tile, band=band)

        source_stars = fitsio.read(fname_source_stars)
        source_stars_selection = (source_stars["imag"] < 25.)
        source_stars = source_stars[source_stars_selection]
        source_stars_x, source_stars_y = wcs.radecToxy(source_stars["ra"], source_stars["dec"], units="deg")
        source_stars_imag = source_stars["imag"]

        # source_gals = fitsio.read(fname_source_gals)
        # source_gals_selection = (
        #     (source_gals["x_sim"] >= 250)
        #     & (source_gals["x_sim"] < 9750)
        #     & (source_gals["y_sim"] >= 250)
        #     & (source_gals["y_sim"] < 9750)
        #     & (source_gals["mag_i_red_sim"] >= 15.)
        #     & (source_gals["mag_i_red_sim"] < 25.4)
        #     & (source_gals["bdf_hlr"] >= 0.)
        #     & (source_gals["bdf_hlr"] < 5.)
        #     & (source_gals["isgal"] == 1)
        #     & (source_gals["mask_flags"] == 0)
        # )
        # source_gals = source_gals[source_gals_selection]
        # source_gals_x, source_gals_y = wcs.radecToxy(source_gals["ra"], source_gals["dec"], units="deg")
        # source_gals_imag = source_gals["imag"]

        source_gaia = fitsio.read("/global/cfs/cdirs/desbalro/des-pizza-slices-y6/DES0105-5040/sources-g/OPS_Taiga/cal/cat_tile_gaia/v1/DES0105-5040_GAIA_DR2_v1.fits")
        source_gaia_x, source_gaia_y = wcs.radecToxy(source_gaia["RA"], source_gaia["DEC"], units="deg")
        source_gaia_G = source_gaia["PHOT_G_MEAN_MAG"]

    if args.detection:
        detection = fitsio.read(fname_detection)
        detection = detection[detection["mdet_step"] == "noshear"]


    plotting.setup()

    # fig, axs = plotting.make_axes(
    #     1, 1,
    #     width=2,
    #     height=2,
    #     x_margin=1,
    #     y_margin=0.5,
    #     gutter=1,
    #     fig_width=4,
    #     fig_height=3,
    # )
    fig, axs = plt.subplots(1, 1, squeeze=False)

    plotting.imshow(axs[0, 0], np.arcsinh(coadd), origin="lower")
    axs[0, 0].set_xlabel("x_coadd [pixels]")
    axs[0, 0].set_ylabel("y_coadd [pixels]")
    axs[0, 0].set_title(f"{tile} {band}")
    fig.suptitle(f"{config}")

    if args.mask:
        plotting.imshow(axs[0, 0], np.arcsinh(mask), origin="lower", cmap="Reds", alpha=0.5)
    if args.truth:
        axs[0, 0].scatter(truth_stars["x_coadd"], truth_stars["y_coadd"], s=24, marker="x", c="k")
        axs[0, 0].scatter(truth_gals["x_coadd"], truth_gals["y_coadd"], s=6, c="b")
    if args.source:
        axs[0, 0].scatter(source_stars_x, source_stars_y, s=24, c="k", marker="x")
        for x, y, imag in zip(source_stars_x, source_stars_y, source_stars_imag):
            axs[0, 0].text(x, y, round(imag), c="w", horizontalalignment="left", verticalalignment="bottom")

        # axs[0, 0].scatter(source_gaia_x, source_gaia_y, s=24, c="k", marker="x")
        # for x, y, G in zip(source_gaia_x, source_gaia_y, source_gaia_G):
        #     axs[0, 0].text(x, y, round(G), c="k", horizontalalignment="left", verticalalignment="bottom")

    if args.detection:
        axs[0, 0].scatter(detection["x"], detection["y"], s=48, c="w", marker="+")
        # for x, y, imag in zip(source_stars_x, source_stars_y, source_stars_imag):
        #     axs[0, 0].text(x, y, round(imag), c="w", horizontalalignment="left", verticalalignment="bottom")

    if args.zoom:
        axs[0, 0].set_xlim(4500, 5500)
        axs[0, 0].set_ylim(4500, 5500)

    if args.save:
        fig.savefig("cutout.png")
        for i, image in enumerate(axs[0, 0].images):
            image.write_png(f"{tile}-{band}-{i}.png")

    plt.show()


if __name__ == "__main__":
    main()
