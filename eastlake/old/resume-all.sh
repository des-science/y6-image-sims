#!/bin/bash

while getopts 'c:r' opt; do
    case $opt in
        c) config=$OPTARG;;
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

if [[ ! $reverse ]]; then
    reverse=false
fi
echo "reverse: $reverse"

if $reverse; then
    shear_plus="plus_reverse"
    shear_minus="minus_reverse"
else
    shear_plus="plus"
    shear_minus="minus"
fi

run=$(basename $config .yaml)
for tile_path in $SCRATCH/y6-image-sims/$run/*
do
    tile=$(basename $tile_path)
    for seed_path in $SCRATCH/y6-image-sims/$run/$tile/*
    do
        seed=$(basename $seed_path)
        pmdetcat=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/${shear_plus}/des-pizza-slices-y6/${tile}/metadetect/${tile}_metadetect-config_mdetcat_part0000.fits
        mmdetcat=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/${shear_minus}/des-pizza-slices-y6/${tile}/metadetect/${tile}_metadetect-config_mdetcat_part0000.fits
        # if [[ (! -f $pmdetcat) || (! -f $mmdetcat) ]]; then
        #     pjobrecord=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/${shear_plus}/job_record.pkl
        #     mjobrecord=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/${shear_minus}/job_record.pkl
        #     if [[ (-f $pjobrecord) && (-f $mjobrecord) ]]; then
        #         echo "sbatch eastlake/resume.sh -c $config -t $tile -s $seed"
        #         sbatch eastlake/resume.sh -c $config -t $tile -s $seed
        #     else
        #         echo "sbatch eastlake/run.sh -c $config -t $tile -s $seed"
        #         sbatch eastlake/run.sh -c $config -t $tile -s $seed
        #     fi
        # fi
        if [[ ! -f $pmdetcat ]]; then
            pjobrecord=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/${shear_plus}/job_record.pkl
            if [[ -f $pjobrecord ]]; then
                if $reverse; then
                    echo "sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g plus -r"
                    sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g plus -r
                else
                    echo "sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g plus"
                    sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g plus
                fi
            else
                if $reverse; then
                    echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus -r"
                    sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus -r
                else
                    echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus"
                    sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus
                fi
            fi
        fi
        if [[ ! -f $mmdetcat ]]; then
            mjobrecord=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/${shear_minus}/job_record.pkl
            if [[ -f $mjobrecord ]]; then
                if $reverse; then
                    echo "sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g minus -r"
                    sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g minus -r
                else
                    echo "sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g minus"
                    sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g minus
                fi
            else
                if $reverse; then
                    echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus -r"
                    sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus -r
                else
                    echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus"
                    sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus
                fi
            fi
        fi
    done
done
