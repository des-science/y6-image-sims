#!/bin/bash
#SBATCH -J eastlake
#SBATCH -A des
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 06:00:00
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=256
#SBATCH --mem=0
#SBATCH --output=logs/slurm-%J.out
#SBATCH --error=logs/slurm-%J.log

while getopts 'c:t:s:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(t) tile=$OPTARG;;
		(s) seed=$OPTARG;;
	esac
done

if [[ ! $config ]]; then
	printf '%s\n' "No config specified. Exiting.">&2
	exit 1
fi
echo "config:	$config"

if [[ ! $tile ]]; then
	printf '%s\n' "No tile specified. Exiting.">&2
	exit 1
fi
echo "tile:	$tile"

if [[ ! $seed ]]; then
	printf '%s\n' "No seed specified. Exiting.">&2
	exit 1
fi
echo "seed:	$seed"

# Source the setup script from the script directory
source setup.sh

# Define run directory
# run=$(basename $(dirname $config))
run=$(basename $config .yaml)

# Create the output directory
output=$SCRATCH/y6-image-sims/$run/$tile/$seed
echo "Writing output to $output"
mkdir -p $output

srun_call="srun --exclusive --cpu-bind=cores --nodes=1 --ntasks=1 --output=logs/slurm-%J.out --error=logs/slurm-%J.log"

$srun_call run-eastlake-sim \
	-v 1 \
	--seed $seed \
	--resume \
	$config \
	$output/plus \
	stamp.shear.g1=0.02 stamp.shear.g2=0.00 output.tilename=$tile \
	&  # run the process in the background so we can execute both job steps in parallel

$srun_call run-eastlake-sim \
	-v 1 \
	--seed $seed \
	--resume \
	$config \
	$output/minus \
	stamp.shear.g1=-0.02 stamp.shear.g2=0.00 output.tilename=$tile \
	&  # run the process in the background so we can execute both job steps in parallel

# wait for each srun job to finish in the background
wait
