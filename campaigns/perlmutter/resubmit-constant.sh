#!/bin/bash

while getopts 'c:f:' opt; do
    case $opt in
        c) config=$OPTARG;;
        f) filename=$OPTARG;;
        \?)
            printf '%s\n' "Invalid option. Exiting">&2
            exit;;
    esac
done

if [[ ! $config ]]; then
    printf '%s\n' "No config specified. Exiting.">&2
    exit 1
fi
echo "config: ${config}"

if [[ ! $filename ]]; then
    printf '%s\n' "No file specified. Exiting.">&2
    exit 1
fi
echo "file: ${filename}"

# Source the setup script from the script directory
source setup.sh

# Define run directory
run=$(basename $config .yaml)

input_dir=${SCRATCH}/y6-image-sims/${run}

for tile_dir in ${input_dir}/*
do
    tilename=$(basename $tile_dir)
    for seed_dir in ${tile_dir}/*
    do
        for shear_dir in ${seed_dir}/*
        do
            if python eastlake/check-task.py ${shear_dir}; then
                echo ""
            else
                index=$(sed -n "/${tilename}/=" ${filename})
                echo "resubmitting $tilename [$index]"
                bash campaigns/perlmutter/submit-array-constant.sh -c ${config} -f ${filename} -j ${index}
                echo ""
                break
            fi
        done
    done
done

