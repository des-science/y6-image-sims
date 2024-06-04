#!/bin/bash
#SBATCH -J eastlake
#SBATCH -A des
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 06:00:00
#SBATCH --nodes=12
#SBATCH --ntasks=12
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
output=${SCRATCH}/y6-image-sims/campaigns/calibration/$run/$tile/$seed
echo "Writing output to $output"
mkdir -p $output

srun_call="srun --exclusive --cpu-bind=cores --nodes=1 --ntasks=1 --output=logs/slurm_%A_%a.%s.out --error=logs/slurm_%A_%a.%s.log"

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other 0.00 \
    --g2_other 0.00 \
    --zlow 0.0 \
    --zhigh 3.0 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=3.0 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice -0.02 \
    --g2_slice 0.00 \
    --g1_other 0.00 \
    --g2_other 0.00 \
    --zlow 0.0 \
    --zhigh 3.0 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=-0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=3.0 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 0.0 \
    --zhigh 0.3 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=0.0__zhigh=0.3 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 0.3 \
    --zhigh 0.6 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=0.3__zhigh=0.6 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 0.6 \
    --zhigh 0.9 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=0.6__zhigh=0.9 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 0.9 \
    --zhigh 1.2 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=0.9__zhigh=1.2 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 1.2 \
    --zhigh 1.5 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=1.2__zhigh=1.5 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 1.5 \
    --zhigh 1.8 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=1.5__zhigh=1.8 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 1.8 \
    --zhigh 2.1 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=1.8__zhigh=2.1 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 2.1 \
    --zhigh 2.4 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=2.1__zhigh=2.4 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 2.4 \
    --zhigh 2.7 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=2.4__zhigh=2.7 \
    &  # run the process in the background so we can execute both job steps in parallel

$srun_call python eastlake/task.py \
    --verbosity 1 \
    --attempt-resume \
    --shear_slice \
    --g1_slice 0.02 \
    --g2_slice 0.00 \
    --g1_other -0.02 \
    --g2_other 0.00 \
    --zlow 2.7 \
    --zhigh 3.0 \
    $config \
    $tile \
    $seed \
    ${output}/g1_slice=0.02__g2_slice=0.00__g1_other=-0.02__g2_other=0.00__zlow=2.7__zhigh=3.0 \
    &  # run the process in the background so we can execute both job steps in parallel

# wait for each srun job to finish in the background
wait
