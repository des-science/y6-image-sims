import argparse
from pathlib import Path
import os

import h5py
import joblib
import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import fitsio

import des_y6utils

import selections
import weights
import util
import plotting


def grid_file(*, fname):
    d = fitsio.read(fname)

    msk = selections.get_selection(d)
    msk &= (d["mdet_step"] == "noshear")

    pgauss_T_err = d["pgauss_T_err"][msk]
    pgauss_T = d["pgauss_T"][msk]

    return pgauss_T_err, pgauss_T


def accumulate_file_pair(*, pdict, mdict, bins, tile, mdet_mask):
    fplus = pdict["catalog"]
    fminus = mdict["catalog"]

    pgauss_T_err_p, pgauss_T_p = grid_file(fname=fplus)
    pgauss_T_err_m, pgauss_T_m = grid_file(fname=fminus)

    hist_p, _, _ = np.histogram2d(pgauss_T_err_p, pgauss_T_p, bins=bins)
    hist_m, _, _ = np.histogram2d(pgauss_T_err_m, pgauss_T_m, bins=bins)

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


    # bins = (
    #     np.linspace(0, 0.8, 100),
    #     np.linspace(-2, 5, 100)
    # )
    bins = (
        np.linspace(0, 0.2, 100),
        np.linspace(-1, 2, 100)
    )

    hf = h5py.File(
        "/dvs_ro/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        # "/global/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        mode="r",
        locking=False
    )
    dset = hf["mdet"]["noshear"]

    mdet_mask = util.load_mdet_mask()
    mdet_area = mdet_mask.get_valid_area()

    hist = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    for sl in dset["patch_num"].iter_chunks():
        print(f"reading slice {sl} of mdet")
        _hist, _, _ = np.histogram2d(dset["pgauss_T_err"][sl], dset["pgauss_T"][sl], bins=bins)
        hist += _hist

    hist /= mdet_area

    jobs = [
        joblib.delayed(accumulate_file_pair)(pdict=sims["plus"], mdict=sims["minus"], bins=bins, tile=tile, mdet_mask=mdet_mask)
        for tile, seeds in pairs.items()
        for seed, sims in seeds.items()
    ]
    if args.fast:
        jobs = jobs[:2]
    print(f"Processing {len(jobs)} paired simulations ({ntiles} tiles)")

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
    hist_sims = np.nanmean([hist_p / area_p, hist_m / area_m], axis=0)

    # percentiles = [50, 99]
    # percentiles = [50.00, 68.27, 95.45, 99.73]
    # percentiles = [0.1, 0.3, 0.5, 0.7, 0.9]
    # percentiles = [0.3, 0.5, 0.7, 0.9]
    percentiles = 1.0 - np.exp(-0.5 * np.array([1.5, 2.0, 2.5, 3.0]) ** 2)
    levels = util.get_levels(hist, percentiles=percentiles)

    cmap_mdet = "des-y6-mdet"
    cmap_sims = "des-y6-sims"

    norm = colors.LogNorm()

    # fig, axs = plt.subplots(1, 3, sharex=True, sharey=True)
    plotting.setup()

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

    pcm = axs[0, 0].pcolormesh(
        bins[0],
        bins[1],
        hist.T,
        norm=norm,
        cmap=cmap_mdet,
        alpha=0.5,
    )
    contours = plotting.contour(axs[0, 0], hist, bins, norm=norm, levels=levels, cmap=cmap_mdet)
    axs[0, 0].set_xlabel("pgauss_T_err")
    axs[0, 0].set_ylabel("pgauss_T")
    axs[0, 0].set_title("mdet")
    axs[0, 0].grid()
    plotting.add_colorbar(axs[0, 0], pcm, label="$counts / deg^2$")
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     f"${{{p}}} \\%$"
    #     for p in percentiles
    # ]
    # axs[0].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    pcm = axs[0, 1].pcolormesh(
        bins[0],
        bins[1],
        hist_sims.T,
        norm=norm,
        cmap=cmap_sims,
        alpha=0.5,
    )
    contours = plotting.contour(axs[0, 1], hist_sims, bins, norm=norm, levels=levels, cmap=cmap_sims)
    axs[0, 1].set_xlabel("pgauss_T_err")
    # axs[0, 1].set_ylabel("pgauss_T")
    axs[0, 1].set_title("sims")
    axs[0, 1].grid()
    plotting.add_colorbar(axs[0, 1], pcm, label="$counts / deg^2$")
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     f"${{{p}}} \\%$"
    #     for p in percentiles
    # ]
    # axs[1].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    # pcm = axs[3].pcolormesh(bins[0], bins[1], hist_m.T, norm=colors.LogNorm())
    # axs[3].contour(bin_centers[0], bin_centers[1], hist_m.T, levels=levels_m, cmap=cmap_sims)
    # axs[3].set_xlabel("pgauss_T_err")
    # axs[3].set_ylabel("pgauss_T")
    # axs[3].set_title("minus")
    # axs[3].grid()
    # fig.colorbar(axs[3], pcm)

    contours = plotting.contour(axs[0, 2], hist, bins, norm=norm, levels=levels, cmap=cmap_mdet)
    contours = plotting.contour(axs[0, 2], hist_sims, bins, norm=norm, levels=levels, cmap=cmap_sims)
    axs[0, 2].set_xlabel("pgauss_T_err")
    # axs[0, 2].set_ylabel("pgauss_T")
    axs[0, 2].grid()
    # nm_mdet, _ = contours_mdet.legend_elements()
    # nm_sims, _ = contours_sims.legend_elements()
    # labels = [
    #     f"${{{p}}} \\%$"
    #     for p in percentiles
    # ]
    # labels_mdet = [f"mdet {label}" for label in labels]
    # labels_sims = [f"sims {label}" for label in labels]
    # legend = axs[2].legend(
    #     nm_mdet + nm_sims,
    #     labels_mdet + labels_sims,
    #     ncols=2,
    #     loc="upper left",
    # )
    # legend_mdet = axs[2].legend(
    #     nm_mdet,
    #     labels,
    #     title="mdet",
    #     loc="upper left",
    # )
    # legend_sims = axs[2].legend(
    #     nm_sims,
    #     labels,
    #     title="sims",
    #     loc="upper right",
    # )
    # axs[2].add_artist(legend_mdet)
    # axs[2].add_artist(legend_sims)

    fig.suptitle(config_name)


    plt.show()


if __name__ == "__main__":
    main()
