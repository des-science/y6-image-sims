#!/bin/bash

while getopts 'c:f:s:n:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(f) filename=$OPTARG;;
		(s) seed=$OPTARG;;
		(n) njobs=$OPTARG;;
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

if [[ ! $njobs ]]; then
	njobs=$(wc -l < $filename)
fi
echo "njobs:	$njobs"

# run=$(basename $(dirname $config))
run=$(basename $config .yaml)
submitted="${filename%.*}-${run}-submitted.txt"

for tile in $(ls $SCRATCH/y6-image-sims/$run | comm -23 <(sort $submitted) - | shuf | head -n $njobs)
do
	seed=$RANDOM
	echo "sbatch eastlake/run.sh -c $config -t $tile -s $seed"
	sbatch eastlake/run.sh -c $config -t $tile -s $seed
done
