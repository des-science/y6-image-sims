#!/bin/bash

while getopts 'c:s:' opt; do
    case $opt in
        c) config=$OPTARG;;
        s) shear=$OPTARG;;
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

run=$(basename ${config} .yaml)

input_dir=${SCRATCH}/y6-image-sims-cuts/${run}/${shear}
output_dir=${SCRATCH}/y6-image-sims-cats/${run}/${shear}
mkdir -p ${output_dir}

pizza-patches-make-hdf5-cats \
    --output-file-base=${output_dir}/"metadetect_cutsv6" \
    --input-file-dir=${input_dir}

# chmod go-w ${output_dir}/metadetect_cutsv6_all.h5
# chmod go-w ${output_dir}/metadetect_cutsv6_patch*.h5
chmod u+w ${output_dir}/metadetect_cutsv6_all.h5
chmod u+w ${output_dir}/metadetect_cutsv6_patch*.h5
