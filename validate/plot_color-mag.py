import argparse
from pathlib import Path
import os

import joblib
import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import fitsio

import des_y6utils


def grid_file(*, fname, Tratio=0.5, s2n=10, mfrac=0.1):
    d = fitsio.read(fname)

    msk = (
        ((d["mask_flags"] & (~16)) == 0)
        & (d["gauss_flags"] == 0)
        & (d["gauss_psf_flags"] == 0)
        & (d["gauss_obj_flags"] == 0)
        & (d["psfrec_flags"] == 0)
    )
    # msk = des_y6utils.mdet.make_mdet_cuts(d, "5")
    # msk = des_y6utils.mdet.make_mdet_cuts(d, "6")
    msk &= (d["gauss_T_ratio"] > Tratio)
    msk &= d["gauss_s2n"] > s2n
    msk &= d["mfrac"] < mfrac

    msk &= d["mdet_step"] == "noshear"

    flux_g = d["pgauss_band_flux_g"][msk]
    flux_r = d["pgauss_band_flux_r"][msk]

    g_mag = -2.5 * np.log10(flux_g) + 30
    gr_color = -2.5 * np.log10(flux_g / flux_r)

    return gr_color, g_mag


def accumulate_file_pair(*, fplus, fminus, bins, Tratio=0.5, s2n=10, mfrac=0.1):
    gr_color_p, g_mag_p = grid_file(fname=fplus, Tratio=Tratio, s2n=s2n, mfrac=mfrac)
    gr_color_m, g_mag_m = grid_file(fname=fminus, Tratio=Tratio, s2n=s2n, mfrac=mfrac)

    hist_p, _, _ = np.histogram2d(gr_color_p, g_mag_p, bins=bins)
    hist_m, _, _ = np.histogram2d(gr_color_m, g_mag_m, bins=bins)

    return hist_p, hist_m


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
        default=[0.1],
        nargs="+",
        help="mfrac cut [float]",
    )
    parser.add_argument(
        "--s2n",
        type=float,
        required=False,
        default=[10],
        nargs="+",
        help="s2n cut [float]",
    )
    parser.add_argument(
        "--Tratio",
        type=float,
        required=False,
        default=[0.5],
        nargs="+",
        help="Tratio cut [float]",
    )
    return parser.parse_args()


def main():

    args = get_args()

    mfracs = args.mfrac
    s2ns = args.s2n
    Tratios = args.Tratio

    pairs = {}

    imsim_path = Path(args.imsim_dir)
    config_name = imsim_path.name
    tile_dirs = imsim_path.glob("*")

    for tile_dir in tile_dirs:
        tile = tile_dir.stem
        pairs[tile] = {}

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

    bins = (
        np.linspace(-2, 4, 100),
        np.linspace(14, 28, 100)
    )

    for Tratio in Tratios:
        for s2n in s2ns:
            for mfrac in mfracs:
                jobs = [
                    joblib.delayed(accumulate_file_pair)(fplus=pfile, fminus=mfile, bins=bins, Tratio=Tratio, s2n=s2n, mfrac=mfrac)
                    for seed in pairs.values()
                    for pfile, mfile in seed.values()
                ]
                print(f"Processing {len(jobs)} paired simulations ({ntiles} tiles)")

                with joblib.Parallel(n_jobs=args.n_jobs, backend="loky", verbose=10) as par:
                    d = par(jobs)

                hist_p, hist_m = np.sum(d, axis=0)

                fig, axs = plt.subplots(1, 2)

                # axs[0].imshow(hist_p, origin="lower")
                pcm = axs[0].pcolormesh(bins[0], bins[1], hist_p.T, norm=colors.lognorm())
                axs[0].set_xlabel("$g - r$")
                axs[0].set_ylabel("$g$")
                axs[0].set_title("plus")
                axs[0].grid()
                axs[0].invert_yaxis()
                fig.colorbar(pcm, ax=axs[0])

                # axs[1].imshow(hist_m, origin="lower")
                pcm = axs[1].pcolormesh(bins[0], bins[1], hist_m.T, norm=colors.lognorm())
                axs[1].set_xlabel("$g - r$")
                axs[1].set_ylabel("$g$")
                axs[1].set_title("minus")
                axs[1].grid()
                axs[1].invert_yaxis()
                fig.colorbar(pcm, ax=axs[1])

                plt.show()


if __name__ == "__main__":
    main()
