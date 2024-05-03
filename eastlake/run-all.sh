#!/bin/bash

while getopts 'c:f:s:n:r' opt; do
    case $opt in
        c) config=$OPTARG;;
        f) filename=$OPTARG;;
        s) seed=$OPTARG;;
        n) njobs=$OPTARG;;
        r) reverse=true;;
        \?)
            printf '%s\n' "Invalid option. Exiting">&2
            exit;;
    esac
done

if [[ ! $config ]]; then
    printf '%s\n' "No config specified. Exiting.">&2
    exit 1
fi
echo "config: $config"

if [[ ! $filename ]]; then
    printf '%s\n' "No file specified. Exiting.">&2
    exit 1
fi
echo "file: $filename"

if [[ ! $seed ]]; then
    printf '%s\n' "No seed specified. Exiting.">&2
    exit 1
fi
echo "seed: $seed"
RANDOM=$seed

if [[ ! $njobs ]]; then
    njobs=$(wc -l < $filename)
fi
echo "njobs: $njobs"

if [[ ! $reverse ]]; then
    reverse=false
fi
echo "reverse: $reverse"

run=$(basename $config .yaml)
submitted="${filename%.*}-${run}-submitted.txt"
touch $submitted

for tile in $(comm -23 <(sort $filename) <(sort $submitted) | shuf | head -n $njobs)
do
    seed=$RANDOM
    if $reverse; then
        # echo "sbatch eastlake/run.sh -c $config -t $tile -s $seed"
        # sbatch eastlake/run.sh -c $config -t $tile -s $seed
        echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus -r"
        sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus
        echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus -r"
        sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus
        echo $tile >> $submitted
    else
        # echo "sbatch eastlake/run.sh -c $config -t $tile -s $seed"
        # sbatch eastlake/run.sh -c $config -t $tile -s $seed
        echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus"
        sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus
        echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus"
        sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus
        echo $tile >> $submitted
    fi
done
echo "finished submitting jobs"
