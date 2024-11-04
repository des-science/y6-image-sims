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

output_flist=${run}-${shear}_flist.txt
if [[ ! -f ${output_flist} ]]; then
    echo "flist not found!"
    echo "expected ${output_flist}"
    exit
fi

output_uids=${run}-${shear}_uids.yaml
if [[ ! -f ${output_uids} ]]; then
    echo "uids not found!"
    echo "expected ${output_uids}"
    exit
fi

output_dir=${SCRATCH}/y6-image-sims-cuts/${run}/${shear}
mkdir -p ${output_dir}

patches_file=/global/cfs/cdirs/des/y6-shear-catalogs/patches-altrem-npatch200-seed9999_v1.fits.gz

pizza-patches-make-cut-files \
    --flist=${output_flist} \
    --uid-info=${output_uids} \
    --patches=${patches_file} \
    --outdir=${output_dir} \
    --keep-coarse-cuts \
    --run-on-sim

# chmod go-w ${output_dir}/*.fits
chmod u+w ${output_dir}/*.fits
