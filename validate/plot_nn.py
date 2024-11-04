import argparse
from pathlib import Path
import functools
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

import smatch
import healsparse
import des_y6utils

import util
import plotting
import selections


NBINS = 100


def load_file(fname):
    fits = fitsio.FITS(fname)
    w = fits[1].where("mdet_step == \"noshear\"")
    data = fits[1][w]

    mask = selections.get_selection(data)

    return data[mask]


# def accumulate_pair(*, pdict, mdict, tile, bins, mdet_mask):
def accumulate_pair(dset_plus, dset_minus, bins, mdet_mask, tile):
    # plus
    sel_p = dset_plus["tilename"][:].astype(str) == tile

    matcher_p = smatch.Matcher(dset_plus["ra"][sel_p], dset_plus["dec"][sel_p])
    indices_p, distances_p = matcher_p.query_knn(matcher_p.lon, matcher_p.lat, k=2, return_distances=True)
    dnn_p = distances_p[:, 1] * 60 * 60
    del matcher_p, indices_p, distances_p

    hist_p, _ = np.histogram(dnn_p, bins=bins)
    del dnn_p

    tile_map_p = util.get_tile_mask(
        tile,
        "r",
        shear="plus",
        mdet_mask=mdet_mask,
    )
    tile_area_p = tile_map_p.get_valid_area(degrees=True)

    n_sample_p = np.sum(sel_p)

    rand_ra_p, rand_dec_p = healsparse.make_uniform_randoms(tile_map_p, n_sample_p)
    del tile_map_p

    rand_matcher_p = smatch.Matcher(rand_ra_p, rand_dec_p)
    rand_indices_p, rand_distances_p = rand_matcher_p.query_knn(rand_matcher_p.lon, rand_matcher_p.lat, k=2, return_distances=True)
    rand_dnn_p = rand_distances_p[:, 1] * 60 * 60
    del rand_matcher_p, rand_indices_p, rand_distances_p

    rand_hist_p, _ = np.histogram(rand_dnn_p, bins=bins)
    del rand_dnn_p

    # minus
    sel_m = dset_minus["tilename"][:].astype(str) == tile

    matcher_m = smatch.Matcher(dset_minus["ra"][sel_m], dset_minus["dec"][sel_m])
    indices_m, distances_m = matcher_m.query_knn(matcher_m.lon, matcher_m.lat, k=2, return_distances=True)
    dnn_m = distances_m[:, 1] * 60 * 60
    del matcher_m, indices_m, distances_m

    hist_m, _ = np.histogram(dnn_m, bins=bins)
    del dnn_m

    tile_map_m = util.get_tile_mask(
        tile,
        "r",
        shear="minus",
        mdet_mask=mdet_mask,
    )
    tile_area_m = tile_map_m.get_valid_area(degrees=True)

    n_sample_m = np.sum(sel_m)

    rand_ra_m, rand_dec_m = healsparse.make_uniform_randoms(tile_map_m, n_sample_m)
    del tile_map_m

    rand_matcher_m = smatch.Matcher(rand_ra_m, rand_dec_m)
    rand_indices_m, rand_distances_m = rand_matcher_m.query_knn(rand_matcher_m.lon, rand_matcher_m.lat, k=2, return_distances=True)
    rand_dnn_m = rand_distances_m[:, 1] * 60 * 60
    del rand_matcher_m, rand_indices_m, rand_distances_m

    rand_hist_m, _ = np.histogram(rand_dnn_m, bins=bins)
    del rand_dnn_m

    return hist_p, rand_hist_p, tile_area_p, hist_m, rand_hist_m, tile_area_m


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "imsim_dir",
        type=str,
        help="Image simulation output directory",
    )
    parser.add_argument(
        "--n_jobs",
        type=int,
        required=False,
        default=8,
        help="Number of joblib jobs [int]",
    )
    parser.add_argument(
        "--mdet",
        action="store_true",
        help="whether to run on mdet cat",
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
    # pairs = util.gather_sims(args.imsim_dir)

    # ntiles = len([p for p in pairs.values() if p])

    hf = h5py.File(
        "/dvs_ro/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        # "/global/cfs/projectdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6/metadetect_cutsv6_all_blinded.h5",
        mode="r",
        locking=False
    )
    dset = hf["mdet"]["noshear"]

    fname_p = imsim_path / "g1_slice=0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0" / "metadetect_cutsv6_all.h5"
    hf_plus = h5py.File(
        fname_p,
        mode="r",
        locking=False,
    )

    fname_m = imsim_path / "g1_slice=-0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0" / "metadetect_cutsv6_all.h5"
    hf_minus = h5py.File(
        fname_m,
        mode="r",
        locking=False,
    )

    dset_plus = hf_plus["mdet"]["noshear"]
    dset_minus = hf_minus["mdet"]["noshear"]

    tilenames_p = np.unique(dset_plus["tilename"]).astype(str)
    tilenames_m = np.unique(dset_minus["tilename"]).astype(str)
    # np.testing.assert_equal(tilenames_p, tilenames_m)
    tilenames = np.intersect1d(tilenames_p, tilenames_m)

    mdet_mask = util.load_mdet_mask()
    mdet_area = mdet_mask.get_valid_area()

    # bins = np.linspace(0, 1, NBINS)  # arcmin
    # bins = np.geomspace(1e-2, 1, NBINS)  # arcmin
    bins = np.geomspace(1e-2, 1, NBINS) * 60  # arcsec

    hist = np.zeros(
        len(bins) - 1
    )
    # for sl in dset["patch_num"].iter_chunks():
    #     matcher = smatch.Matcher(dset["ra"][sl], dset["dec"][sl])
    #     matches = matcher.query_knn(matcher.lon, matcher.lat, k=2, return_distances=True)
    #     dnn = matches[1][:, 1] * 60
    #     _hist, _ = np.histogram(dnn, bins=bins)
    #     hist += _hist

    #     # if args.fast:
    #     #     break
    if args.mdet:
        matcher = smatch.Matcher(dset["ra"], dset["dec"])
        indices, distances = matcher.query_knn(matcher.lon, matcher.lat, k=2, return_distances=True)
        dnn = distances[:, 1] * 60 * 60
        del matcher, indices, distances  # forecfully cleanup
        _hist, _ = np.histogram(dnn, bins=bins)
        hist += _hist

    hist /= mdet_area

    # jobs = [
    #     joblib.delayed(accumulate_pair)(pdict=sims["plus"], mdict=sims["minus"], tile=tile, bins=bins, mdet_mask=mdet_mask)
    #     for tile, seeds in pairs.items()
    #     for seed, sims in seeds.items()
    # ]
    # if args.fast:
    #     jobs = jobs[:2]
    # print(f"Processing {len(jobs)} paired simulations")

    hist_p = np.zeros(len(bins) - 1)
    rand_hist_p = np.zeros(len(bins) - 1)
    area_p = 0
    hist_m = np.zeros(len(bins) - 1)
    rand_hist_m = np.zeros(len(bins) - 1)
    area_m = 0
    # with joblib.Parallel(n_jobs=args.n_jobs, backend="loky", verbose=10) as par:
    #     # d = par(jobs)
    #     for res in par(jobs):
    #         hist_p += res[0]
    #         rand_hist_p += res[1]
    #         area_p += res[2]
    #         hist_m += res[3]
    #         rand_hist_m += res[4]
    #         area_m += res[5]
    for res in tqdm.tqdm(
        map(
            functools.partial(accumulate_pair, dset_plus, dset_minus, bins, mdet_mask),
            tilenames,
        ),
        total=len(tilenames),
        ncols=80,
    ):
        hist_p += res[0]
        rand_hist_p += res[1]
        area_p += res[2]
        hist_m += res[3]
        rand_hist_m += res[4]
        area_m += res[5]

    # hist_sims = np.nanmean([hist_p, hist_m], axis=0)
    # hist_sims /= np.nanmean([area_p, area_m])
    hist_sims = np.nanmean([hist_p / area_p, hist_m / area_m], axis=0)
    hist_rand = np.nanmean([rand_hist_p / area_p, rand_hist_m / area_m], axis=0)

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


    if args.mdet:
        axs[0, 0].stairs(
            hist,
            edges=bins,
            color=plotting.mdet_color,
            label="mdet",
        )
    axs[0, 0].stairs(
        hist_rand,
        edges=bins,
        color="gray",
        label="rand",
    )
    axs[0, 0].stairs(
        hist_sims,
        edges=bins,
        color=plotting.sims_color,
        label="sims",
    )
    axs[0, 0].set_xlabel("nearest neighbor distance [arcsec]")
    axs[0, 0].set_ylabel("source density [$counts / deg^2$]")
    axs[0, 0].legend(loc="upper left")
    axs[0, 0].set_xscale("log")
    axs[0, 0].xaxis.set_major_formatter(ticker.ScalarFormatter())
    # axs[0, 0].xaxis.set_minor_formatter(ticker.ScalarFormatter())
    # axs[0, 0].set_yscale("log")
    axs[0, 0].grid()
    axs[0, 0].set_ylim(0, None)

    fig.suptitle(config_name)


    plt.show()


if __name__ == "__main__":
    main()
