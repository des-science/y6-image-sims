#!/bin/bash

source setup.sh

while getopts 'f:' opt; do
    case $opt in
        f) filename=$OPTARG;;
        \?)
            printf '%s\n' "Invalid option. Exiting">&2
            exit;;
    esac
done

if [[ ! $filename ]]; then
    printf '%s\n' "No file specified. Exiting.">&2
    exit 1
fi
echo "file: $filename"

python seeds/generate.py $filename --seed 42
