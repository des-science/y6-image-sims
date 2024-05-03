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
    "mag": np.linspace(17, 27, NBINS),
    "size": np.linspace(0, 5, NBINS),
}


def compute_mag(data, mask, band):

    flux = data[f"pgauss_band_flux_{band}"][mask]

    mag = -2.5 * np.log10(flux) + 30

    return mag


def compute_size(data, mask):

    T_ratio = data[f"gauss_T_ratio"][mask]
    psf_T = data[f"gauss_psf_T"][mask]

    size = T_ratio * psf_T

    return size


def load_file(fname):
    fits = fitsio.FITS(fname)
    w = fits[1].where("mdet_step == \"noshear\"")
    data = fits[1][w]

    mask = selections.get_selection(data)

    return data[mask]


def mag_size_hist(data, mask, band, bins):
    mag = compute_mag(data, mask, band)
    size = compute_size(data, mask)
    # hist, _, _ = np.histogram2d(color_x, color_y, bins=bins)
    hist, _, _, _ = stats.binned_statistic_2d(
        mag,
        size,
        None,
        statistic="count",
        bins=bins,
    )
    return hist


def accumulate_pair(*, pdict, mdict, tile, band, bins, mdet_mask):
    fplus = pdict["catalog"]
    fminus = mdict["catalog"]

    data_p = load_file(fplus)
    data_m = load_file(fminus)

    cuts_p = selections.get_selection(data_p)
    cuts_m = selections.get_selection(data_m)

    hist_p = mag_size_hist(data_p, cuts_p, band, bins)
    hist_m = mag_size_hist(data_m, cuts_m, band, bins)

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

    imsim_path = Path(args.imsim_dir)
    config_name = imsim_path.name

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

    bands = ["g", "r", "i"]
    # bands = ["i"]

    plotting.setup()

    fig, axs = plotting.make_axes(
        3, 3,
        width=2,
        height=2,
        x_margin=1,
        y_margin=1/2,
        margin_top=1,
        gutter=1,
        y_gutter=0.5,
        fig_width=10,
        fig_height=8.5,
        sharex="row",
        sharey="row",
    )


    for i, band in enumerate(bands):

        # bins_center = (BINS[bands_x], BINS[bands_y])
        # bins_x = np.concatenate([
        #     [-np.inf], BINS[bands_x], [np.inf],
        # ])
        # bins_y = np.concatenate([
        #     [-np.inf], BINS[bands_y], [np.inf],
        # ])
        # bins = (bins_x, bins_y)
        bins = (BINS["mag"], BINS["size"])

        hist = np.zeros(
            (len(bins[0]) - 1, len(bins[1]) - 1)
        )
        for sl in dset["patch_num"].iter_chunks():
            print(f"reading slice {sl} of mdet")
            _hist = mag_size_hist(dset, sl, band, bins)
            # hist += _hist
            hist = np.nansum([hist, _hist], axis=0)

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

        hist_p = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
        hist_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
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

        # https://corner.readthedocs.io/en/latest/pages/sigmas/
        # percentiles = [50.00, 70.00, 90.00]
        # percentiles = 1.0 - np.exp(-0.5 * np.array([0.5, 1.0, 1.5, 2.0]) ** 2)
        # percentiles = [0.5, 0.7, 0.9]
        percentiles = 1.0 - np.exp(-0.5 * np.array([1.5, 2.0, 2.5, 3.0]) ** 2)
        levels = util.get_levels(hist, percentiles=percentiles)
        # levels = util.get_levels(hist_sims, percentiles=percentiles)

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

        ax = axs[i, 0]
        pcm = ax.pcolormesh(
            bins[0],
            bins[1],
            hist.T,
            # norm=colors.LogNorm(),
            norm=norm,
            cmap=cmap_mdet,
            alpha=0.5,
        )
        plotting.add_colorbar(ax, pcm, label="$counts / deg^2$")
        contours = plotting.contour(ax, hist, bins, norm=norm, levels=levels, cmap=cmap_mdet)
        ax.set_xlabel(format_band(band))
        ax.set_ylabel("gauss_T")
        if i == 0:
            # legend_elements, _ = contours.legend_elements()
            # legend_labels = [
            #     # f"${{{p * 100:.2f}}} \\%$"
            #     # for p in percentiles
            #     f"${{{util.get_percentile(hist, level):.2f}}} \\%$"
            #     for level in levels
            # ]
            # ax.legend(
            #     legend_elements,
            #     legend_labels,
            #     loc="upper left",
            # )
            ax.set_title("mdet")
        ax.grid()

        # ax = fig.add_axes(
        #     divider.get_position(),
        #     axes_locator=divider.new_locator(nx=5, ny=1)
        # )
        # cax = fig.add_axes(
        #     divider.get_position(),
        #     axes_locator=divider.new_locator(nx=7, ny=1)
        # )
        # ax.cax = cax

        ax = axs[i, 1]
        pcm = ax.pcolormesh(
            bins[0],
            bins[1],
            hist_sims.T,
            # norm=colors.LogNorm(),
            norm=norm,
            cmap=cmap_sims,
            alpha=0.5,
        )
        plotting.add_colorbar(ax, pcm, label="$counts / deg^2$")
        contours = plotting.contour(ax, hist_sims, bins, norm=norm, levels=levels, cmap=cmap_sims)
        ax.set_xlabel(format_band(band))
        # ax.set_ylabel(format_bands(bands_y))
        if i == 0:
            # legend_elements, _ = contours.legend_elements()
            # legend_labels = [
            #     # f"${{{p * 100:.2f}}} \\%$"
            #     # for p in percentiles
            #     f"${{{util.get_percentile(hist_sims, level):.2f}}} \\%$"
            #     for level in levels
            # ]
            # ax.legend(
            #     legend_elements,
            #     legend_labels,
            #     loc="upper left",
            # )
            # ax.set_title("plus")
            ax.set_title("sims")
        ax.grid()

        # ax = axs[i, 2]
        # pcm = ax.pcolormesh(
        #     bins[0][1:-1],
        #     bins[1][1:-1],
        #     hist_m.T[1:-1, 1:-1],
        #     norm=colors.LogNorm(),
        # )
        # ax.contour(
        #     bin_centers[0],
        #     bin_centers[1],
        #     hist_m.T[1:-1, 1:-1],
        #     levels=levels_m,
        #     cmap=cmap,
        # )
        # ax.set_xlabel(format_bands(bands_x))
        # ax.set_ylabel(format_bands(bands_y))
        # if i == 0:
        #     ax.set_title("minus")
        # ax.grid()
        # fig.colorbar(pcm, cax=ax.cax)

        ax = axs[i, 2]
        contours = plotting.contour(ax, hist, bins, norm=norm, levels=levels, cmap=cmap_mdet)
        contours = plotting.contour(ax, hist_sims, bins, norm=norm, levels=levels, cmap=cmap_sims)
        ax.set_xlabel(format_band(band))
        # ax.set_ylabel(format_bands(bands_y))
        # if i == 0:
        #     ax.set_title("minus")
        ax.grid()

    fig.suptitle(config_name)


    plt.show()


if __name__ == "__main__":
    main()
