import numpy as np
import argparse
from pathlib import Path

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
    parser.add_argument(
        "--n_tiles",
        type=int,
        required=False,
        default=1000,
        help="number of tiles for which to generate seeds",
    )
    parser.add_argument(
        "--n_seeds",
        type=int,
        required=False,
        default=10,
        help="number of seeds to generate per tile",
    )
    return parser.parse_args()


def main():
    args = get_args()

    print(vars(args))

    print(f"Making generator with seed {args.seed}")
    rng = np.random.default_rng(seed=args.seed)
    print(f"Making {args.n_seeds} seeds for {args.n_tiles} tiles")
    seed_lists = rng.integers(1, 2**30, size=(args.n_tiles, args.n_seeds)).tolist()

    print(f"Writing seeds to {args.output}")
    with open(args.output, "w") as fp:
        for i, seed_list in enumerate(seed_lists):
            for ii, seed in enumerate(seed_list):
                fp.write("%s" % seed)
                if ii < args.n_seeds - 1:
                    fp.write(" ")
            fp.write("\n")

    print("Done!")


if __name__ == "__main__":
    main()
