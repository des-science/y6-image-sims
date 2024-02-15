import argparse
from pathlib import Path
import os

import joblib
import tqdm
import numpy as np
import fitsio

import des_y6utils


def grid_file(*, fname, ngrid, mfrac=0.1):
    d = fitsio.read(fname)

    dgrid = 1e4 / ngrid
    xind = np.floor(d["x"] / dgrid)
    yind = np.floor(d["y"] / dgrid)
    gind = yind * ngrid + xind

    msk = (
        ((d["mask_flags"] & (~16)) == 0)
        & (d["gauss_flags"] == 0)
        & (d["gauss_psf_flags"] == 0)
        & (d["gauss_obj_flags"] == 0)
        & (d["psfrec_flags"] == 0)
        & (d["gauss_T_ratio"] > 0.5)
        & (d["gauss_s2n"] > 10)
    )
    # msk = des_y6utils.mdet.make_mdet_cuts(d, "5")
    msk &= d["mfrac"] < mfrac

    vals = []

    ugind = np.unique(gind)
    for _gind in range(ngrid*ngrid):
        gmsk = msk & (_gind == gind)
        if np.any(gmsk):
            sval = []
            for shear in ["noshear", "1p", "1m", "2p", "2m"]:
                sgmsk = gmsk & (d["mdet_step"] == shear)
                if np.any(sgmsk):
                    sval.append(np.mean(d["gauss_g_1"][sgmsk]))
                    sval.append(np.mean(d["gauss_g_2"][sgmsk]))
                    sval.append(np.sum(sgmsk))
                else:
                    sval.append(np.nan)
                    sval.append(np.nan)
                    sval.append(np.nan)
            vals.append(tuple(sval + [_gind]))
        else:
            vals.append(tuple([np.nan] * 3 * 5 + [_gind]))

    return np.array(
        vals,
        dtype=[
            ("g1", "f8"),
            ("g2", "f8"),
            ("n", "f8"),
            ("g1_1p", "f8"),
            ("g2_1p", "f8"),
            ("n_1p", "f8"),
            ("g1_1m", "f8"),
            ("g2_1m", "f8"),
            ("n_1m", "f8"),
            ("g1_2p", "f8"),
            ("g2_2p", "f8"),
            ("n_2p", "f8"),
            ("g1_2m", "f8"),
            ("g2_2m", "f8"),
            ("n_2m", "f8"),
            ("grid_ind", "i4")
        ]
    )


def grid_file_pair(*, fplus, fminus, ngrid, mfrac=0.1):
    dp = grid_file(fname=fplus, ngrid=ngrid, mfrac=mfrac)
    dm = grid_file(fname=fminus, ngrid=ngrid, mfrac=mfrac)

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
    g1_p = np.nansum(d["g1_p"] * d["n_p"]) / np.nansum(d["n_p"])
    g1p_p = np.nansum(d["g1_1p_p"] * d["n_1p_p"]) / np.nansum(d["n_1p_p"])
    g1m_p = np.nansum(d["g1_1m_p"] * d["n_1m_p"]) / np.nansum(d["n_1m_p"])
    R11_p = (g1p_p - g1m_p) / 0.02

    g1_m = np.nansum(d["g1_m"] * d["n_m"]) / np.nansum(d["n_m"])
    g1p_m = np.nansum(d["g1_1p_m"] * d["n_1p_m"]) / np.nansum(d["n_1p_m"])
    g1m_m = np.nansum(d["g1_1m_m"] * d["n_1m_m"]) / np.nansum(d["n_1m_m"])
    R11_m = (g1p_m - g1m_m) / 0.02

    g2_p = np.nansum(d["g2_p"] * d["n_p"]) / np.nansum(d["n_p"])
    g2p_p = np.nansum(d["g2_2p_p"] * d["n_2p_p"]) / np.nansum(d["n_2p_p"])
    g2m_p = np.nansum(d["g2_2m_p"] * d["n_2m_p"]) / np.nansum(d["n_2m_p"])
    R22_p = (g2p_p - g2m_p) / 0.02

    g2_m = np.nansum(d["g2_m"] * d["n_m"]) / np.nansum(d["n_m"])
    g2p_m = np.nansum(d["g2_2p_m"] * d["n_2p_m"]) / np.nansum(d["n_2p_m"])
    g2m_m = np.nansum(d["g2_2m_m"] * d["n_2m_m"]) / np.nansum(d["n_2m_m"])
    R22_m = (g2p_m - g2m_m) / 0.02

    return (g1_p - g1_m) / (R11_p + R11_m) / 0.02 - 1., (g2_p + g2_m) / (R22_p + R22_m)


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
        "--mfrac",
        type=float,
        required=False,
        default=0.1,
        help="mfrac cut [float]",
    )
    return parser.parse_args()


def main():

    args = get_args()

    pairs = {}

    imsim_path = Path(args.imsim_dir)
    config_name = imsim_path.name
    tile_dirs = imsim_path.glob("*")

    for tile_dir in tile_dirs:
        tile = tile_dir.stem
        pairs[tile] = {}
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

            pairs[tile][run] = (fname_plus, fname_minus)

    ntiles = len([p for p in pairs.values() if p])

    mfrac = args.mfrac
    jobs = [
        joblib.delayed(grid_file_pair)(fplus=pfile, fminus=mfile, ngrid=10, mfrac=mfrac)
        for seed in pairs.values()
        for pfile, mfile in seed.values()
    ]
    print(f"Processing {len(jobs)} paired simulations ({ntiles} tiles)")

    with joblib.Parallel(n_jobs=args.n_jobs, backend="loky", verbose=10) as par:
        d = par(jobs)

    d = np.concatenate(d, axis=0)

    ns = 1000  # number of bootstrap resamples
    rng = np.random.RandomState(seed=args.seed)

    m_mean, c_mean = compute_shear_pair(d)

    print(f"Bootstrapping with {ns} resamples")
    bootstrap = []
    for i in tqdm.trange(ns, ncols=80):
        rind = rng.choice(d.shape[0], size=d.shape[0], replace=True)
        bootstrap.append(compute_shear_pair(d[rind]))

    bootstrap = np.array(bootstrap)
    m_std, c_std = np.std(bootstrap, axis=0)

    # print("\v")
    # print("m:	(%0.3e, %0.3e)" % (m_mean - m_std * 3, m_mean + m_std * 3))
    # print("m mean:	%0.3e" % m_mean)
    # print("m std:	%0.3e [3 sigma]" % (m_std * 3))
    # print("\v")
    # print("c:	(%0.3e, %0.3e)" % (c_mean - c_std * 3, c_mean + c_std * 3))
    # print("c mean:	%0.3e" % c_mean)
    # print("c std:	%0.3e [3 sigma]" % (c_std * 3))
    # print("\v")
    print(f"| configuration | m mean | m std (3σ) | c mean | c std (3σ) | # tiles | mfrac |")
    print(f"|---|---|---|---|---|---|")
    print(f"| {config_name} | {m_mean:0.3e} | {m_std*3:0.3e} | {c_mean:0.3e} | {c_std*3:0.3e} | {ntiles} | {mfrac} |")

if __name__ == "__main__":
    main()
