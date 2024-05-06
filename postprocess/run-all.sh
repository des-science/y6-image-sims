#!/bin/bash

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

echo "running step_00_make_flist"
bash postprocess/step_00_make_flist.sh -c ${config} -s ${shear}
echo "done"

echo "running step_02_make_cuts"
bash postprocess/step_02_make_cuts.sh -c ${config} -s ${shear}
echo "done"

echo "running step_03_make_hdf5"
bash postprocess/step_03_make_hdf5.sh -c ${config} -s ${shear}
echo "done"
