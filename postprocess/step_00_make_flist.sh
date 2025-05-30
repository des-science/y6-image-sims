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

# perlmutter sims
input_dir="${SCRATCH}/y6-image-sims/${run}"
output_flist=${run}-${shear}_flist.txt
touch ${output_flist}

for fname in ${input_dir}/DES**/**/${shear}/des-pizza-slices-y6/DES**/metadetect/*_metadetect-config_mdetcat_part0000.fits
do
    echo ${fname}
    echo ${fname} >> ${output_flist}
done

# degrid sims
input_dir="/pscratch/sd/d/dhayaa/y6-image-sims/campaigns/${run}"
for fname in ${input_dir}/DES**/${shear}/metadetect/*_metadetect-config_mdetcat_part0000.fits
do
    echo ${fname}
    echo ${fname} >> ${output_flist}
done
