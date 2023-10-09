#!/bin/bash

source meds/setup.sh

export DES_RSYNC_PASSFILE=/global/cfs/cdirs/des/y6-image-sims/rsync_pass-smau.txt
export DESREMOTE_RSYNC=smau@desar2.cosmology.illinois.edu::ALLDESFiles/new_archive/desarchive/
export MEDS_DIR=/global/cfs/cdirs/des/y6-image-sims

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

# make sure the finished list file exists if not present
finished="${filename%.*}-finished.txt"
touch $finished
# e.g., for tile not in the finished list
for tile in $(comm -23 $filename $finished)
do
	# download all bands for a given tile in parallel
	for band in g r i z
	do
		echo "des-pizza-cutter-prep-tile --config meds/des-pizza-slices-y6.yaml --tilename $tile --band $band"
		# des-pizza-cutter-prep-tile --config meds/des-pizza-slices-y6.yaml --tilename $tile --band $band &
	done
	wait  # wait for each band to finish downloading
	echo "finished tile $tile"
	echo $tile >> $finished
done
wait  # wait for each tile to finish downloading
echo "finished downlading all tiles"

# for i in {0..9}  # number of processes determined by number of locks
# do
# 	for j in {0..100}
# 	do
# 		flock --verbose /tmp/flock-$i sleep $((1 + $RANDOM % 2)) &
# 		echo "submitted job $j on lock $i"
# 	done
# done
# echo "done"

