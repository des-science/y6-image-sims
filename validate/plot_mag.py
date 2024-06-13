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

import healsparse
import des_y6utils


import util
import plotting
import selections


NBINS = 100
BINS = {
    "g": np.linspace(17, 27, NBINS),
    "r": np.linspace(17, 27, NBINS),
    "i": np.linspace(17, 27, NBINS),
    "z": np.linspace(17, 27, NBINS),
}


def compute_mag(data, mask, band):

    flux = data[f"pgauss_band_flux_{band}"][mask]

    mag = -2.5 * np.log10(flux) + 30

    return mag


def load_file(fname):
    fits = fitsio.FITS(fname)
    w = fits[1].where("mdet_step == \"noshear\"")
    data = fits[1][w]

    mask = selections.get_selection(data)

    return data[mask]


def mag_hist(data, mask, band, bins):
    mag = compute_mag(data, mask, band)
    hist, _ = np.histogram(mag, bins=bins)
    # hist, _, _ = stats.binned_statistic(
    #     mag,
    #     None,
    #     statistic="count",
    #     bins=bins,
    # )
    return hist


def accumulate_pair(*, pdict, mdict, tile, band, bins, mdet_mask):
    fplus = pdict["catalog"]
    fminus = mdict["catalog"]

    data_p = load_file(fplus)
    data_m = load_file(fminus)

    cuts_p = selections.get_selection(data_p)
    cuts_m = selections.get_selection(data_m)

    hist_p = mag_hist(data_p, cuts_p, band, bins)
    hist_m = mag_hist(data_m, cuts_m, band, bins)

    # hsp_plus = pdict["mask"]
    # hsp_minus = mdict["mask"]

    # hsp_map_p = healsparse.HealSparseMap.read(hsp_plus)
    # hsp_map_m = healsparse.HealSparseMap.read(hsp_minus)

    tile_area_p = util.get_tile_area(
        tile,
        band,
        shear="plus",
        pizza_slices_dir=pdict["pizza_slices_dir"],
        des_pizza_slices_dir=os.environ["IMSIM_DATA"],
        mdet_mask=mdet_mask,
    )
    tile_area_m = util.get_tile_area(
        tile,
        band,
        shear="minus",
        pizza_slices_dir=mdict["pizza_slices_dir"],
        des_pizza_slices_dir=os.environ["IMSIM_DATA"],
        mdet_mask=mdet_mask,
    )

    return hist_p, tile_area_p, hist_m, tile_area_m


def format_band(band):
    return f"${{{band}}}$"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "imsim_dir",
        type=str,
        help="Image simulation output directory",
    )
    parser.add_argument(
        "--seed",
        type=int,
        required=False,
        default=1,
        help="RNG seed [int]",
    )
    parser.add_argument(
        "--n_jobs",
        type=int,
        required=False,
        default=8,
        help="Number of joblib jobs [int]",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="whether to do a fast run",
    )
    return parser.parse_args()


def main():

    args = get_args()

    # pairs = {}

    imsim_path = Path(args.imsim_dir)
    config_name = imsim_path.name
    # tile_dirs = imsim_path.glob("*")

    # for tile_dir in tile_dirs:
    #     tile = tile_dir.stem
    #     pairs[tile] = {}

    #     run_dirs = tile_dir.glob("*")

    #     for run_dir in run_dirs:
    #         run = run_dir.stem
    #         # print(f"\tRun: {run}")

    #         fname_plus = run_dir / "plus" / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000.fits"
    #         fname_minus = run_dir / "minus" / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000.fits"

    #         if not (
    #             os.path.exists(fname_plus)
    #             and os.path.exists(fname_minus)
    #         ):
    #             continue

    #         pairs[tile][run] = (fname_plus, fname_minus)
    pairs = util.gather_sims(args.imsim_dir)

    ntiles = len([p for p in pairs.values() if p])

    hf = h5py.File(
        "/dvs_ro/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        # "/global/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        mode="r",
        locking=False
    )
    dset = hf["mdet"]["noshear"]

    mdet_mask = util.load_mdet_mask()
    mdet_area = mdet_mask.get_valid_area()

    bands = ["g", "r", "i", "z"]
    # bands = ["i"]

    # fig, axs = plt.subplots(1, len(bands), squeeze=False, sharex="row", sharey="row")
    fig, axs = plotting.make_axes(
        2, 4,
        width=2,
        height=2,
        x_margin=1,
        y_margin=1/2,
        margin_top=1,
        gutter=1,
        fig_width=13,
        fig_height=6,
        sharex="all",
        sharey="row",
    )

    for i, band in enumerate(bands):

        # bins_center = BINS[band]
        # bins = np.concatenate([
        #     [-np.inf], BINS[band], [np.inf],
        # ])
        bins = BINS[band]

        hist = np.zeros(
            len(bins) - 1
        )
        for sl in dset["patch_num"].iter_chunks():
            print(f"reading slice {sl} of mdet")
            _hist = mag_hist(dset, sl, band, bins)
            hist += _hist

            # if args.fast:
            #     break

        hist /= mdet_area

        jobs = [
            joblib.delayed(accumulate_pair)(pdict=sims["plus"], mdict=sims["minus"], tile=tile, band=band, bins=bins, mdet_mask=mdet_mask)
            for tile, seeds in pairs.items()
            for seed, sims in seeds.items()
        ]
        if args.fast:
            jobs = jobs[:2]
        print(f"Processing {len(jobs)} paired simulations")

        hist_p = np.zeros(len(bins) - 1)
        hist_m = np.zeros(len(bins) - 1)
        area_p = 0
        area_m = 0
        with joblib.Parallel(n_jobs=args.n_jobs, backend="loky", verbose=10) as par:
            # d = par(jobs)
            for res in par(jobs):
                hist_p += res[0]
                area_p += res[1]
                hist_m += res[2]
                area_m += res[3]

        # hist_sims = np.nanmean([hist_p, hist_m], axis=0)
        # hist_sims /= np.nanmean([area_p, area_m])
        hist_sims = np.nanmean([hist_p / area_p, hist_m / area_m], axis=0)

        ax = axs[0, i]
        ax.stairs(
            hist,
            edges=bins,
            color=plotting.mdet_color,
            label="mdet",
        )
        ax.stairs(
            hist_sims,
            edges=bins,
            color=plotting.sims_color,
            label="sims",
        )
        # ax.set_xlabel(format_band(band))
        ax.set_ylabel(f"$counts / deg^2$")
        ax.set_yscale("log")
        if i == 0:
            ax.legend(loc="upper left")
        ax.grid()

        ax = axs[1, i]
        ax.stairs(
            hist_sims / hist,
            edges=bins,
            color=plotting.sims_color,
        )
        ax.set_xlabel(format_band(band))
        ax.set_ylabel(f"sims / mdet")
        # ax.set_yscale("log")
        ax.grid()

    fig.suptitle(config_name)

    plt.show()


if __name__ == "__main__":
    main()
