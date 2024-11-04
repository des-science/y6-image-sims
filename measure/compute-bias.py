import argparse
from pathlib import Path

import tqdm
import numpy as np
import h5py

import weights


SHEAR_STEPS = ["noshear", "1p", "1m", "2p", "2m"]


def concatenate_catalogs(data):
    _dp, _dm = np.stack(data, axis=1)
    dp = {
        shear_step: np.hstack(
            [_d[shear_step] for _d in _dp],
        )
        for shear_step in SHEAR_STEPS
    }
    dm = {
        shear_step: np.hstack(
            [_d[shear_step] for _d in _dm],
        )
        for shear_step in SHEAR_STEPS
    }
    return dp, dm


def process_file(*, dset, tile):
    mdet = dset["mdet"]

    res = {}
    for shear_step in SHEAR_STEPS:
        mdet_cat = mdet[shear_step]
        in_tile = mdet_cat["tilename"][:] == tile
        _w = weights.get_shear_weights(mdet_cat, in_tile)
        n = np.sum(_w)
        if n > 0:
            g1 = np.average(mdet_cat["gauss_g_1"][in_tile], weights=_w)
            g2 = np.average(mdet_cat["gauss_g_2"][in_tile], weights=_w)
        else:
            g1 = np.nan
            g2 = np.nan

        res[shear_step] = np.array(
            [(n, g1, g2)],
            dtype=[
                ("n", "f8"),
                ("g1", "f8"),
                ("g2", "f8"),
            ],
        )
    return res


def process_file_pair(dset_plus, dset_minus, *, tile):
    dp = process_file(dset=dset_plus, tile=tile)
    dm = process_file(dset=dset_minus, tile=tile)

    return dp, dm


def compute_shear_pair(dp, dm):
    g1_p = np.nansum(dp["noshear"]["g1"] * dp["noshear"]["n"]) / np.nansum(dp["noshear"]["n"])
    g1p_p = np.nansum(dp["1p"]["g1"] * dp["1p"]["n"]) / np.nansum(dp["1p"]["n"])
    g1m_p = np.nansum(dp["1m"]["g1"] * dp["1m"]["n"]) / np.nansum(dp["1m"]["n"])
    R11_p = (g1p_p - g1m_p) / 0.02

    g1_m = np.nansum(dm["noshear"]["g1"] * dm["noshear"]["n"]) / np.nansum(dm["noshear"]["n"])
    g1p_m = np.nansum(dm["1p"]["g1"] * dm["1p"]["n"]) / np.nansum(dm["1p"]["n"])
    g1m_m = np.nansum(dm["1m"]["g1"] * dm["1m"]["n"]) / np.nansum(dm["1m"]["n"])
    R11_m = (g1p_m - g1m_m) / 0.02

    g2_p = np.nansum(dp["noshear"]["g2"] * dp["noshear"]["n"]) / np.nansum(dp["noshear"]["n"])
    g2p_p = np.nansum(dp["2p"]["g2"] * dp["2p"]["n"]) / np.nansum(dp["2p"]["n"])
    g2m_p = np.nansum(dp["2m"]["g2"] * dp["2m"]["n"]) / np.nansum(dp["2m"]["n"])
    R22_p = (g2p_p - g2m_p) / 0.02

    g2_m = np.nansum(dm["noshear"]["g2"] * dm["noshear"]["n"]) / np.nansum(dm["noshear"]["n"])
    g2p_m = np.nansum(dm["2p"]["g2"] * dm["2p"]["n"]) / np.nansum(dm["2p"]["n"])
    g2m_m = np.nansum(dm["2m"]["g2"] * dm["2m"]["n"]) / np.nansum(dm["2m"]["n"])
    R22_m = (g2p_m - g2m_m) / 0.02

    # return (g1_p - g1_m) / (R11_p + R11_m) / 0.02 - 1., (g2_p + g2_m) / (R22_p + R22_m)
    # return (g1_p - g1_m) / (R11_p + R11_m) / 0.02 - 1., (g1_p + g1_m) / (R11_p + R11_m)
    return (
        (g1_p - g1_m) / (R11_p + R11_m) / 0.02 - 1.,  # m1
        (g1_p + g1_m) / (R11_p + R11_m),  # c1
        (g2_p + g2_m) / (R22_p + R22_m),  # c2
    )


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "catalogs",
        type=str,
        nargs=2,
        help="Image simulation output catalogs [plus, minus]",
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
        "--resample",
        type=str,
        required=False,
        default="jackknife",
        choices=["jackknife", "bootstrap"],
        help="Resample method [str]",
    )
    return parser.parse_args()


def main():

    args = get_args()

    resample = args.resample

    pairs = {}

    fname_p, fname_m = args.catalogs
    parts_p = Path(fname_p).parts
    parts_m = Path(fname_m).parts

    config_p = parts_p[-3]
    config_m = parts_m[-3]

    shear_p = parts_p[-2].split("__")
    shear_m = parts_m[-2].split("__")
    assert config_p == config_m

    hf_plus = h5py.File(
        fname_p,
        mode="r",
        locking=False,
    )

    hf_minus = h5py.File(
        fname_m,
        mode="r",
        locking=False,
    )

    tilenames_p = np.unique(hf_minus["mdet"]["noshear"]["tilename"][:])
    tilenames_m = np.unique(hf_minus["mdet"]["noshear"]["tilename"][:])
    tilenames = np.intersect1d(tilenames_p, tilenames_m)
    ntiles = len(tilenames)

    data = [
        process_file_pair(hf_plus, hf_minus, tile=tile)
        for tile in tqdm.tqdm(
            tilenames,
            total=ntiles,
            desc="processing",
            ncols=80,
        )
    ]

    print(f"Computing uncertainties via {resample}")
    if resample == "bootstrap":
        ns = 1000  # number of bootstrap resamples
        rng = np.random.RandomState(seed=args.seed)

        dp, dm = concatenate_catalogs(data)
        m_mean, c_mean_1, c_mean_2 = compute_shear_pair(dp, dm)

        print(f"Bootstrapping with {ns} resamples")
        bootstrap = []
        for i in tqdm.trange(ns, desc="bootstrap", ncols=80):
            rind = rng.choice(data.shape[0], size=data.shape[0], replace=True)
            _bootstrap = data[rind]
            _dp, _dm = concatenate_catalogs(_bootstrap)
            bootstrap.append(compute_shear_pair(_dp, _dm))

        bootstrap = np.array(bootstrap)
        m_std, c_std_1, c_std_2 = np.std(bootstrap, axis=0)

    elif resample == "jackknife":
        jackknife = []
        for i in tqdm.trange(len(data), desc="jackknife", ncols=80):
            _pre = data[:i]
            _post = data[i + 1:]
            _jackknife = _pre + _post
            _dp, _dm = concatenate_catalogs(_jackknife)
            jackknife.append(compute_shear_pair(_dp, _dm))

        _n = len(jackknife)
        # m_mean, c_mean_1, c_mean_2 = np.mean(jackknife, axis=0)
        jackknife_mean = np.mean(jackknife, axis=0)
        # jackknife_var = ((_n - 1) / _n) * np.sum(np.square(np.subtract(jackknife, jackknife_mean)), axis=0)
        jackknife_std = np.sqrt(((_n - 1) / _n) * np.sum(np.square(np.subtract(jackknife, jackknife_mean)), axis=0))

        m_mean, c_mean_1, c_mean_2 = jackknife_mean
        m_std, c_std_1, c_std_2 = jackknife_std

    print("\n")
    print(f"config:  {config_p}")
    print(f"plus:    {shear_p[0]}, {shear_p[1]}, {shear_p[2]}, {shear_p[3]}, {shear_p[4]}, {shear_p[5]}")
    print(f"minus:   {shear_m[0]}, {shear_m[1]}, {shear_m[2]}, {shear_m[3]}, {shear_m[4]}, {shear_m[5]}")
    print(f"| m mean | 3 * m std | c_1 mean | 3 * c_1 std | c_2 mean | 3 * c_2 std | # tiles |")
    print(f"| {m_mean:0.3e} | {3 * m_std:0.3e} | {c_mean_1:0.3e} | {3 * c_std_1:0.3e} | {c_mean_2:0.3e} | {3 * c_std_2:0.3e} | {ntiles} |")
    print("\n")


if __name__ == "__main__":
    main()
