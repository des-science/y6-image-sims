#!/bin/bash

while getopts 'c:f:s:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(f) filename=$OPTARG;;
		(s) seed=$OPTARG;;
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

if [[ ! $seed ]]; then
	printf '%s\n' "No seed specified. Exiting.">&2
	exit 1
fi
echo "seed:	$seed"
RANDOM=$seed

# for tile in $(find /global/cfs/cdirs/des/y6-image-sims/des-pizza-slices-y6-v16/ -mindepth 1 -maxdepth 1 -type d -regex '/global/cfs/cdirs/des/y6-image-sims/des-pizza-slices-y6-v16/DES[0-9]+.[0-9]+' -printf '%f\n')
# do
# 	seed=$RANDOM
# 	echo "sbatch eastlake/run.sh -c $config -t $tile -s $seed"
# 	sbatch eastlake/run.sh -c $config -t $tile -s $seed
# 	sleep 1
# done

submitted="${filename%.*}-$(basename $(dirname $config))-$seed-submitted.txt"
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
