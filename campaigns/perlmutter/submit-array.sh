#!/bin/bash

while getopts 'c:f:j:' opt; do
    case $opt in
        c) config=$OPTARG;;
        f) filename=$OPTARG;;
        j) jobs=$OPTARG;;
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

maxjobs=$(wc -l < $filename)

if [[ ! $jobs ]]; then
    printf '%s\n' "No jobs specified. Exiting.">&2
    exit 1
fi
# if [[ ! $jobs =~ ^[0-9]+:[0-9]+$ ]]; then
#     printf '%s\n' "Invalid jobs format; should be [0-9]+:[0-9]+. Exiting.">&2
#     exit 1
# fi
echo "jobs: ${jobs}"


run=$(basename $config .yaml)
submitted="${filename%.*}-${run}-submitted.txt"
touch $submitted

# Create the output directory
output="${SCRATCH}/y6-image-sims/${run}"
echo "Writing output to $output"
mkdir -p $output

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-1.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-1.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-2.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-2.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-3.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-3.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-4.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-4.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-5.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-5.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-6.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-6.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-7.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-7.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-8.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-8.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-9.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-9.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-10.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-10.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-11.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-11.sh -c ${config} -f ${filename}

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-12.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-12.sh -c ${config} -f ${filename}

