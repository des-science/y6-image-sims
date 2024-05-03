import argparse
from pathlib import Path
import os

import joblib
import tqdm
import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import ticker
import fitsio
from scipy import stats

import des_y6utils

import selections
import weights
import util
import plotting


def grid_file(*, fname):
    d = fitsio.read(fname)

    msk = selections.get_selection(d)
    # msk &= (d["mdet_step"] == "noshear")
    ns_msk = msk & (d["mdet_step"] == "noshear")
    g1p_msk = msk & (d["mdet_step"] == "1p")
    g1m_msk = msk & (d["mdet_step"] == "1m")

    if np.any(ns_msk):
        size_ratio = d["gauss_T_ratio"][ns_msk]
        snr = d["gauss_s2n"][ns_msk]

        ellipticity = np.hypot(
            d["gauss_g_1"][ns_msk],
            d["gauss_g_2"][ns_msk]
        )

        weight = weights.get_shear_weights(d[ns_msk])

        size_ratio_g1p = d["gauss_T_ratio"][g1p_msk]
        snr_g1p = d["gauss_s2n"][g1p_msk]
        e1_g1p = d["gauss_g_1"][g1p_msk]

        size_ratio_g1m = d["gauss_T_ratio"][g1m_msk]
        snr_g1m = d["gauss_s2n"][g1m_msk]
        e1_g1m = d["gauss_g_1"][g1m_msk]

        return size_ratio, snr, ellipticity, weight, size_ratio_g1p, snr_g1p, e1_g1p, size_ratio_g1m, snr_g1m, e1_g1m
    else:
        return [np.nan], [np.nan], [np.nan], [np.nan], [np.nan], [np.nan], [np.nan], [np.nan], [np.nan], [np.nan]


def accumulate_file_pair(*, pdict, mdict, bins, tile, mdet_mask):
    fplus = pdict["catalog"]
    fminus = mdict["catalog"]

    size_ratio_p, snr_p, ellipticity_p, weight_p, size_ratio_g1p_p, snr_g1p_p, e1_g1p_p, size_ratio_g1m_p, snr_g1m_p, e1_g1m_p = grid_file(fname=fplus)
    size_ratio_m, snr_m, ellipticity_m, weight_m, size_ratio_g1p_m, snr_g1p_m, e1_g1p_m, size_ratio_g1m_m, snr_g1m_m, e1_g1m_m = grid_file(fname=fminus)

    ellipticity_p, _, _, _ = stats.binned_statistic_2d(
        size_ratio_p,
        snr_p,
        ellipticity_p,
        statistic="sum",
        bins=bins,
    )
    weight_p, _, _, _ = stats.binned_statistic_2d(
        size_ratio_p,
        snr_p,
        weight_p,
        statistic="sum",
        bins=bins,
    )
    count_p, _, _, _ = stats.binned_statistic_2d(
        size_ratio_p,
        snr_p,
        None,
        statistic="count",
        bins=bins,
    )

    ellipticity_m, _, _, _ = stats.binned_statistic_2d(
        size_ratio_m,
        snr_m,
        ellipticity_m,
        statistic="sum",
        bins=bins,
    )
    weight_m, _, _, _ = stats.binned_statistic_2d(
        size_ratio_m,
        snr_m,
        weight_m,
        statistic="sum",
        bins=bins,
    )
    count_m, _, _, _ = stats.binned_statistic_2d(
        size_ratio_m,
        snr_m,
        None,
        statistic="count",
        bins=bins,
    )

    count_g1p_p, _, _, _ = stats.binned_statistic_2d(
        size_ratio_g1p_p,
        snr_g1p_p,
        None,
        statistic="count",
        bins=bins,
    )
    count_g1m_p, _, _, _ = stats.binned_statistic_2d(
        size_ratio_g1m_p,
        snr_g1m_p,
        None,
        statistic="count",
        bins=bins,
    )
    e1_g1p_p, _, _, _ = stats.binned_statistic_2d(
        size_ratio_g1p_p,
        snr_g1p_p,
        e1_g1p_p,
        statistic="sum",
        bins=bins,
    )
    e1_g1m_p, _, _, _ = stats.binned_statistic_2d(
        size_ratio_g1m_p,
        snr_g1m_p,
        e1_g1m_p,
        statistic="sum",
        bins=bins,
    )

    count_g1p_m, _, _, _ = stats.binned_statistic_2d(
        size_ratio_g1p_m,
        snr_g1p_m,
        None,
        statistic="count",
        bins=bins,
    )
    count_g1m_m, _, _, _ = stats.binned_statistic_2d(
        size_ratio_g1m_m,
        snr_g1m_m,
        None,
        statistic="count",
        bins=bins,
    )
    e1_g1p_m, _, _, _ = stats.binned_statistic_2d(
        size_ratio_g1p_m,
        snr_g1p_m,
        e1_g1p_m,
        statistic="sum",
        bins=bins,
    )
    e1_g1m_m, _, _, _ = stats.binned_statistic_2d(
        size_ratio_g1m_m,
        snr_g1m_m,
        e1_g1m_m,
        statistic="sum",
        bins=bins,
    )

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

    # return ellipticity_p, responsivity_p, weight_p, count_p, tile_area_p, ellipticity_m, responsivity_m, weight_m, count_m, tile_area_m
    return \
        ellipticity_p, weight_p, count_p, tile_area_p, \
        e1_g1p_p, count_g1p_p, e1_g1m_p, count_g1m_p, \
        ellipticity_m, weight_m, count_m, tile_area_m, \
        e1_g1p_m, count_g1p_m, e1_g1m_m, count_g1m_m


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

    bins = (
        np.geomspace(0.5, 5, 20),
        np.geomspace(10, 1000, 20)
    )

    hf = h5py.File(
        "/dvs_ro/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        # "/global/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        mode="r",
        locking=False
    )
    dset = hf["mdet"]["noshear"]
    dset_1p = hf["mdet"]["1p"]
    dset_1m = hf["mdet"]["1m"]

    mdet_mask = util.load_mdet_mask()
    mdet_area = mdet_mask.get_valid_area()
    mdet_weight = weights.get_shear_weights(dset)

    ellipticity = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    responsivity = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    weight = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    count = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    for sl in dset["patch_num"].iter_chunks():
        print(f"reading slice {sl} of mdet (ns)")
        size_ratio = dset["gauss_T_ratio"][sl]
        snr = dset["gauss_s2n"][sl]

        values = np.hypot(
            dset["gauss_g_1"][sl],
            dset["gauss_g_2"][sl]
        )

        _ellipticity, _, _, _ = stats.binned_statistic_2d(
            size_ratio,
            snr,
            values,
            statistic="sum",
            bins=bins,
        )
        _weight, _, _, _ = stats.binned_statistic_2d(
            size_ratio,
            snr,
            mdet_weight[sl],
            statistic="sum",
            bins=bins,
        )
        _count, _, _, _ = stats.binned_statistic_2d(
            size_ratio,
            snr,
            None,
            statistic="count",
            bins=bins,
        )

        ellipticity = np.nansum([ellipticity, _ellipticity], axis=0)
        weight = np.nansum([weight, _weight], axis=0)
        count = np.nansum([count, _count], axis=0)

    e1_1p = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    count_1p = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    for sl in dset_1p["patch_num"].iter_chunks():
        print(f"reading slice {sl} of mdet (1p)")
        size_ratio_1p = dset_1p["gauss_T_ratio"][sl]
        snr_1p = dset_1p["gauss_s2n"][sl]
        values = dset_1p["gauss_g_1"][sl]
        _e1_1p, _, _, _ = stats.binned_statistic_2d(
            size_ratio_1p,
            snr_1p,
            values,
            statistic="sum",
            bins=bins,
        )
        _count_1p, _, _, _ = stats.binned_statistic_2d(
            size_ratio_1p,
            snr_1p,
            None,
            statistic="count",
            bins=bins,
        )
        e1_1p = np.nansum([e1_1p, _e1_1p], axis=0)
        count_1p = np.nansum([count_1p, _count_1p], axis=0)

    e1_1m = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    count_1m = np.zeros(
        (len(bins[0]) - 1, len(bins[1]) - 1)
    )
    for sl in dset_1m["patch_num"].iter_chunks():
        print(f"reading slice {sl} of mdet (1m)")
        size_ratio_1m = dset_1m["gauss_T_ratio"][sl]
        snr_1m = dset_1m["gauss_s2n"][sl]
        values = dset_1m["gauss_g_1"][sl]
        _e1_1m, _, _, _ = stats.binned_statistic_2d(
            size_ratio_1m,
            snr_1m,
            values,
            statistic="sum",
            bins=bins,
        )
        _count_1m, _, _, _ = stats.binned_statistic_2d(
            size_ratio_1m,
            snr_1m,
            None,
            statistic="count",
            bins=bins,
        )
        e1_1m = np.nansum([e1_1m, _e1_1m], axis=0)
        count_1m = np.nansum([count_1m, _count_1m], axis=0)

    e1_1p = e1_1p / count_1p
    e1_1m = e1_1m / count_1m
    responsivity = (e1_1p - e1_1m) / (2 * 0.01)

    # ellipticity = ellipticity / count / mdet_area
    ellipticity = ellipticity / count
    weight = weight / count
    count = count / mdet_area

    hf.close()

    jobs = [
        joblib.delayed(accumulate_file_pair)(pdict=sims["plus"], mdict=sims["minus"], bins=bins, tile=tile, mdet_mask=mdet_mask)
        for tile, seeds in pairs.items()
        for seed, sims in seeds.items()
    ]
    if args.fast:
        jobs = jobs[:2]
    print(f"Processing {len(jobs)} paired simulations ({ntiles} tiles)")

    ellipticity_p = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    weight_p = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    count_p = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    area_p = 0

    e1_g1p_p = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    count_g1p_p = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    e1_g1m_p = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    count_g1m_p = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))

    ellipticity_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    responsivity_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    weight_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    count_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    area_m = 0

    e1_g1p_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    count_g1p_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    e1_g1m_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))
    count_g1m_m = np.zeros((len(bins[0]) - 1, len(bins[1]) - 1))

    with joblib.Parallel(n_jobs=args.n_jobs, backend="loky", verbose=10) as par:
        # d = par(jobs)
        for res in par(jobs):
            ellipticity_p = np.nansum([ellipticity_p, res[0]], axis=0)
            weight_p = np.nansum([weight_p, res[1]], axis=0)
            count_p = np.nansum([count_p, res[2]], axis=0)
            area_p = np.nansum([area_p, res[3]], axis=0)

            e1_g1p_p = np.nansum([e1_g1p_p, res[4]], axis=0)
            count_g1p_p = np.nansum([count_p, res[5]], axis=0)
            e1_g1m_p = np.nansum([e1_g1m_p, res[6]], axis=0)
            count_g1m_p = np.nansum([count_p, res[7]], axis=0)

            ellipticity_m = np.nansum([ellipticity_m, res[8]], axis=0)
            weight_m = np.nansum([weight_m, res[9]], axis=0)
            count_m = np.nansum([count_m, res[10]], axis=0)
            area_m = np.nansum([area_m, res[11]], axis=0)

            e1_g1p_m = np.nansum([e1_g1p_p, res[12]], axis=0)
            count_g1p_m = np.nansum([count_p, res[13]], axis=0)
            e1_g1m_m = np.nansum([e1_g1m_p, res[14]], axis=0)
            count_g1m_m = np.nansum([count_p, res[15]], axis=0)

    ellipticity_p = ellipticity_p / count_p
    weight_p = weight_p / count_p
    count_p = count_p / area_p

    e1_1p_p = e1_g1p_p / count_g1p_p
    e1_1m_p = e1_g1m_p / count_g1m_p
    responsivity_p = (e1_1p_p - e1_1m_p) / (2 * 0.01)

    ellipticity_m = ellipticity_m / count_m
    weight_m = weight_m / count_m
    count_m = count_m / area_m

    e1_1p_m = e1_g1p_m / count_g1p_m
    e1_1m_m = e1_g1m_m / count_g1m_m
    responsivity_m = (e1_1p_m - e1_1m_m) / (2 * 0.01)

    # ellipticity_p, ellipticity_m = np.nanmean(d, axis=0)
    # ellipticity_p, count_p, ellipticity_m, count_m = np.nanmean(d, axis=0)
    # ellipticity_sims = np.nanmean([ellipticity_p / count_p / area_p, ellipticity_m / count_m / area_m], axis=0)
    # count_sims = np.nanmean([count_p / area_p, count_m / area_m], axis=0)
    count_sims = np.nanmean([count_p, count_m], axis=0)
    ellipticity_sims = np.nanmean([ellipticity_p, ellipticity_m], axis=0)
    responsivity_sims = np.nanmean([responsivity_p, responsivity_m], axis=0)
    weight_sims = np.nanmean([weight_p, weight_m], axis=0)

    count_label = "$counts / deg^2$"
    ellipticity_label = "$\\sqrt{\\langle e^2 \\rangle}$"
    responsivity_label = "$\\langle R \\rangle$"
    weight_label = "shear weight"

    # percentiles = [0.3, 0.5, 0.7, 0.9]
    percentiles = 1.0 - np.exp(-0.5 * np.array([1.5, 2.0, 2.5, 3.0]) ** 2)
    count_levels = util.get_levels(count, percentiles=percentiles)
    ellipticity_levels = util.get_levels(ellipticity, percentiles=percentiles)
    responsivity_levels = util.get_levels(responsivity, percentiles=percentiles)
    weight_levels = util.get_levels(weight, percentiles=percentiles)

    cmap_mdet = "des-y6-mdet"
    cmap_sims = "des-y6-sims"

    count_norm = colors.Normalize()
    ellipticity_norm = colors.Normalize()
    responsivity_norm = colors.Normalize()
    weight_norm = colors.Normalize()

    plotting.setup()
    # fig, axs = plt.subplots(3, 3, sharex="row", sharey="row")
    fig, axs = plotting.make_axes(
        4, 3,
        width=2,
        height=2,
        x_margin=1,
        y_margin=1/2,
        margin_top=1,
        gutter=1,
        y_gutter=0.5,
        fig_width=10,
        fig_height=11,
        sharex="all",
        sharey="all",
    )

    # counts

    pcm = axs[0, 0].pcolormesh(
        bins[0],
        bins[1],
        count.T,
        norm=count_norm,
        cmap=cmap_mdet,
        alpha=0.5,
    )
    contours = plotting.contour(axs[0, 0], count, bins, norm=count_norm, levels=count_levels, cmap=cmap_mdet)
    # axs[0, 0].set_xlabel("gauss_T_ratio")
    axs[0, 0].set_ylabel("gauss_s2n")
    axs[0, 0].set_title("mdet")
    axs[0, 0].set_xscale("log")
    axs[0, 0].set_yscale("log")
    plotting.add_colorbar(axs[0, 0], pcm, label=count_label)
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     # f"${{{p}}} \\%$"
    #     # for p in percentiles
    #      f"${{{util.get_percentile(count, level):.2f}}} \\%$"
    #      for level in count_levels
    # ]
    # axs[0, 0].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    pcm = axs[0, 1].pcolormesh(
        bins[0],
        bins[1],
        count_sims.T,
        norm=count_norm,
        cmap=cmap_sims,
        alpha=0.5,
    )
    contours = plotting.contour(axs[0, 1], count_sims, bins, norm=count_norm, levels=count_levels, cmap=cmap_sims)
    # axs[0, 1].set_xlabel("gauss_T_ratio")
    # axs[0, 1].set_ylabel("gauss_s2n")
    axs[0, 1].set_title("sims")
    plotting.add_colorbar(axs[0, 1], pcm, label=count_label)
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     # f"${{{p}}} \\%$"
    #     # for p in percentiles
    #      f"${{{util.get_percentile(count_sims, level):.2f}}} \\%$"
    #      for level in count_levels
    # ]
    # axs[0, 1].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    contours = plotting.contour(axs[0, 2], count, bins, norm=count_norm, levels=count_levels, cmap=cmap_mdet)
    contours = plotting.contour(axs[0, 2], count_sims, bins, norm=count_norm, levels=count_levels, cmap=cmap_sims)
    # axs[0, 2].set_xlabel("gauss_T_ratio")
    # axs[0, 2].set_ylabel("gauss_s2n")

    # ellipticity

    pcm = axs[1, 0].pcolormesh(
        bins[0],
        bins[1],
        ellipticity.T,
        norm=ellipticity_norm,
        cmap=cmap_mdet,
        alpha=0.5,
    )
    contours = plotting.contour(axs[1, 0], ellipticity, bins, norm=ellipticity_norm, levels=ellipticity_levels, cmap=cmap_mdet)
    # axs[1, 0].set_xlabel("gauss_T_ratio")
    axs[1, 0].set_ylabel("gauss_s2n")
    # axs[1, 0].set_title("mdet")
    axs[1, 0].set_xscale("log")
    axs[1, 0].set_yscale("log")
    plotting.add_colorbar(axs[1, 0], pcm, label=ellipticity_label)
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     # f"${{{p}}} \\%$"
    #     # for p in percentiles
    #      f"${{{util.get_percentile(ellipticity, level):.2f}}} \\%$"
    #      for level in ellipticity_levels
    # ]
    # axs[1, 0].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    pcm = axs[1, 1].pcolormesh(
        bins[0],
        bins[1],
        ellipticity_sims.T,
        norm=ellipticity_norm,
        cmap=cmap_sims,
        alpha=0.5,
    )
    contours = plotting.contour(axs[1, 1], ellipticity_sims, bins, norm=ellipticity_norm, levels=ellipticity_levels, cmap=cmap_sims)
    # axs[1, 1].set_xlabel("gauss_T_ratio")
    # axs[1, 1].set_ylabel("gauss_s2n")
    # axs[1, 1].set_title("sims")
    plotting.add_colorbar(axs[1, 1], pcm, label=ellipticity_label)
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     # f"${{{p}}} \\%$"
    #     # for p in percentiles
    #      f"${{{util.get_percentile(ellipticity_sims, level):.2f}}} \\%$"
    #      for level in ellipticity_levels
    # ]
    # axs[1, 1].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    contours = plotting.contour(axs[1, 2], ellipticity, bins, norm=ellipticity_norm, levels=ellipticity_levels, cmap=cmap_mdet)
    contours = plotting.contour(axs[1, 2], ellipticity_sims, bins, norm=ellipticity_norm, levels=ellipticity_levels, cmap=cmap_sims)
    # axs[1, 2].set_xlabel("gauss_T_ratio")
    # axs[1, 2].set_ylabel("gauss_s2n")

    # responsivity

    pcm = axs[2, 0].pcolormesh(
        bins[0],
        bins[1],
        responsivity.T,
        norm=responsivity_norm,
        cmap=cmap_mdet,
        alpha=0.5,
    )
    contours = plotting.contour(axs[2, 0], responsivity, bins, norm=responsivity_norm, levels=responsivity_levels, cmap=cmap_mdet)
    # axs[2, 0].set_xlabel("gauss_T_ratio")
    axs[2, 0].set_ylabel("gauss_s2n")
    # axs[2, 0].set_title("mdet")
    axs[2, 0].set_xscale("log")
    axs[2, 0].set_yscale("log")
    plotting.add_colorbar(axs[2, 0], pcm, label=responsivity_label)
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     # f"${{{p}}} \\%$"
    #     # for p in percentiles
    #      f"${{{util.get_percentile(ellipticity, level):.2f}}} \\%$"
    #      for level in ellipticity_levels
    # ]
    # axs[2, 0].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    pcm = axs[2, 1].pcolormesh(
        bins[0],
        bins[1],
        responsivity_sims.T,
        norm=responsivity_norm,
        cmap=cmap_sims,
        alpha=0.5,
    )
    contours = plotting.contour(axs[2, 1], responsivity_sims, bins, norm=responsivity_norm, levels=responsivity_levels, cmap=cmap_sims)
    # axs[2, 1].set_xlabel("gauss_T_ratio")
    # axs[2, 1].set_ylabel("gauss_s2n")
    # axs[2, 1].set_title("sims")
    plotting.add_colorbar(axs[2, 1], pcm, label=responsivity_label)
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     # f"${{{p}}} \\%$"
    #     # for p in percentiles
    #      f"${{{util.get_percentile(responsivity_sims, level):.2f}}} \\%$"
    #      for level in responsivity_levels
    # ]
    # axs[2, 1].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    contours = plotting.contour(axs[2, 2], responsivity, bins, norm=responsivity_norm, levels=responsivity_levels, cmap=cmap_mdet)
    contours = plotting.contour(axs[2, 2], responsivity_sims, bins, norm=responsivity_norm, levels=responsivity_levels, cmap=cmap_sims)
    # axs[2, 2].set_xlabel("gauss_T_ratio")
    # axs[2, 2].set_ylabel("gauss_s2n")

    # weights

    pcm = axs[3, 0].pcolormesh(
        bins[0],
        bins[1],
        weight.T,
        norm=weight_norm,
        cmap=cmap_mdet,
        alpha=0.5,
    )
    contours = plotting.contour(axs[3, 0], weight, bins, norm=weight_norm, levels=weight_levels, cmap=cmap_mdet)
    axs[3, 0].set_xlabel("gauss_T_ratio")
    axs[3, 0].set_ylabel("gauss_s2n")
    # axs[3, 0].set_title("mdet")
    axs[3, 0].set_xscale("log")
    axs[3, 0].set_yscale("log")
    plotting.add_colorbar(axs[3, 0], pcm, label=weight_label)
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     # f"${{{p}}} \\%$"
    #     # for p in percentiles
    #      f"${{{util.get_percentile(weight, level):.2f}}} \\%$"
    #      for level in weight_levels
    # ]
    # axs[2, 0].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    pcm = axs[3, 1].pcolormesh(
        bins[0],
        bins[1],
        weight_sims.T,
        norm=weight_norm,
        cmap=cmap_sims,
        alpha=0.5,
    )
    contours = plotting.contour(axs[3, 1], weight_sims, bins, norm=weight_norm, levels=weight_levels, cmap=cmap_sims)
    axs[3, 1].set_xlabel("gauss_T_ratio")
    # axs[3, 1].set_ylabel("gauss_s2n")
    # axs[3, 1].set_title("sims")
    plotting.add_colorbar(axs[3, 1], pcm, label=weight_label)
    # legend_elements, _ = contours.legend_elements()
    # legend_labels = [
    #     # f"${{{p}}} \\%$"
    #     # for p in percentiles
    #      f"${{{util.get_percentile(weight_sims, level):.2f}}} \\%$"
    #      for level in weight_levels
    # ]
    # axs[2, 1].legend(
    #     legend_elements,
    #     legend_labels,
    #     loc="upper right",
    # )

    contours = plotting.contour(axs[3, 2], weight, bins, norm=weight_norm, levels=weight_levels, cmap=cmap_mdet)
    contours = plotting.contour(axs[3, 2], weight_sims, bins, norm=weight_norm, levels=weight_levels, cmap=cmap_sims)
    axs[3, 2].set_xlabel("gauss_T_ratio")
    # axs[3, 2].set_ylabel("gauss_s2n")

    axs[0, 0].xaxis.set_major_formatter(ticker.ScalarFormatter())
    axs[0, 0].xaxis.set_minor_formatter(ticker.NullFormatter())
    axs[0, 0].xaxis.set_major_locator(ticker.MaxNLocator(nbins="auto"))

    fig.suptitle(config_name)

    plt.show()


if __name__ == "__main__":
    main()
