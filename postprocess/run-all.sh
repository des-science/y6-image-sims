#!/bin/bash
#SBATCH -J pizza-patches
#SBATCH -A des
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 04:00:00
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32GB
#SBATCH --output=logs/slurm_%j.out
#SBATCH --error=logs/slurm_%j.log

while getopts 'c:s:' opt; do
    case $opt in
        c) config=$OPTARG;;
        s) shear=$OPTARG;;
        \?)
            printf '%s\n' "Invalid option. Exiting">&2
            exit;;
    esac
done

if [[ ! $config ]]; then
    printf '%s\n' "No config specified. Exiting.">&2
    exit 1
fi
echo "config: ${config}"

if [[ ! $shear ]]; then
    printf '%s\n' "No shear specified. Exiting.">&2
    exit 1
fi
echo "shear: ${shear}"

run=$(basename ${config} .yaml)

source setup.sh

echo "running step_00_make_flist"
bash postprocess/step_00_make_flist.sh -c ${config} -s ${shear}
echo "done"

echo "running step_01_make_uids"
bash postprocess/step_01_make_uids.sh -c ${config} -s ${shear}
echo "done"

echo "running step_02_make_cuts"
bash postprocess/step_02_make_cuts.sh -c ${config} -s ${shear}
echo "done"

echo "running step_03_make_hdf5"
bash postprocess/step_03_make_hdf5.sh -c ${config} -s ${shear}
echo "done"

echo "cleaning up..."

output_flist=${run}-${shear}_flist.txt
if [[ ! -f ${output_flist} ]]; then
    echo "flist not found!"
    echo "expected ${output_flist}"
    exit
else
    echo "removing ${output_flist}"
    rm -v ${output_flist}
fi

output_uids=${run}-${shear}_uids.yaml
if [[ ! -f ${output_uids} ]]; then
    echo "uids not found!"
    echo "expected ${output_uids}"
    exit
else
    echo "removing ${output_uids}"
    rm -v ${output_uids}
fi
