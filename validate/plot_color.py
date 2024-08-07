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

import des_y6utils


import util
import plotting
import selections


NBINS = 100
BINS = {
    "gi": np.linspace(-10, 10, NBINS),
}


def compute_color(data, mask, bands, nodered=False):

    col_1 = f"pgauss_band_flux_{bands[0]}"
    col_2 = f"pgauss_band_flux_{bands[1]}"
    if nodered:
        col_1 += "_nodered"
        col_2 += "_nodered"
    flux_1 = data[col_1][mask]
    flux_2 = data[col_2][mask]

    color = -2.5 * np.log10(flux_1 / flux_2)

    return color



def load_file(fname):
    fits = fitsio.FITS(fname)
    w = fits[1].where("mdet_step == \"noshear\"")
    data = fits[1][w]

    mask = selections.get_selection(data)

    return data[mask]


def color_hist(data, mask, bands, bins, nodered=False):
    color = compute_color(data, mask, bands, nodered=nodered)
    hist, _ = np.histogram(color, bins=bins)
    return hist


def accumulate_pair(*, pdict, mdict, tile, bands, bins, mdet_mask):
    fplus = pdict["catalog"]
    fminus = mdict["catalog"]

    data_p = load_file(fplus)
    data_m = load_file(fminus)

    cuts_p = selections.get_selection(data_p)
    cuts_m = selections.get_selection(data_m)

    hist_p = color_hist(data_p, cuts_p, bands, bins)
    hist_m = color_hist(data_m, cuts_m, bands, bins)

    tile_area_p = util.get_tile_area(
        tile,
        "r",
        shear="plus",
        pizza_slices_dir=pdict["pizza_slices_dir"],
        des_pizza_slices_dir=os.environ["IMSIM_DATA"],
        mdet_mask=mdet_mask,
    )
    tile_area_m = util.get_tile_area(
        tile,
        "r",
        shear="minus",
        pizza_slices_dir=mdict["pizza_slices_dir"],
        des_pizza_slices_dir=os.environ["IMSIM_DATA"],
        mdet_mask=mdet_mask,
    )

    return hist_p, tile_area_p, hist_m, tile_area_m


def format_bands(bands):
    match len(bands):
        case 1:
            TeXstring = f"${{{bands}}}$"
        case 2:
            TeXstring = f"${{{bands[0]}}} - {{{bands[1]}}}$"
        case _:
            raise ValueError(f"Invalid bands for color or magnitude")
    return TeXstring


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

    pairs = util.gather_sims(args.imsim_dir)

    ntiles = len([p for p in pairs.values() if p])

    hf = h5py.File(
        "/dvs_ro/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_blinded.h5",
        # "/global/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_blinded.h5",
        mode="r",
        locking=False
    )
    dset = hf["mdet"]["noshear"]

    mdet_mask = util.load_mdet_mask()
    mdet_area = mdet_mask.get_valid_area()

    all_axes = [
        ("gi"),
    ]

    plotting.setup()
    # fig, axs = plt.subplots(len(all_axes), 3, squeeze=False, sharex="row", sharey="row")

    fig, axs = plotting.make_axes(
        1, 1,
        width=2,
        height=2,
        x_margin=1,
        y_margin=1/2,
        gutter=1,
        fig_width=4,
        fig_height=3,
        sharex="row",
        sharey="row",
    )


    for i, (bands) in enumerate(all_axes):

        # bins_center = (BINS[bands_x], BINS[bands_y])
        # bins_x = np.concatenate([
        #     [-np.inf], BINS[bands_x], [np.inf],
        # ])
        # bins_y = np.concatenate([
        #     [-np.inf], BINS[bands_y], [np.inf],
        # ])
        # bins = (bins_x, bins_y)
        bins = BINS[bands]

        hist = np.zeros(
            (len(bins) - 1)
        )
        for sl in dset["patch_num"].iter_chunks():
            print(f"reading slice {sl} of mdet")
            _hist = color_hist(dset, sl, bands, bins, nodered=True)
            # hist += _hist
            hist = np.nansum([hist, _hist], axis=0)

            # if args.fast:
            #     break

        hist /= mdet_area

        jobs = [
            joblib.delayed(accumulate_pair)(pdict=sims["plus"], mdict=sims["minus"], tile=tile, bands=bands, bins=bins, mdet_mask=mdet_mask)
            for tile, seeds in pairs.items()
            for seed, sims in seeds.items()
        ]
        if args.fast:
            jobs = jobs[:2]
        print(f"Processing {len(jobs)} paired simulations")

        hist_p = np.zeros((len(bins) - 1))
        hist_m = np.zeros((len(bins) - 1))
        area_p = 0
        area_m = 0
        with joblib.Parallel(n_jobs=args.n_jobs, backend="loky", verbose=10) as par:
            # d = par(jobs)
            for res in par(jobs):
                hist_p = np.nansum([hist_p, res[0]], axis=0)
                area_p = np.nansum([area_p, res[1]], axis=0)
                hist_m = np.nansum([hist_m, res[2]], axis=0)
                area_m = np.nansum([area_m, res[3]], axis=0)

        # hist_p, hist_m = np.sum(d, axis=0)

        # hist_sims = np.nanmean([hist_p, hist_m], axis=0)
        # hist_sims /= np.nanmean([area_p, area_m])
        hist_sims = np.nanmean([hist_p / area_p, hist_m / area_m], axis=0)

        # hist_p = np.zeros(
        #     (len(bins[0]) - 1, len(bins[1]) - 1)
        # )
        # hist_m = np.zeros(
        #     (len(bins[0]) - 1, len(bins[1]) - 1)
        # )
        # for seed in pairs.values():
        #     for pfile, mfile in seed.values():
        #         data_p = load_file(pfile)
        #         data_m = load_file(mfile)

        #         mask_p = get_cuts(data_p)
        #         mask_m = get_cuts(data_m)

        #         _hist_p = multiband_hist(data_p, mask_p, bands_x, bands_y, bins)
        #         hist_p += _hist_p

        #         _hist_m = multiband_hist(data_m, mask_m, bands_x, bands_y, bins)
        #         hist_m += _hist_m

        #         if args.fast:
        #             break

        #     if args.fast:
        #         break

        cmap_mdet = "des-y6-mdet"
        cmap_sims = "des-y6-sims"

        # fig, axs = plt.subplots(1, 3)
        # fig = plt.figure(figsize=(9, 3))
        # h = [
        #     Size.Fixed(1),
        #     Size.Fixed(2),
        #     Size.Fixed(1/8),
        #     Size.Fixed(1/8),
        #     Size.Fixed(6/8),
        #     Size.Fixed(2),
        #     Size.Fixed(1/8),
        #     Size.Fixed(1/8),
        #     Size.Fixed(6/8),
        #     Size.Fixed(2),
        #     Size.Fixed(1/8),
        #     Size.Fixed(1/8),
        #     Size.Fixed(6/8),
        # ]
        # v = [
        #     Size.Fixed(0.5),
        #     Size.Fixed(2),
        #     Size.Fixed(0.5),
        # ]
        # divider = Divider(fig, (0, 0, 1, 1), h, v, aspect=False)

        # ax = fig.add_axes(
        #     divider.get_position(),
        #     axes_locator=divider.new_locator(nx=1, ny=1)
        # )
        # cax = fig.add_axes(
        #     divider.get_position(),
        #     axes_locator=divider.new_locator(nx=3, ny=1)
        # )
        # ax.cax = cax

        norm = colors.LogNorm()

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
        ax.set_xlabel(format_bands(bands))
        ax.set_ylabel(f"$counts / deg^2$")
        ax.set_yscale("log")
        # if i == 0:
        #     ax.legend(loc="upper left")
        ax.grid()

    plt.show()


if __name__ == "__main__":
    main()
