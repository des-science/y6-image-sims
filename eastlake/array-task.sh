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
#SBATCH --output=logs/slurm_%A_%a.out
#SBATCH --error=logs/slurm_%A_%a.log

while getopts 'c:f:' opt; do
    case $opt in
        c) config=$OPTARG;;
        f) filename=$OPTARG;;
        \?)
            printf '%s\n' "Invalid option. Exiting">&2
            exit;;
    esac
done

echo "task: ${SLURM_ARRAY_TASK_ID}"

if [[ ! $config ]]; then
    printf '%s\n' "No config specified. Exiting.">&2
    exit 1
fi
echo "config: ${config}"

if [[ ! $filename ]]; then
    printf '%s\n' "No file specified. Exiting.">&2
    exit 1
fi
echo "file: ${filename}"

args=( $(sed -n "${SLURM_ARRAY_TASK_ID} p" $filename) )
echo "args: ${args[@]}"

tile=${args[0]}
if [[ ! $tile ]]; then
    printf '%s\n' "No tile found. Exiting.">&2
    exit 1
fi
echo "tile: ${tile}"

seed=${args[1]}
if [[ ! $seed ]]; then
    printf '%s\n' "No seed found. Exiting.">&2
    exit 1
fi
echo "seed: ${seed}"

# Source the setup script from the script directory
source setup.sh

# Define run directory
run=$(basename $config .yaml)
submitted="${filename%.*}-${run}-submitted.txt"
touch $submitted
echo $tile >> $submitted

# Create the output directory
output=${SCRATCH}/y6-image-sims/$run/$tile/$seed
echo "Writing output to $output"
mkdir -p $output

# srun_call=""
srun_call="srun --exclusive --cpu-bind=cores --nodes=1 --ntasks=1 --output=logs/slurm_%A_%a.%s.out --error=logs/slurm_%A_%a.%s.log"

# $srun_call run-eastlake-sim \
#     -v 1 \
#     --seed $seed \
#     $config \
#     $output/plus \
#     stamp.shear.g1=0.02 stamp.shear.g2=0.00 output.tilename=$tile \
#     &  # run the process in the background so we can execute both job steps in parallel
# 
# $srun_call run-eastlake-sim \
#     -v 1 \
#     --seed $seed \
#     $config \
#     $output/minus \
#     stamp.shear.g1=-0.02 stamp.shear.g2=0.00 output.tilename=$tile \
#     &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --g1 0.02 \
    --g2 0.00 \
    $config \
    $tile \
    $seed \
    ${output}/plus \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --g1 -0.02 \
    --g2 0.00 \
    $config \
    $tile \
    $seed \
    ${output}/minus \
    &  # run the process in the background so we can execute both job steps in parallel

# wait for each srun job to finish in the background
wait
