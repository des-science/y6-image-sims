#!/bin/bash
#SBATCH -J eastlake
#SBATCH -A des
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=256
#SBATCH --mem=0

while getopts 'c:n:' opt; do
	case $opt in
		c) config=$OPTARG;;
		n) njobs=$OPTARG;;
	esac
done

if [[ ! $config ]]; then
	printf '%s\n' "No config specified. Exiting.">&2
	exit 1
fi
echo "config:	$config"

if [[ ! $njobs ]]; then
	njobs=8
fi
echo "njobs:	$njobs"

# Source the setup script from the script directory
source setup.sh

# run=$(basename $(dirname $config))
run=$(basename $config .yaml)
pcat="${SCRATCH}/y6-image-sims-cats/${run}/g1_slice=0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0/metadetect_cutsv6_all.h5"
mcat="${SCRATCH}/y6-image-sims-cats/${run}/g1_slice=-0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0/metadetect_cutsv6_all.h5"

python measure/compute-bias.py \
	$pcat $mcat \
	--n_jobs $njobs

echo "column -t -s \| -o \|"
