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

patches_file=/astro/u/esheldon/y6patches/patches-altrem-npatch200-seed8888.fits.gz  # FIXME

pizza-patches-make-cut-files \
    --flist=${output_flist} \
    --uid-info=${output_uids} \
    --patches=${patches_file} \
    --outdir=${output_dir} \
    --keep-coarse-cuts

chmod go-rwx ${output_dir}/*.fits
chmod u-w ${output_dir}/*.fits

echo "done"
