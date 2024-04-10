#!/bin/bash

while getopts 't:s:' opt; do
    case $opt in
        t) tiles=$OPTARG;;
        s) seeds=$OPTARG;;
        \?)
            printf '%s\n' "Invalid option. Exiting">&2
            exit;;
    esac
done

if [[ ! $tiles ]]; then
    printf '%s\n' "No tiles specified. Exiting.">&2
    exit 1
fi
echo "tiles: $tiles"

if [[ ! $seeds ]]; then
    printf '%s\n' "No seeds specified. Exiting.">&2
    exit 1
fi
echo "seeds: $seeds"

paste -d ' ' $tiles $seeds | shuf > args-y6.txt
