import argparse
from pathlib import Path
import os

import joblib
import tqdm
import numpy as np
import fitsio

import des_y6utils


def grid_file(*, fname, ngrid):
    d = fitsio.read(fname)

    dgrid = 1e4/ngrid
    xind = np.floor(d["x"] / dgrid)
    yind = np.floor(d["y"] / dgrid)
    gind = yind * ngrid + xind

    msk = (
        ((d["mask_flags"] & (~16)) == 0)
        &
        (d["gauss_flags"] == 0)
        &
        (d["gauss_psf_flags"] == 0)
        &
        (d["gauss_obj_flags"] == 0)
        &
        (d["psfrec_flags"] == 0)
        &
        (d["gauss_T_ratio"] > 0.5)
        & (d["gauss_s2n"] > 10)
    )
    # msk = des_y6utils.mdet.make_mdet_cuts(d, "5")
    msk &= d["mfrac"] < 0.01

    vals = []

    ugind = np.unique(gind)
    for _gind in range(ngrid*ngrid):
        gmsk = msk & (_gind == gind)
        if np.any(gmsk):
            sval = []
            for shear in ["noshear", "1p", "1m"]:
                sgmsk = gmsk & (d["mdet_step"] == shear)
                if np.any(sgmsk):
                    sval.append(np.mean(d["gauss_g_1"][sgmsk]))
                    sval.append(np.sum(sgmsk))
                else:
                    sval.append(np.nan)
                    sval.append(np.nan)
            vals.append(tuple(sval + [_gind]))
        else:
            vals.append(tuple([np.nan] * 6 + [_gind]))

    return np.array(vals, dtype=[("g1", "f8"), ("ng1", "f8"), ("g1p", "f8"), ("ng1p", "f8"), ("g1m", "f8"), ("ng1m", "f8"), ("grid_ind", "i4")])


def grid_file_pair(*, fplus, fminus, ngrid):
    dp = grid_file(fname=fplus, ngrid=ngrid)
    dm = grid_file(fname=fminus, ngrid=ngrid)

    assert np.all(dp["grid_ind"] == dm["grid_ind"])

    dt = []
    for tail in ["_p", "_m"]:
        for name in dp.dtype.names:
            if name != "grid_ind":
                dt.append((name + tail, "f8"))
    dt.append(("grid_ind", "i4"))
    d = np.zeros(ngrid * ngrid, dtype=dt)
    for _d, tail in [(dp, "_p"), (dm, "_m")]:
        for name in dp.dtype.names:
            if name != "grid_ind":
                d[name + tail] = _d[name]
    d["grid_ind"] = dp["grid_ind"]

    return d

def compute_shear_pair(d):
    g1_p = np.nansum(d["g1_p"] * d["ng1_p"]) / np.nansum(d["ng1_p"])
    g1p_p = np.nansum(d["g1p_p"] * d["ng1p_p"]) / np.nansum(d["ng1p_p"])
    g1m_p = np.nansum(d["g1m_p"] * d["ng1m_p"]) / np.nansum(d["ng1m_p"])
    R11_p = (g1p_p - g1m_p) / 0.02

    g1_m = np.nansum(d["g1_m"] * d["ng1_m"]) / np.nansum(d["ng1_m"])
    g1p_m = np.nansum(d["g1p_m"] * d["ng1p_m"]) / np.nansum(d["ng1p_m"])
    g1m_m = np.nansum(d["g1m_m"] * d["ng1m_m"]) / np.nansum(d["ng1m_m"])
    R11_m = (g1p_m - g1m_m) / 0.02

    return (g1_p - g1_m) / (R11_p + R11_m)


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
    return parser.parse_args()


def main():

    args = get_args()

    pairs = {}

    tile_dirs = Path(args.imsim_dir).glob("*")

    for tile_dir in tile_dirs:
        tile = tile_dir.stem
        # FIXME one tile test for now..
        # if tile != "DES0050-2249":
        #     continue
        # print(f"Tile: {tile}")

        run_dirs = tile_dir.glob("*")

        for run_dir in run_dirs:
            run = run_dir.stem
            # print(f"\tRun: {run}")

            fname_plus = run_dir / "plus" / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000.fits"
            fname_minus = run_dir / "minus" / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000.fits"

            if not (
                os.path.exists(fname_plus)
                and os.path.exists(fname_minus)
            ):
                continue

            pairs[f"{tile}_{run}"] = (fname_plus, fname_minus)

    print(len(pairs))

    jobs = [
        joblib.delayed(grid_file_pair)(fplus=pfile, fminus=mfile, ngrid=10)
        for pfile, mfile in pairs.values()
    ]

    with joblib.Parallel(n_jobs=8, backend="loky", verbose=10) as par:
        d = par(jobs)

    d = np.concatenate(d, axis=0)

    ns = 1000  # number of bootstrap resamples
    rng = np.random.RandomState(seed=args.seed)

    mean = compute_shear_pair(d)/0.02-1
    bootstrap = []
    for i in tqdm.trange(ns, ncols=80):
        rind = rng.choice(d.shape[0], size=d.shape[0], replace=True)
        bootstrap.append(compute_shear_pair(d[rind])/0.02-1)

    print("m = %0.3f +/- %0.3f [1e-3, 3-sigma]" % (mean/1e-3, np.std(bootstrap)*3/1e-3))
    print("m = %0.3e +/- %0.3e [3-sigma]" % (mean, np.std(bootstrap) * 3))
    print("m: (%0.3e, %0.3e) [3-sigma]" % (mean - np.std(bootstrap) * 3, mean + np.std(bootstrap) * 3))

if __name__ == "__main__":
    main()
