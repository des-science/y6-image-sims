#!/bin/bash

while getopts 'c:f:s:' opt; do
    case $opt in
        c) config=$OPTARG;;
        f) filename=$OPTARG;;
        s) seed=$OPTARG;;
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

njobs=$(wc -l < $filename)

echo "sbatch --array=1-$njobs eastlake/array-task.sh -c $config -f $filename -s $seed"
sbatch --array=1-$njobs eastlake/array-task.sh -c $config -f $filename -s $seed

