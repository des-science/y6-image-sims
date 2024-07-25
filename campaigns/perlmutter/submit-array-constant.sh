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

echo "sbatch --array=${jobs} campaigns/perlmutter/array-task-constant.sh -c ${config} -f ${filename}"
sbatch --array=${jobs} campaigns/perlmutter/array-task-constant.sh -c ${config} -f ${filename}

# while read tile
# do
#     echo $tile >> $submitted
# done < $filename
