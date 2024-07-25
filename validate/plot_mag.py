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


def accumulate_pair(dset_plus, dset_minus, *, tile, band, bins, mdet_mask):
    # FIXME surely we can improve on this...
    # cuts_p = dset_plus["tilename"][:].astype(str) == tile
    # cuts_m = dset_minus["tilename"][:].astype(str) == tile
    data_p = load_file(dset_plus)
    data_m = load_file(dset_minus)
    cuts_p = slice(-1)
    cuts_m = slice(-1)
    # cuts_p = data_p["mdet_flags"] == 0
    # cuts_m = data_m["mdet_flags"] == 0

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

    # hf_plus = h5py.File(
    #     imsim_path / "plus" / "metadetect_cutsv6_all.h5",
    #     mode="r",
    #     locking=False,
    # )
    # hf_minus = h5py.File(
    #     imsim_path / "minus" / "metadetect_cutsv6_all.h5",
    #     mode="r",
    #     locking=False,
    # )


    # dset_plus = hf_plus["mdet"]["noshear"]
    # dset_minus = hf_minus["mdet"]["noshear"]

    # tilenames = np.unique(dset_plus["tilename"]).astype(str)
    # np.testing.assert_equal(tilenames, np.unique(dset_minus["tilename"]).astype(str))
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
        # TODO
        # for sl in dset["patch_num"].iter_chunks():
        #     print(f"reading slice {sl} of mdet")
        #     _hist = mag_hist(dset, sl, band, bins)
        #     hist += _hist
        # TODO
        mdet_area = 0
        for _mdet_file in Path("/global/cfs/cdirs/des/y6-shear-catalogs/Y6A2_METADETECT_V6_UNBLINDED/tiles/").glob("*.fits"):
            _d = load_file(_mdet_file, cuts=True)
            _cuts = slice(-1)
            _hist = mag_hist(_d, _cuts, band, bins)
            hist += _hist
            tile_name = _mdet_file.name.split("_")[0]
            _tile_area = util.get_tile_area(
                tile_name,
                "r",
                mdet_mask=mdet_mask,
                border=False,
            )
            mdet_area += _tile_area
        # TODO

        hist /= mdet_area

        hist_p = np.zeros(len(bins) - 1)
        hist_m = np.zeros(len(bins) - 1)
        area_p = 0
        area_m = 0
        jobs = [
            joblib.delayed(accumulate_pair)(catalogs[tile]["plus"], catalogs[tile]["minus"], tile=tile, band=band, bins=bins, mdet_mask=mdet_mask)
            for tile in catalogs.keys()
        ]
        with joblib.Parallel(n_jobs=args.n_jobs, backend="loky", verbose=10) as par:
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
