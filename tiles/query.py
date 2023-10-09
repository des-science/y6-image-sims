import argparse
from pathlib import Path

import easyaccess as ea
import numpy as np


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output",
        type=str,
        help="Output file",
    )
    parser.add_argument(
        "--seed",
        type=int,
        required=False,
        default=1,
        help="RNG seed",
    )
    return parser.parse_args()


def main():

    args = get_args()
    print(args)

    # y6 tiles
    connection=ea.connect()
    cursor=connection.cursor()
    # query = "select distinct(tilename) from DES_ADMIN.Y6A2_COADD_OBJECT_SUMMARY shuffle fetch first 1000 rows only"
    query = "select distinct(tilename) from DES_ADMIN.Y6A2_COADD_OBJECT_SUMMARY"
    df = connection.query_to_pandas(query)
    y6_tiles = df.to_numpy().ravel().tolist()

    # y3 tiles
    p = Path("/dvs_ro/cfs/cdirs/des/y3-image-sims/y3v02/")
    y3_tiles = [t.stem for t in p.glob("DES*")]

    y3_set = set(y3_tiles)
    y6_set = set(y6_tiles)
    y6_and_y3_set = y3_set & y6_set  # get tiles in y6 that are also in y3
    y6_not_y3_set = y6_set - y3_set  # get tiles in y6 that are not in y3

    y6_and_y3_list = list(y6_and_y3_set)
    y6_not_y3_list = list(y6_not_y3_set)

    # sort in-place for reproducability
    y6_and_y3_list.sort()
    y6_not_y3_list.sort()

    rng = np.random.default_rng(args.seed)

    y3_100 = rng.choice(y6_and_y3_list, 100, replace=False)
    y6_900 = rng.choice(y6_not_y3_list, 900, replace=False)

    tiles = list(set(y3_100) | set(y6_900))
    tiles.sort()
    if len(tiles) != 1000:
        raise ValueError("Incorrect number of tiles! Found %d from y3 and %d from y6 (should be 100 and 900)" % len(y3_100), len(y6_900))

    with open(args.output, 'w') as fp:
        for tile in tiles:
            fp.write('%s\n' % tile)


if __name__ == "__main__":
    main()
