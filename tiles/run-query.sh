#!/bin/bash

source tiles/setup.sh

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

python tiles/query.py $filename --seed 13720
