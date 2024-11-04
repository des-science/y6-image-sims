import logging
import os
import functools
import operator
from pathlib import Path

import numpy as np

import galsim
import h5py
import hpgeom as hpg
import healsparse
import yaml
import pyarrow.compute as pc
import pyarrow.dataset as ds
from pyarrow import acero


logger = logging.getLogger(__name__)


# thanks @eli
def extractor(m, poly):
    pixels = poly.get_pixels(nside=m.nside_sparse)

    extracted = healsparse.HealSparseMap.make_empty(
        nside_coverage=m.nside_coverage,
        nside_sparse=m.nside_sparse,
        dtype=np.bool_,
        sentinel=False,
        bit_packed=True,
    )
    extracted[pixels] = m[pixels]

    return extracted


def load_wcs(tilename, band="r"):
    image_paths = list(
        Path(os.environ["IMSIM_DATA"]).glob(
            f"des-pizza-slices-y6/{tilename}/sources-{band}/OPS_Taiga/multiepoch/*/*/{tilename}/*/coadd/{tilename}_*_{band}.fits.fz"
        )
    )
    image_path = image_paths.pop().as_posix()
    if len(image_paths) > 0:
        logger.warning(f"Warning: found multiple images for {tilename}: {image_paths}")
    logger.info(f"Found following image for {tilename}: {image_path}")

    coadd_header = galsim.fits.FitsHeader(image_path)
    coadd_wcs, origin = galsim.wcs.readFromFitsHeader(coadd_header)

    return coadd_wcs


def get_tile_mask(tile, band, shear=None, mdet_mask=None, border=True):
    logger.info(f"computing effective tile mask for {tile}/{band}")
    wcs = load_wcs(
        tile,
        band=band,
    )
    match shear:
        case "plus":
            applied_shear = galsim.Shear(g1=0.02, g2=0.00)
        case "minus":
            applied_shear = galsim.Shear(g1=-0.02, g2=0.00)
        case _:
            applied_shear = galsim.Shear(g1=0.00, g2=0.00)

    if border:
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
    else:
        ra_vertices = [
            wcs.toWorld(galsim.PositionD(0, 0).shear(applied_shear)).ra.deg,
            wcs.toWorld(galsim.PositionD(10000, 0).shear(applied_shear)).ra.deg,
            wcs.toWorld(galsim.PositionD(10000, 0).shear(applied_shear)).ra.deg,
            wcs.toWorld(galsim.PositionD(0, 0).shear(applied_shear)).ra.deg,
        ]
        dec_vertices = [
            wcs.toWorld(galsim.PositionD(0, 0).shear(applied_shear)).dec.deg,
            wcs.toWorld(galsim.PositionD(0, 0).shear(applied_shear)).dec.deg,
            wcs.toWorld(galsim.PositionD(0, 10000).shear(applied_shear)).dec.deg,
            wcs.toWorld(galsim.PositionD(0, 10000).shear(applied_shear)).dec.deg,
        ]

    polygon = healsparse.Polygon(
        ra=ra_vertices,
        dec=dec_vertices,
        value=True,
    )

    if mdet_mask is not None:
        valid_map = extractor(mdet_mask, polygon)
    else:
        valid_map = polygon.get_map(
            nside_coverage=32,
            nside_sparse=131072,
            dtype=np.bool_,
        )

    return valid_map


def get_tile_area(tile, band, shear=None, mdet_mask=None, border=True):
    logger.info(f"computing effective tile area for {tile}/{band}")
    valid_map = get_tile_mask(tile, band, shear=shear, mdet_mask=mdet_mask, border=border)
    valid_area = valid_map.get_valid_area(degrees=True)
    logger.info(f"effective tile area for {tile}/{band}: {valid_area:.3f} deg^2")

    return valid_area


def load_mdet_mask(fname="/dvs_ro/cfs/cdirs/des/y6-shear-catalogs/y6-combined-hleda-gaiafull-des-stars-hsmap131k-mdet-v2.hsp"):
    logger.info(f"loading mdet mask from {fname}")
    hmap = healsparse.HealSparseMap.read(
        fname,
    )
    return hmap


def gather_inputs():
    inputs = []
    input_base = Path(os.environ["IMSIM_DATA"]) / "cosmos_simcat"
    for input_path in input_base.glob("cosmos_simcat_v7_DES[0-9]*[+-][0-9]*_seed[0-9]*.fits"):
        input_file = input_path.as_posix()
        logger.info(input_file)
        inputs.append(input_file)

    return inputs


# def gather_sims(imsim_path):
#     imsim_path = Path(imsim_path)
#     config_name = imsim_path.name
#     tile_dirs = imsim_path.glob("*")
# 
#     shears = ["plus", "minus"]
# 
#     pairs = {}
#     for tile_dir in tile_dirs:
#         tile = tile_dir.stem
#         pairs[tile] = {}
# 
#         seed_dirs = tile_dir.glob("*")
# 
#         for seed_dir in seed_dirs:
#             seed = seed_dir.stem
# 
#             pairs[tile][seed] = {}
#             for shear in shears:
#                 # pairs[tile][run][shear] = {}
#                 catalog_fname = seed_dir / shear / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000.fits"
#                 mask_fname = seed_dir / shear / "des-pizza-slices-y6" / tile / "metadetect" / f"{tile}_metadetect-config_mdetcat_part0000-healsparse-mask.hs"
#                 pizza_slices_dir = seed_dir / shear / "des-pizza-slices-y6"
# 
#                 pairs[tile][seed][shear] = {
#                     "catalog": catalog_fname.as_posix(),
#                     "mask": mask_fname.as_posix(),
#                     "pizza_slices_dir": pizza_slices_dir.as_posix(),
#                 }
# 
#                 print(tile, seed, shear)
# 
#             exists = [
#                 (
#                     os.path.exists(pairs[tile][seed][shear]["catalog"])
#                     and os.path.exists(pairs[tile][seed][shear]["mask"])
#                     and os.path.exists(pairs[tile][seed][shear]["pizza_slices_dir"])
#                 ) for shear in shears
#             ]
#             if not functools.reduce(operator.and_, exists):
#                 print("removing ", tile, seed)
#                 pairs[tile].pop(seed)
#                 continue
# 
# 
#     return pairs

# def gather_catalogs(imsim_path):
#     catalogs = {}
#     for catalog_file in (imsim_path / "g1_slice=0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0").glob("*"):
# 
#         catalogs["plus"] = str(catalog_file)
# 
#     for catalog_file in (imsim_path / "g1_slice=-0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0").glob("*"):
#         catalogs["minus"] = str(catalog_file)
# 
#     return catalogs
def gather_catalogs(imsim_path):
    catalogs = {}
    for catalog_file in (imsim_path / "g1_slice=0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0").glob("*"):
        tilename = catalog_file.name.split("_")[0]

        catalogs[tilename] = {}
        catalogs[tilename]["plus"] = str(catalog_file)

    for catalog_file in (imsim_path / "g1_slice=-0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0").glob("*"):
        tilename = catalog_file.name.split("_")[0]
        catalogs[tilename]["minus"] = str(catalog_file)

    return catalogs


def get_levels(hist, percentiles=[0.5]):
    levels = np.quantile(
        hist[hist > 0],
        percentiles,
    )
    # levels = np.array([
    #     np.max(hist[hist < percentile * np.mean(hist[hist > 0])])
    #     for percentile in percentiles
    # ])

    logger.info("percentiles:", percentiles)
    logger.info("levels:", levels)

    return levels

def get_percentile(hist, level):

    percentile = (1 - np.mean(hist[hist > 0] < level)) * 100
    # percentile = np.sum(hist[hist > level]) / np.sum(hist) * 100

    return percentile



def get_tilenames(dset_plus, dset_minus):
    scan_node_p = acero.Declaration(
        "scan",
        acero.ScanNodeOptions(
            dset_plus,
            columns=["tilename"],
        ),
    )
    aggregate_node_p = acero.Declaration(
        "aggregate",
        acero.AggregateNodeOptions(
            [
                ("tilename", "hash_count", None, "count"),
            ],
            keys=["tilename"],
        ),
        inputs=[scan_node_p],
    )

    scan_node_m = acero.Declaration(
        "scan",
        acero.ScanNodeOptions(
            dset_minus,
            columns=["tilename"],
        ),
    )
    aggregate_node_m = acero.Declaration(
        "aggregate",
        acero.AggregateNodeOptions(
            [
                ("tilename", "hash_count", None, "count"),
            ],
            keys=["tilename"],
        ),
        inputs=[scan_node_m],
    )

    join_node = acero.Declaration(
        "hashjoin",
        acero.HashJoinNodeOptions(
            "inner",
            ["tilename"],
            ["tilename"],
            left_output=["tilename", "count"],
            right_output=["count"],
            output_suffix_for_left="_p",
            output_suffix_for_right="_m",
        ),
        inputs=[aggregate_node_p, aggregate_node_m],
    )

    plan = join_node

    print(plan)
    res = plan.to_table(use_threads=True)
    tilenames = res["tilename"].to_pylist()

    return tilenames


def get_column(data, column, predicate=None):
    match data:
        case h5py.Group():
            if predicate is None:
                predicate = slice(None)
            return data[column][predicate]
        case ds.Dataset():
            _table = data.to_table(
                filter=predicate,
                columns=[column],
            )
            return _table[column].to_numpy()
        case _:
            return None
