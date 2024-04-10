#!/bin/bash

source setup.sh

while getopts 'f:' opt; do
    case $opt in
        (f) filename=$OPTARG;;
    esac
done

if [[ ! $filename ]]; then
    printf '%s\n' "No file specified. Exiting.">&2
    exit 1
fi
echo "file:	$filename"

# make sure the downloaded list file exists if not present
downloaded="${filename%.*}-downloaded.txt"
touch $downloaded
# e.g., for tile not in the finished list
for tile in $(comm -23 <(sort $filename) <(sort $downloaded))
do
# download all bands for a given tile in parallel
    for band in g r i z
    do
        echo "des-pizza-cutter-prep-tile --config meds/des-pizza-slices-y6.yaml --tilename $tile --band $band"
        des-pizza-cutter-prep-tile --config meds/des-pizza-slices-y6.yaml --tilename $tile --band $band &
    done
    wait  # wait for each band to finish downloading
    echo $tile >> $downloaded
    done
wait  # wait for each tile to finish downloading
echo "finished downlading all tiles"

# for i in {0..9}  # number of processes determined by number of locks
# do
#     for j in {0..100}
#     do
#         flock --verbose /tmp/flock-$i sleep $((1 + $RANDOM % 2)) &
#         echo "submitted job $j on lock $i"
#     done
# done
# echo "done"

