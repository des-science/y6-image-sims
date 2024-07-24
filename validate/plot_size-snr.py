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
    "logsnr": np.linspace(0, 5, NBINS),
    # "logsize": np.linspace(-0.1, 0.4, NBINS),
    "size": np.linspace(-1, 1, NBINS),
}


def compute_logsnr(data, mask):

    snr = data[f"gauss_s2n"][mask]
    logsnr = np.log10(snr)

    return logsnr
    # return snr


def compute_size(data, mask):

    # T_ratio = data[f"gauss_T_ratio"][mask]
    # psf_T = data[f"gauss_psf_T"][mask]

    # size = T_ratio * psf_T

    # logsize = np.log10(1 + size)

    # return logsize

    # return np.log10(T_ratio)

    # T_ratio = data[f"gauss_T_ratio"][mask]
    T_ratio = data[f"pgauss_T"][mask] / data[f"pgauss_psf_T"][mask]
    return T_ratio


def load_file(fname, cuts=False):
    fits = fitsio.FITS(fname)
    w = fits[1].where("mdet_step == \"noshear\"")
    # w = fits[1].where("mdet_step == \"noshear\" && mdet_flags == 0")
    data = fits[1][w]
    if cuts:
        inds, = np.where(
            (data['psfrec_flags'] == 0) &
            (data['gauss_flags'] == 0) &
            (data['gauss_s2n'] > 5) &
            (data['pgauss_T_flags'] == 0) &
            (data['pgauss_s2n'] > 5) &
            (data['pgauss_band_flux_flags_g'] == 0) &
            (data['pgauss_band_flux_flags_r'] == 0) &
            (data['pgauss_band_flux_flags_i'] == 0) &
            (data['pgauss_band_flux_flags_z'] == 0) &
            (data['mask_flags'] == 0) &
            (data['shear_bands'] == '123')
        )
        data = data[inds]
        data = des_y6utils.mdet.add_extinction_correction_columns(data)

    # mask = selections.get_selection(data)

    # return data[mask]
    return data


def size_snr_hist(data, mask, bins):
    value_x = compute_logsnr(data, mask)
    value_y = compute_size(data, mask)
    hist, _, _ = np.histogram2d(value_x, value_y, bins=bins)
    # hist, _, _, _ = stats.binned_statistic_2d(
    #     value_x,
    #     value_y,
    #     None,
    #     statistic="count",
    #     bins=bins,
    # )
    return hist



def accumulate_pair(dset_plus, dset_minus, *, tile, bins, mdet_mask):
    # fplus = pdict["catalog"]
    # fminus = mdict["catalog"]

    # data_p = load_file(fplus)
    # data_m = load_file(fminus)

    # cuts_p = selections.get_selection(data_p)
    # cuts_m = selections.get_selection(data_m)

    data_p = load_file(dset_plus)
    data_m = load_file(dset_minus)
    cuts_p = slice(-1)
    cuts_m = slice(-1)
    # cuts_p = data_p["mdet_flags"] == 0
    # cuts_m = data_m["mdet_flags"] == 0

    hist_p = size_snr_hist(data_p, cuts_p, bins)
    hist_m = size_snr_hist(data_m, cuts_m, bins)

    tile_area_p = util.get_tile_area(
        tile,
        "r",
        shear="plus",
        mdet_mask=mdet_mask,
    )
    tile_area_m = util.get_tile_area(
        tile,
        "r",
        shear="minus",
        mdet_mask=mdet_mask,
    )

    return hist_p, tile_area_p, hist_m, tile_area_m


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

    # pairs = util.gather_sims(args.imsim_dir)

    # ntiles = len([p for p in pairs.values() if p])

    catalogs = util.gather_catalogs(imsim_path)

    hf = h5py.File(
        "/dvs_ro/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        # "/global/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        mode="r",
        locking=False
    )
    dset = hf["mdet"]["noshear"]

    mdet_mask = util.load_mdet_mask()
    mdet_area = mdet_mask.get_valid_area()

    plotting.setup()
    # fig, axs = plt.subplots(len(all_axes), 3, squeeze=False, sharex="row", sharey="row")

    fig, axs = plotting.make_axes(
        1, 3,
        width=2,
        height=2,
        x_margin=1,
        y_margin=1/2,
        margin_top=1,
        gutter=1,
        fig_width=10,
        fig_height=3.5,
        sharex="row",
        sharey="row",
    )

    bins = (BINS["logsnr"], BINS["size"])

    hist = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    # TODO
    # for sl in dset["patch_num"].iter_chunks():
    #     print(f"reading slice {sl} of mdet")
    #     _hist = size_snr_hist(dset, sl, bins)
    #     # hist += _hist
    #     hist = np.nansum([hist, _hist], axis=0)
    #
    # TODO
    mdet_area = 0
    for _mdet_file in Path("/global/cfs/cdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6_UNBLINDED/tiles/").glob("*.fits"):
        _d = load_file(_mdet_file, cuts=True)
        _cuts = slice(-1)
        _hist = size_snr_hist(_d, _cuts, bins)
        hist += _hist
        tile_name = _mdet_file.name.split("_")[0]
        _tile_area = util.get_tile_area(
            tile_name,
            "r",
            mdet_mask=mdet_mask,
        )
        mdet_area += _tile_area
    # TODO
    hist /= mdet_area

    # jobs = [
    #     joblib.delayed(accumulate_pair)(pdict=sims["plus"], mdict=sims["minus"], tile=tile, bins=bins, mdet_mask=mdet_mask)
    #     for tile, seeds in pairs.items()
    #     for seed, sims in seeds.items()
    # ]
    jobs = [
            joblib.delayed(accumulate_pair)(catalogs[tile]["plus"], catalogs[tile]["minus"], tile=tile, bins=bins, mdet_mask=mdet_mask)
            for tile in catalogs.keys()
        ]
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

    ax = axs[0, 0]
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
    # ax.set_xlabel("$S/N$")
    ax.set_xlabel("$\\log_{10}(S/N)$")
    # ax.set_ylabel("$\\log_{10}(1 + T)$")
    ax.set_ylabel("$T/T_{PSF}$")
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
    # ax.grid()

    # ax = fig.add_axes(
    #     divider.get_position(),
    #     axes_locator=divider.new_locator(nx=5, ny=1)
    # )
    # cax = fig.add_axes(
    #     divider.get_position(),
    #     axes_locator=divider.new_locator(nx=7, ny=1)
    # )
    # ax.cax = cax

    ax = axs[0, 1]
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
    # ax.set_xlabel("$S/N$")
    ax.set_xlabel("$\\log_{10}(S/N)$")
    # ax.set_ylabel("$\\log_{10}(1 + T)$")
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
    # ax.set_xlabel("$\\log_{10}(S/N)$")
    # ax.set_ylabel("$\\log_{10}(1 + T)$")
    # ax.grid()
    # fig.colorbar(pcm, cax=ax.cax)

    ax = axs[0, 2]
    contours = plotting.contour(ax, hist, bins, norm=norm, levels=levels, cmap=cmap_mdet)
    contours = plotting.contour(ax, hist_sims, bins, norm=norm, levels=levels, cmap=cmap_sims)
    # ax.set_xlabel("$S/N$")
    ax.set_xlabel("$\\log_{10}(S/N)$")
    # ax.set_ylabel("$\\log_{10}(1 + T)$")
    ax.grid()

    fig.suptitle(config_name)


    plt.show()


if __name__ == "__main__":
    main()
