#!/bin/bash

while getopts 'c:f:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(f) filename=$OPTARG;;
	esac
done

if [[ ! $config ]]; then
	printf '%s\n' "No config specified. Exiting.">&2
	exit 1
fi
echo "config:	$config"

if [[ ! $filename ]]; then
	printf '%s\n' "No file specified. Exiting.">&2
	exit 1
fi
echo "file:	$filename"

# for tile in $(find /global/cfs/cdirs/des/y6-image-sims/des-pizza-slices-y6-v16/ -mindepth 1 -maxdepth 1 -type d -regex '/global/cfs/cdirs/des/y6-image-sims/des-pizza-slices-y6-v16/DES[0-9]+.[0-9]+' -printf '%f\n')
# do
# 	seed=$RANDOM
# 	echo "sbatch eastlake/run.sh -c $config -t $tile -s $seed"
# 	sbatch eastlake/run.sh -c $config -t $tile -s $seed
# 	sleep 1
# done

# # fix random seed
# RANDOM=13720

submitted="${filename%.*}-$(basename $(dirname $config))-submitted.txt"
touch $submitted
for tile in $(comm -23 <(sort $filename) <(sort $submitted))
do
	seed=$RANDOM
	echo "sbatch eastlake/run.sh -c $config -t $tile -s $seed"
	# sbatch eastlake/run.sh -c $config -t $tile -s $seed
	echo $tile >> $submitted
done
echo "finished submitting all tiles"
# rm -f -- $submitted
