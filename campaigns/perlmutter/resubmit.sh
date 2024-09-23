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
        for run in 1 2 3 4 5 6 7 8 9 10 11 12; do
            shear_dir="${seed_dir}/run_${run}"
            if [ -d ${shear_dir} ]; then
                if python eastlake/check-task.py ${shear_dir}; then
                    echo ""
                else
                    index=$(sed -n "/${tilename}/=" ${filename})
                    echo "resubmitting $tilename [$index]"
                    # bash campaigns/perlmutter/submit-array-constant.sh -c ${config} -f ${filename} -j ${index}
                    echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-${run}.sh -c ${config} -f ${filename}"
                    # sbatch --array=${jobs} "campaigns/perlmutter/array-task-${run}.sh" -c ${config} -f ${filename}
                    echo ""
                fi
            fi
        done
    done
done

