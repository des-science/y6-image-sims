#!/bin/bash

while getopts 'c:t:s:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(t) tiles=$OPTARG;;
	esac
done

if [[ ! $config ]]; then
	printf '%s\n' "No config specified. Exiting.">&2
	exit 1
fi
echo "config:	$config"

# if [[ ! $tiles ]]; then
# 	printf '%s\n' "No tiles specified. Exiting.">&2
# 	exit 1
# fi
# echo "tile:	$TILE"

# for tile in $(cat $tiles);
# do
# 	echo "sbatch scripts/run.sh -c $config -t $tile -s $RANDOM"
# done

for tile in $(find /global/cfs/cdirs/des/y6-image-sims/des-pizza-slices-y6-v16/ -mindepth 1 -maxdepth 1 -type d -regex '/global/cfs/cdirs/des/y6-image-sims/des-pizza-slices-y6-v16/DES[0-9]+.[0-9]+' -printf '%f\n')
do
	SEED=$RANDOM
	echo "sbatch scripts/run.sh -c $config -t $tile -s $SEED"
	sbatch scripts/run.sh -c $config -t $tile -s $SEED
	sleep 1
done
