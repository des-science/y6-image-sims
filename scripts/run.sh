#!/bin/bash
#SBATCH -A des
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 03:00:00
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=256
#SBATCH --mem=0
#SBATCH --output=logs/slurm-%J.out
#SBATCH --error=logs/slurm-%J.log

DEFAULT_TILE="DES2205+0126"

while getopts 'c:t:s:' opt; do
    case $opt in
      (c)   CONFIG=$OPTARG;;
      (t)   TILE=$OPTARG;;
      (s)   SEED=$OPTARG;;
      # (:)   # "optional arguments" (missing option-argument handling)
      #       case $OPTARG in
      #         (c) exit 1;; # error, according to our syntax
      #         (t) exit 1;;
      #         (s) exit 1;;
      #       esac;;
    esac
done

if [[ ! $CONFIG ]]; then
    printf '%s\n' "No config specified. Exiting.">&2
    exit 1
fi
echo "config:	$CONFIG"

if [[ ! $TILE ]]; then
    printf '%s\n' "No tile specified. Exiting.">&2
    exit 1
fi
echo "tile:	$TILE"

if [[ ! $SEED ]]; then
    printf '%s\n' "No seed specified. Exiting.">&2
    exit 1
fi
echo "seed:	$SEED"

# shift "$OPTIND"
# remaining is "$@"

# Source the setup script from the script directory
source ./scripts/setup.sh
# source $(realpath $(dirname "$0")/setup.sh)

# Define run directory
RUN=$(basename $(dirname $CONFIG))

# Create the output directory
OUTPUT=$SCRATCH/y6-image-sims/$RUN/$TILE/$SEED
# If we have already run this seed, find a new one
while [ -d "$OUTPUT" ]
do
    echo "$OUTPUT already exists; trying a new seed"
    SEED=$RANDOM
    OUTPUT=$SCRATCH/y6-image-sims/$RUN/$TILE/$SEED
done
echo "Writing output to $OUTPUT"
mkdir -p $OUTPUT

srun_call="srun --exclusive --cpu-bind=cores --nodes=1 --ntasks=1 --output=logs/slurm-%J.out --error=logs/slurm-%J.log"

$srun_call run-eastlake-sim \
  -v 1 \
  --seed $SEED \
  $CONFIG \
  $OUTPUT/plus \
  stamp.shear.g1=0.02 stamp.shear.g2=0.00 output.tilename=$TILE \
  &  # run the process in the background so we can execute both job steps in parallel

$srun_call run-eastlake-sim \
  -v 1 \
  --seed $SEED \
  $CONFIG \
  $OUTPUT/minus \
  stamp.shear.g1=-0.02 stamp.shear.g2=0.00 output.tilename=$TILE \
  &  # run the process in the background so we can execute both job steps in parallel

# wait for each srun job to finish in the background
wait
