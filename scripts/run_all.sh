while getopts 'c:t:s:' opt; do
    case $opt in
      (c)   CONFIG=$OPTARG;;
      (t)   TILES=$OPTARG;;
    esac
done

if [[ ! $CONFIG ]]; then
    printf '%s\n' "No config specified. Exiting.">&2
    exit 1
fi
echo "config:	$CONFIG"

# if [[ ! $TILES ]]; then
#     printf '%s\n' "No tiles specified. Exiting.">&2
#     exit 1
# fi
# echo "tile:	$TILE"

# for tile in $(cat $TILES);
# do
#     echo "sbatch scripts/run.sh -c $CONFIG -t $tile -s $RANDOM"
# done

for tile in $(find /global/cfs/cdirs/des/y6-image-sims/des-pizza-slices-y6-v16/ -mindepth 1 -maxdepth 1 -type d -regex '/global/cfs/cdirs/des/y6-image-sims/des-pizza-slices-y6-v16/DES[0-9]+.[0-9]+' -printf '%f\n')
do
        SEED=$RANDOM
        echo "sbatch scripts/run.sh -c $CONFIG -t $tile -s $SEED"
        sbatch scripts/run.sh -c $CONFIG -t $tile -s $SEED
        sleep 1
done
