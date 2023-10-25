#!/bin/bash

while getopts 'c:t:s:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(t) tile=$OPTARG;;
		(s) seed=$OPTARG;;
	esac
done

if [[ ! $config ]]; then
	printf '%s\n' "No config specified. Exiting.">&2
	exit 1
fi
echo "config:	$config"

if [[ ! $tile ]]; then
	printf '%s\n' "No tile specified. Exiting.">&2
	exit 1
fi
echo "tile:	$tile"

if [[ ! $seed ]]; then
	printf '%s\n' "No seed specified. Exiting.">&2
	exit 1
fi
echo "seed:	$seed"

# Source the setup script from the script directory
source eastlake/setup.sh
# source $(realpath $(dirname "$0")/setup.sh)

# Define run directory
run=$(basename $(dirname $config))

# Create the output directory
output=$SCRATCH/y6-image-sims/$run/$tile/$seed
echo "Writing output to $output"
mkdir -p $output

echo "Running eastlake sim with positive shear"
run-eastlake-sim \
	-v 3 \
	--seed $seed \
	$config \
	$output/plus \
	stamp.shear.g1=0.02 stamp.shear.g2=0.00 output.tilename=$tile \
	pizza_cutter.n_jobs=8 metadetect.n_jobs=8 output.nproc=1 \
	output.n_se_test=1 output.bands="r"
