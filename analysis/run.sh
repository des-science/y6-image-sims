#!/bin/bash
#SBATCH -J eastlake
#SBATCH -A des
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=256
#SBATCH --mem=0

while getopts 'c:t:s:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(s) seed=$OPTARG;;
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

# Source the setup script from the script directory
source eastlake/setup.sh
# source $(realpath $(dirname "$0")/setup.sh)

# Define run directory
run=$(basename $(dirname $config))

python analysis/compute-bias.py \
	$SCRATCH/y6-image-sims/$run
	--seed $seed \
	--n_jobs 128
