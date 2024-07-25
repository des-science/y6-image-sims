#!/bin/bash

#Quick check for now
if [ "$USER" != "dhayaa" ]; then
  echo "Warning: This script is hardcoded to Dhayaa's NERSC paths. Modify script before running it."
  exit 1
fi


#Tilepath is passed in during runtime.
#Everything else is derived from this path.
#Example is "/pscratch/sd/s/smau/y6-image-sims/fiducial/DES0152-4957/159551638"
#So you must pass in the randomseed as well in the path
tilepath=$1
SEEDSTR=$(basename "$tilepath")
tilename=$(basename "$(dirname "$tilepath")")
logfile=bfd_$tilename.log

echo "Logging to file: ${logfile}"
echo "Starting BFD for tile: $tilename"
echo "Starting BFD for seed: $SEEDSTR"

# Copy all files to TMPDIR. This copies all versions available. So plus, minus, ....
cp -ruv ${tilepath}/* /${TMPDIR}

for mode in "$TMPDIR"/*; #Loop over plus, minus, ...
do
    mode=$(basename $mode) #Only take the basename
    echo "RUNNING MODE ${mode}"
    
    # The run for this mode is stored in a separate file
    TMPPATH=$TMPDIR/$mode
    
    # Find SOF and MEDS files
    SOF=$(find  "$TMPPATH/des-pizza-slices-y6/${tilename}/fitvd" -name "*sof*.fits" | head -n 1)
    MEDS=$(find "$TMPPATH/des-pizza-slices-y6/${tilename}/" -name "*meds*.fits.fz")
    
    # Find SOF filename and replace it with bfd to get bfd filename.
    # This keeps the PROC ID in there.
    file_name=$(basename "$SOF")
    new_file_name="${file_name//"sof"/"bfd"}"

    # Create directories expected by BFD code
    mkdir -p "${TMPPATH}/fitvd" "${TMPPATH}/meds" "${TMPPATH}/bfd"

    # Copy SOF and MEDS files to their respective directories
    cp -v "$SOF" "${TMPPATH}/fitvd/"
    for m in $MEDS; do cp -v "$m" "${TMPPATH}/meds/"; done

    # Prepare arguments for the configuration file
    TILENAME=$tilename
    MEDSDIR="${TMPPATH}/meds"
    SOFDIR="${TMPPATH}/fitvd"
    OUTDIR="${TMPPATH}/bfd"

    # Print the args
    echo "TILENAME: $TILENAME"
    echo "MEDSDIR: $MEDSDIR"
    echo "SOFDIR: $SOFDIR"
    echo "OUTDIR: $OUTDIR"

    # Configuration text.
    CONFIG_TEXT=$(cat <<EOF
run:
     - measure_moments_targets
     #- target_noise_tiers

######################################################################
#                       general config
######################################################################

general:
    output_folder:  '$OUTDIR'

    # BFD window function parameters. Defaults: n = 4, sigma = 0.65
    filter_sigma: 0.65

    # per-band weights.
    bands_meds_files: ['g','r','i','z']
    bands_weights: [0.,0.6,0.3,0.1]

    # pad factor for the FFT of the images. Default: 2. 
    FFT_pad_factor: 2.

    # whether if you want to use MPI or not.
    MPI: True


######################################################################
#                       measure_moments_targets
######################################################################

measure_moments_targets:
    flagged_exp_list: '/global/homes/d/dhayaa/BalrogY6/BFD_pipeline/data/PSF_cuts.npy'
    reserved_stars_list: '/global/homes/d/dhayaa/BalrogY6/BFD_pipeline/data/coadd_id_reserved_stars_c.npy.npz'
    efficiency_list: '/global/homes/d/dhayaa/BalrogY6/BFD_pipeline/data/zero_point_efficiency.npy'
    debug: False
    debug_SN : False
    compute_shotnoise: True
    max_frac_stamp_masked: 0.05
    chunk_size: 650
    agents: 128

    path_MEDS: '$MEDSDIR'
    path_galaxy_models: '$SOFDIR'
    tiles: ['$TILENAME']


######################################################################
#                       measure_moments_targets
######################################################################

target_noise_tiers:
    gold_id: '/global/cfs/cdirs/des/BFD_Y6/gold_id.npy' # it could be None
    star_galaxy_separation_value: 3.5 # Mr/Mf < star_galaxy_separation
    flux_covariance_maps_nside: 4096 # 
    overwrite_noisetiers: False
    sn_min: 7
    sn_max: 200
    noiseStep: .3
    psfStep: .3
EOF
)

    # Write the configuration text to a file
    echo "$CONFIG_TEXT" > "${TMPPATH}/config.yaml"
    echo "Config file created at: ${TMPPATH}/config.yaml"

    #Now actually run the BFD pipeline
    python $HOME/BalrogY6/BFD_pipeline/run_bfd.py --config $TMPPATH/config.yaml --output_label _BFD
    echo "BFD Finished"
    echo "Final cleanup and moving logfile"
    
    #Now move the new file back to the original path
    NEWPATH=${tilepath}/${mode}/des-pizza-slices-y6/${tilename}
    echo "Sending files back to ${NEWPATH}"
    mkdir $NEWPATH/bfd
    mv -v $OUTDIR/targets/targets_${tilename}_BFD.fits $NEWPATH/bfd/${new_file_name}
    # mv -v $logfile ${tilepath}/${SEEDSTR}/${mode}/${tilepath}/$logfile #Skipping logfile

done

#Cleanup existing files and directories to prep for the next run
rm -rv ${TMPDIR}/*
