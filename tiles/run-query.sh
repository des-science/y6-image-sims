#!/bin/bash

source setup.sh

while getopts 'f:' opt; do
    case $opt in
      (f)   FILE=$OPTARG;;
    esac
done

if [[ ! $FILE ]]; then
    printf '%s\n' "No file specified. Exiting.">&2
    exit 1
fi
echo "file:	$FILE"

python query.py $FILE --seed 13720
