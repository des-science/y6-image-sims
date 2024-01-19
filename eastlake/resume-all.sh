#!/bin/bash

while getopts 'c:' opt; do
	case $opt in
		(c) config=$OPTARG;;
	esac
done

if [[ ! $config ]]; then
	printf '%s\n' "No config specified. Exiting.">&2
	exit 1
fi
echo "config:	$config"

run=$(basename $config .yaml)
for tile_path in $SCRATCH/y6-image-sims/$run/*
do
    tile=$(basename $tile_path)
	for seed_path in $SCRATCH/y6-image-sims/$run/$tile/*
	do
		seed=$(basename $seed_path)
		pmdetcat=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/plus/des-pizza-slices-y6/${tile}/metadetect/${tile}_metadetect-config_mdetcat_part0000.fits
		mmdetcat=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/minus/des-pizza-slices-y6/${tile}/metadetect/${tile}_metadetect-config_mdetcat_part0000.fits
		# if [[ (! -f $pmdetcat) || (! -f $mmdetcat) ]]; then
		# 	pjobrecord=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/plus/job_record.pkl
		# 	mjobrecord=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/minus/job_record.pkl
		# 	if [[ (-f $pjobrecord) && (-f $mjobrecord) ]]; then
		# 	    echo "sbatch eastlake/resume.sh -c $config -t $tile -s $seed"
		# 	    sbatch eastlake/resume.sh -c $config -t $tile -s $seed
		# 	else
		# 	    echo "sbatch eastlake/run.sh -c $config -t $tile -s $seed"
		# 	    sbatch eastlake/run.sh -c $config -t $tile -s $seed
		# 	fi
		# fi
		if [[ ! -f $pmdetcat ]]; then
			pjobrecord=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/plus/job_record.pkl
			if [[ -f $pjobrecord ]]; then
			    echo "sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g plus"
			    sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g plus
			else
			    echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus"
			    sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g plus
			fi
		fi
		if [[ ! -f $mmdetcat ]]; then
			mjobrecord=${SCRATCH}/y6-image-sims/${run}/${tile}/${seed}/minus/job_record.pkl
			if [[ -f $mjobrecord ]]; then
			    echo "sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g minus"
			    sbatch eastlake/resume-single-shear.sh -c $config -t $tile -s $seed -g minus
			else
			    echo "sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus"
			    sbatch eastlake/run-single-shear.sh -c $config -t $tile -s $seed -g minus
			fi
		fi
	done
done
