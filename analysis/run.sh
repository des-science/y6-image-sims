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

while getopts 'c:s:m:n:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(s) seed=$OPTARG;;
		(m) mfrac=$OPTARG;;
		(n) njobs=$OPTARG;;
	esac
done

if [[ ! $config ]]; then
	printf '%s\n' "No config specified. Exiting.">&2
	exit 1
fi
echo "config:	$config"

if [[ ! $seed ]]; then
	printf '%s\n' "No seed specified. Exiting.">&2
	exit 1
fi
echo "seed:	$seed"

if [[ ! $mfrac ]]; then
	mfrac=0.1
fi
echo "mfrac:	$mfrac"

if [[ ! $njobs ]]; then
	njobs=8
fi
echo "njobs:	$njobs"

# Source the setup script from the script directory
source setup.sh

# run=$(basename $(dirname $config))
run=$(basename $config .yaml)

python analysis/compute-bias.py \
	$SCRATCH/y6-image-sims/$run \
	--seed $seed \
	--mfrac $mfrac \
	--n_jobs $njobs
