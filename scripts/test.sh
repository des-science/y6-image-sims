#!/bin/bash

DEFAULT_TILE="DES2205+0126"

while getopts 'c:t:s:' opt; do
    case $opt in
      (c)   CONFIG=$OPTARG;;
      (t)   TILE=$OPTARG;;
      (s)   SEED=$OPTARG;;
      # (:)   # "optional arguments" (missing option-argument handling)
      #       case $OPTARG in
      #         (c) exit 1;; # error, according to our syntax
      #         (t) exit 1;;
      #         (s) exit 1;;
      #       esac;;
    esac
done

if [[ ! $CONFIG ]]; then
    printf '%s\n' "No config specified. Exiting.">&2
    exit 1
fi
echo "config:	$CONFIG"

if [[ ! $TILE ]]; then
    printf '%s\n' "No tile specified. Exiting.">&2
    exit 1
fi
echo "tile:	$TILE"

if [[ ! $SEED ]]; then
    printf '%s\n' "No seed specified. Exiting.">&2
    exit 1
fi
echo "seed:	$SEED"

# shift "$OPTIND"
# remaining is "$@"

# Source the setup script from the script directory
source ./scripts/setup.sh
# source $(realpath $(dirname "$0")/setup.sh)

# Define run directory
RUN=$(basename $(dirname $CONFIG))

# Create the output directory
OUTPUT=$SCRATCH/y6-image-sims/$RUN/$TILE/$SEED
# If we have already run this seed, find a new one
while [ -d "$OUTPUT" ]
do
    echo "$OUTPUT already exists; trying a new seed"
    SEED=$RANDOM
    OUTPUT=$SCRATCH/y6-image-sims/$RUN/$TILE/$SEED
done
echo "Writing output to $OUTPUT"
mkdir -p $OUTPUT

echo "Running eastlake sim with positive shear"
run-eastlake-sim \
    -v 1 \
    --seed $SEED \
    $CONFIG \
    $OUTPUT/plus \
    stamp.shear.g1=0.02 stamp.shear.g2=0.00 output.tilename=$TILE \
    pizza_cutter.n_jobs=8 metadetect.n_jobs=8 output.nproc=1 \
    output.n_se_test=1 output.bands="r"
