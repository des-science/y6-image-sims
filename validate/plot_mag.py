import argparse
from pathlib import Path
import math
import os
import functools
import multiprocessing

import joblib
import tqdm
import h5py
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds
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


def process_data(dset, tile, func, *args, **kwargs):
    # with h5py.File(
    #     fname,
    #     mode="r",
    #     locking=False,
    # ) as hf:
    #     data = hf["mdet"]["noshear"]
    #     sel = data["tilename"][:].astype(str) == tile
    #     res = func(data, sel, *args, **kwargs)
    # ---
    sel = dset["tilename"][:].astype(str) == tile
    res = func(dset, sel, *args, **kwargs)

    return res


def accumulate_hist(dset, band, bins, mdet_mask, shear, tile):

    # data = load_file(dset)
    # cuts = data["mdet_flags"] == 0
    # data = data[cuts]
    # cuts = slice(None)
    # hist = mag_hist(data, cuts, band, bins)

    # ---

    hist = process_data(dset, tile, mag_hist, band, bins)

    tile_area = util.get_tile_area(
        tile,
        band,
        shear=shear,
        mdet_mask=mdet_mask,
    )

    return hist, tile_area


# def accumulate_pair(fname_p, fname_m, band, bins, mdet_mask, tile):
# def accumulate_pair(catalogs, band, bins, mdet_mask, tile):
def accumulate_pair(dset_plus, dset_minus, band, bins, mdet_mask, tile):
    # dset_plus = catalogs[tile]["plus"]
    # dset_minus = catalogs[tile]["minus"]

    # data_p = load_file(dset_plus)
    # cuts_p = data_p["mdet_flags"] == 0
    # hist_p = mag_hist(data_p, cuts_p, band, bins)

    # data_m = load_file(dset_minus)
    # cuts_m = data_m["mdet_flags"] == 0
    # hist_m = mag_hist(data_m, cuts_m, band, bins)

    # ---

    hist_p = process_data(dset_plus, tile, mag_hist, band, bins)
    hist_m = process_data(dset_minus, tile, mag_hist, band, bins)

    tile_area_p = util.get_tile_area(
        tile,
        band,
        shear="plus",
        mdet_mask=mdet_mask,
    )
    tile_area_m = util.get_tile_area(
        tile,
        band,
        shear="minus",
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
        "--n_jobs",
        type=int,
        required=False,
        default=8,
        help="Number of joblib jobs [int]",
    )
    return parser.parse_args()


def main():

    args = get_args()

    n_jobs = args.n_jobs
    pa.set_cpu_count(n_jobs)
    pa.set_io_thread_count(2 * n_jobs)

    # pairs = {}

    imsim_path = Path(args.imsim_dir)
    config_name = imsim_path.name
    # tile_dirs = imsim_path.glob("*")

    # TODO
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

    # ---
    plus_path = os.path.join(
        imsim_path,
        "g1_slice=0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0",
    )

    minus_path = os.path.join(
        imsim_path,
        "g1_slice=-0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0",
    )

    # predicate = (pc.field("mdet_step") == "noshear")

    # dset_plus = ds.dataset(plus_path).filter(predicate)
    # dset_minus = ds.dataset(minus_path).filter(predicate)

    # print(f"plus: {dset_plus.count_rows()} rows")
    # print(f"minus: {dset_minus.count_rows()} rows")

    # tilenames = util.get_tilenames(dset_plus, dset_minus)
    # print(f"{len(tilenames)} tiles")

    # ---

    # catalogs = util.gather_catalogs(imsim_path)
    # tilenames = list(catalogs.keys())
    # print(f"{len(tilenames)} tiles")

    # ---

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

    # fig, axs = plt.subplots(2, len(bands), sharex="row", sharey="row", constrained_layout=True, squeeze=False)
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
        # TODO
        for sl in tqdm.tqdm(
            dset["patch_num"].iter_chunks(),
            total=math.ceil(dset["patch_num"].len() / dset["patch_num"].chunks[0]),
            ncols=80,
        ):
            _hist = mag_hist(dset, sl, band, bins)
            hist += _hist
        # TODO
        # mdet_area = 0
        # for _mdet_file in Path("/global/cfs/cdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6_UNBLINDED/tiles/").glob("*.fits"):
        #     _d = load_file(_mdet_file, cuts=True)
        #     _cuts = slice(-1)
        #     _hist = mag_hist(_d, _cuts, band, bins)
        #     hist += _hist
        #     tile_name = _mdet_file.name.split("_")[0]
        #     _tile_area = util.get_tile_area(
        #         tile_name,
        #         "r",
        #         mdet_mask=mdet_mask,
        #         border=False,
        #     )
        #     mdet_area += _tile_area
        # TODO

        hist /= mdet_area

        hist_p = np.zeros(len(bins) - 1)
        hist_m = np.zeros(len(bins) - 1)
        area_p = 0
        area_m = 0
        # with multiprocessing.Pool(
        #     8,
        # ) as pool:
        #     results = pool.imap(
        #         functools.partial(accumulate_pair, fname_p, fname_m, band, bins, mdet_mask),
        #         (tilenames)
        #     )
        #     for res in track(results, total=len(tilenames)):
        #         hist_p += res[0]
        #         area_p += res[1]
        #         hist_m += res[2]
        #         area_m += res[3]
        # ---
        # with multiprocessing.Pool(
        #     args.n_jobs,
        # ) as pool:
        #     results = pool.imap(
        #         functools.partial(accumulate_pair, catalogs, band, bins, mdet_mask),
        #         tilenames,
        #     )
        #     for res in track(
        #         results,
        #         total=len(tilenames),
        #     ):
        #         hist_p += res[0]
        #         area_p += res[1]
        #         hist_m += res[2]
        #         area_m += res[3]
        # ---
        for res in tqdm.tqdm(
            map(
                functools.partial(accumulate_pair, dset_plus, dset_minus, band, bins, mdet_mask),
                tilenames,
            ),
            total=len(tilenames),
            ncols=80,
        ):
            hist_p += res[0]
            area_p += res[1]
            hist_m += res[2]
            area_m += res[3]
        # ---
        # for res in track(
        #     map(
        #         functools.partial(accumulate_hist, dset_plus, band, bins, mdet_mask, "plus"),
        #         tilenames,
        #     ),
        #     total=len(tilenames),
        # ):
        #     hist_p += res[0]
        #     area_p += res[1]
        # for res in track(
        #     map(
        #         functools.partial(accumulate_hist, dset_minus, band, bins, mdet_mask, "minus"),
        #         tilenames,
        #     ),
        #     total=len(tilenames),
        # ):
        #     hist_m += res[0]
        #     area_m += res[1]

        # hist_sims = np.nanmean([hist_p, hist_m], axis=0)
        # hist_sims /= np.nanmean([area_p, area_m])
        # ---
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
