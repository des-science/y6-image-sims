#!/bin/bash

while getopts 'c:s:n:' opt; do
    case $opt in
        c) config=$OPTARG;;
        s) shear=$OPTARG;;
        n) njobs=$OPTARG;;
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

if [[ ! $shear ]]; then
    printf '%s\n' "No shear specified. Exiting.">&2
    exit 1
fi
echo "shear: ${shear}"

if [[ ! $njobs ]]; then
    njobs=1
fi
echo "njobs: $njobs"

run=$(basename ${config} .yaml)

output_flist=${run}-${shear}_flist.txt

if [[ ! -f ${output_flist} ]]; then
    echo "flist not found!"
    echo "expected ${output_flist}"
    exit
fi

output_uids=${run}-${shear}_uids.yaml
touch ${output_uids}

pizza-patches-make-uids \
    --flist=${output_flist} \
    --output=${output_uids} \
    --n-jobs=${n_jobs}

echo "done"
