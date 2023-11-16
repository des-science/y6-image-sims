#!/bin/bash
#SBATCH -J eastlake
#SBATCH -A des
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=256
#SBATCH --mem=0
#SBATCH --output=logs/slurm-%J.out
#SBATCH --error=logs/slurm-%J.log

while getopts 'c:t:s:g:' opt; do
	case $opt in
		(c) config=$OPTARG;;
		(t) tile=$OPTARG;;
		(s) seed=$OPTARG;;
		(g) shear=$OPTARG;;
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

if [[ ! $shear ]]; then
	printf '%s\n' "No shear specified. Exiting.">&2
	exit 1
fi
case $shear in
	(plus)
		g1=0.02
		g2=0.00
		;;
	(minus)
		g1=-0.02
		g2=0.00
		;;
	(*)
		printf '%s\n' "Invalid shear. Exiting.">&2
		exit 1
		;;
esac
echo "shear:	$shear ($g1, $g2)"

# Source the setup script from the script directory
source setup.sh

# Define run directory
# run=$(basename $(dirname $config))
run=$(basename $config .yaml)

# Create the output directory
output=$SCRATCH/y6-image-sims/$run/$tile/$seed
echo "Writing output to $output"
mkdir -p $output

run-eastlake-sim \
	-v 1 \
	--seed $seed \
	--resume \
	$config \
	$output/$shear \
	stamp.shear.g1=$g1 stamp.shear.g2=$g2 output.tilename=$tile

