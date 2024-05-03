import os
import functools
import operator
from pathlib import Path

import numpy as np

import galsim
import hpgeom as hpg
import healsparse
import yaml


def load_wcs(tile, band, pizza_slices_dir="", des_pizza_slices_dir=""):
    print(f"loading coadd wcs for {tile}/{band}")

    pizza_cutter_info = f"{pizza_slices_dir}/pizza_cutter_info/{tile}_{band}_pizza_cutter_info.yaml"
    with open(pizza_cutter_info, "r") as fp:
        pizza_dict = yaml.safe_load(fp)

    pizza_image_path = pizza_dict.get("image_path")

    # break up the path to the image path from pizza_slices_dir
    pizza_image_path_parts = pizza_image_path.split("/")
    # take the parts below des-pizza-slices-y6
    pizza_slices_path = "/".join(pizza_image_path_parts[pizza_image_path_parts.index("des-pizza-slices-y6"):])
    # merge with des_pizza_slices_dir, add .fz extension
    image_path = (Path(des_pizza_slices_dir) / pizza_slices_path).with_suffix(".fits.fz").as_posix()

    coadd_header = galsim.fits.FitsHeader(image_path)
    coadd_wcs, origin = galsim.wcs.readFromFitsHeader(coadd_header)

    return coadd_wcs


def get_tile_area(tile, band, shear=None, pizza_slices_dir="", des_pizza_slices_dir="", mdet_mask=None):
    print(f"computing effective tile area for {tile}/{band}")
    wcs = load_wcs(
        tile,
        band,
        pizza_slices_dir=pizza_slices_dir,
        des_pizza_slices_dir=des_pizza_slices_dir,
    )
    match shear:
        case "plus":
            applied_shear = galsim.Shear(g1=0.02, g2=0.00)
        case "minus":
            applied_shear = galsim.Shear(g1=-0.02, g2=0.00)
        case _:
            applied_shear = galsim.Shear(g1=0.00, g2=0.00)

    ra_vertices = [
        wcs.toWorld(galsim.PositionD(250, 0).shear(applied_shear)).ra.deg,
        wcs.toWorld(galsim.PositionD(9750, 0).shear(applied_shear)).ra.deg,
        wcs.toWorld(galsim.PositionD(9750, 0).shear(applied_shear)).ra.deg,
        wcs.toWorld(galsim.PositionD(250, 0).shear(applied_shear)).ra.deg,
    ]
    dec_vertices = [
        wcs.toWorld(galsim.PositionD(0, 250).shear(applied_shear)).dec.deg,
        wcs.toWorld(galsim.PositionD(0, 250).shear(applied_shear)).dec.deg,
        wcs.toWorld(galsim.PositionD(0, 9750).shear(applied_shear)).dec.deg,
        wcs.toWorld(galsim.PositionD(0, 9750).shear(applied_shear)).dec.deg,
    ]

    hsp_polygon = healsparse.Polygon(
        ra=ra_vertices,
        dec=dec_vertices,
        value=1,
    )
    nside_sparse = mdet_mask.nside_sparse
    valid_area = np.sum(
         mdet_mask[hsp_polygon.get_pixels(nside=nside_sparse)],
    ) * hpg.nside_to_pixel_area(nside_sparse, degrees=True)
    print(f"effective tile area for {tile}/{band}: {valid_area:.3f} deg^2")

    return valid_area


def load_mdet_mask(fname="/dvs_ro/cfs/cdirs/des/y6-shear-catalogs/y6-combined-hleda-gaiafull-des-stars-hsmap131k-mdet-v2.hsp"):
    print(f"loading mdet mask from {fname}")
    hmap = healsparse.HealSparseMap.read(
        fname,
    )
    return hmap


def gather_sims(imsim_path):
    imsim_path = Path(imsim_path)
    config_name = imsim_path.name
    tile_dirs = imsim_path.glob("*")

    shears = ["plus", "minus"]

    pairs = {}
    for tile_dir in tile_dirs:
        tile = tile_dir.stem
        pairs[tile] = {}

        seed_dirs = tile_dir.glob("*")

        for seed_dir in seed_dirs:
            seed = seed_dir.stem

            pairs[tile][seed] = {}
            for shear in shears:
                # pairs[tile][run][shear] = {}
                catalog_fname = seed_dir / shear / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000.fits"
                mask_fname = seed_dir / shear / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000-healsparse-mask.hs"
                pizza_slices_dir = seed_dir / shear / "des-pizza-slices-y6"

                pairs[tile][seed][shear] = {
                    "catalog": catalog_fname.as_posix(),
                    "mask": mask_fname.as_posix(),
                    "pizza_slices_dir": pizza_slices_dir.as_posix(),
                }

                print(tile, seed, shear)

            exists = [
                (
                    os.path.exists(pairs[tile][seed][shear]["catalog"])
                    and os.path.exists(pairs[tile][seed][shear]["mask"])
                    and os.path.exists(pairs[tile][seed][shear]["pizza_slices_dir"])
                ) for shear in shears
            ]
            if not functools.reduce(operator.and_, exists):
                print("removing ", tile, seed)
                pairs[tile].pop(seed)
                continue


    return pairs


def get_levels(hist, percentiles=[0.5]):
    levels = np.quantile(
        hist[hist > 0],
        percentiles,
    )
    # levels = np.array([
    #     np.max(hist[hist < percentile * np.mean(hist[hist > 0])])
    #     for percentile in percentiles
    # ])

    print("percentiles:", percentiles)
    print("levels:", levels)

    return levels

def get_percentile(hist, level):

    percentile = (1 - np.mean(hist[hist > 0] < level)) * 100
    # percentile = np.sum(hist[hist > level]) / np.sum(hist) * 100

    return percentile


