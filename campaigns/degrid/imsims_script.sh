#!/bin/bash

export USER=${GRID_USER}
echo $USER

source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh
setup ifdhc

which ifdh

cp ${CONDOR_DIR_INPUT}/.desservices.ini .
chmod og-rw .desservices.ini
cp ${CONDOR_DIR_INPUT}/.rsyncrc .
chmod og-rw .rsyncrc

label=${TILENAME}
export WORK_DIR=`pwd`

datestamp=`date +%Y%m%dT%H%M%S`

mkdir MEDS_DIR
mkdir IMSIM_DATA
mkdir TMPDIR
mkdir SCRATCH
mkdir .easyaccess
mkdir inputs

echo ${TILENAME}
echo ${HOME}

git clone https://github.com/des-science/y6-image-sims.git --branch 1.0.0 #The final tag, as of 07/31/2024
cd y6-image-sims;

####################################################################
# Make setup file.
# I do things this way because the env variable was being weird
# otherwise. It wasn't actually being read in correctly during
# source setup.sh. In script below the WORK_DIR is drop-in replaced
# during write, so env variable is never referenced.
#####################################################################

#/cvmfs/des.opensciencegrid.org/fnal/portconda/base311/bin

cat <<EOF > setup.sh
#!/bin/bash

export PATH=/cvmfs/des.opensciencegrid.org/fnal/miniforge3/bin:$PATH
source activate /cvmfs/des.opensciencegrid.org/fnal/stacks/des-y6

export DESDATA=${HOME}/DESDATA
export DESPROJ=OPS
export DESREMOTE=https://desar2.cosmology.illinois.edu/DESFiles/desarchive
export DESREMOTE_RSYNC=desar2.cosmology.illinois.edu::ALLDESFiles/desarchive
export DESREMOTE_RSYNC_USER=${USER}
export DES_RSYNC_PASSFILE=${HOME}/.rsyncrc

export IMSIM_DATA=${WORK_DIR}/IMSIM_DATA
export MEDS_DIR=${WORK_DIR}/IMSIM_DATA
export TMPDIR=${WORK_DIR}/TMPDIR
export SCRATCH=${WORK_DIR}/SCRATCH

# see https://joblib.readthedocs.io/en/latest/parallel.html#avoiding-over-subscription-of-cpu-resources
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
EOF

cat setup.sh

source setup.sh


##############################################################
# First find the right seed to use for this tile
##############################################################

INDEX=1 #Use the first (of ten) seed for the runs
eastlake_seed=$(awk -v s="${TILENAME}" -v col=$((INDEX + 1)) '$1 == s {print $col}' ./args-y6.txt)
eastlake_seed=$((eastlake_seed + 0)) #To force the variable to be a int (and not string)


###############################################################
# Use the Balrog env just for downloading stuff. Its hacky
# but it works :p The imsims one breaks during jobs on DEgrid
###############################################################

conda deactivate
source activate /cvmfs/des.opensciencegrid.org/fnal/portconda/des-y6-imsims-newenv

for band in g r i z
do
    echo "des-pizza-cutter-prep-tile --config meds/des-pizza-slices-y6.yaml --tilename ${TILENAME} --band $band"
    des-pizza-cutter-prep-tile --config meds/des-pizza-slices-y6.yaml --tilename ${TILENAME} --band $band
done
wait  # wait for each band to finish downloading


#Now switch to actual Imsims env for rest
conda deactivate
source activate /cvmfs/des.opensciencegrid.org/fnal/stacks/des-y6


echo "I HAVE FINISHED PREPPING"
ls -lsh

#Just set this to some short name so that SWARP doesn't break
MYPATH=RUN #${RUN_NAME}

echo "I am using ${MYPATH}"


###########################
# Replace paths in config
###########################

ifdh cp -D /pnfs/des/persistent/Y6Imsims/input_cosmos_v4.fits .
ifdh cp -D /pnfs/des/persistent/Y6Imsims/merged_y6/${TILENAME}.fits .
ifdh cp -D /pnfs/des/persistent/Y6Imsims/input_simcats_v7/cosmos_simcat_v7_${TILENAME}_seed${eastlake_seed}.fits .

#Some filepath changes
sed -i -e 's|/dvs_ro/cfs/cdirs/des/y3-image-sims/input_cosmos_v4.fits|/srv/y6-image-sims/input_cosmos_v4.fits|' ./campaigns/$CONFIG
sed -i -e 's|/dvs_ro/cfs/cdirs/desbalro/starsim/catalogs/merged_y6/|/srv/y6-image-sims/|' ./campaigns/$CONFIG
sed -i -e 's|$FITVD_ENV|/cvmfs/des.opensciencegrid.org/fnal/portconda/des-y6-fitvd-env|' ./campaigns/$CONFIG
sed -i -e 's|/dvs_ro/cfs/cdirs/desbalro/cosmos_simcat/cosmos_simcat_v7_|/srv/y6-image-sims/cosmos_simcat_v7_|' ./campaigns/$CONFIG

#Now some Njobs changes

sed -i 's/nproc: 64/nproc: 12/' ./campaigns/$CONFIG
sed -i '/^coadd_nwgint:/,/^[^ ]/s/n_jobs: 128/n_jobs: 12/' ./campaigns/$CONFIG
sed -i '/^desdm_meds:/,/^[^ ]/s/n_jobs: 128/n_jobs: 12/' ./campaigns/$CONFIG
sed -i '/^pizza_cutter:/,/^[^ ]/s/n_jobs: 32/n_jobs: 12/' ./campaigns/$CONFIG
sed -i '/^metadetect:/,/^[^ ]/s/n_jobs: 128/n_jobs: 12/' ./campaigns/$CONFIG


###########################
#RUN THE SIM!
###########################

#python3 eastlake/task.py --verbosity 0 --g1 ${SHEAR} --g2 0.00 ${CONFIG} ${TILENAME} ${eastlake_seed} ./${MYPATH}

python3 eastlake/task.py --verbosity 1 --shear_slice \
                         --g1_slice ${SHEAR} --g2_slice 0.00 --g1_other ${SHEAR_OTHER} --g2_other 0.00 --zlow ${ZLOW} --zhigh ${ZHIGH} \
                         ./campaigns/${CONFIG} ${TILENAME} ${eastlake_seed} ./${MYPATH}

ls -lsh "/srv/y6-image-sims/g1_slice=0.02__g2_slice=0.00__g1_other=0.00__g2_other=0.00__zlow=0.0__zhigh=6.0/des-pizza-slices-y6/DES0448-2706/sources-g/OPS_Taiga/multiepoch/Y6A1/r4939/DES0448-2706/p01/coadd"
cd $MYPATH


#################################
# Time to copy everything over
#################################

ifdh mkdir /pnfs/des/persistent/users/${USER}/Y6Imsims/${TILENAME}
ifdh mkdir /pnfs/des/persistent/users/${USER}/Y6Imsims/${TILENAME}/${RUN_NAME}
OUTPUT=/pnfs/des/persistent/users/${USER}/Y6Imsims/${TILENAME}/${RUN_NAME}

ifdh cp -D config.yaml ${OUTPUT}
ifdh cp -D job_record.pkl ${OUTPUT}
ifdh cp -D orig-config.yaml ${OUTPUT}

#Get meds files and yaml files
cd ./des-pizza-slices-y6/${TILENAME}
for f in $(ls ./DES*.fits.fz); do ifdh cp -D ${f} ${OUTPUT}; done;
for f in $(ls ./*.yaml); do ifdh cp -D ${f} ${OUTPUT}; done;


#mdet files
cd metadetect
ifdh mkdir ${OUTPUT}/metadetect
for f in $(ls ./${TILENAME}_*); do ifdh cp -D ${f} ${OUTPUT}/metadetect; done;


#fitvd files
cd ../fitvd
ifdh mkdir ${OUTPUT}/fitvd
for f in $(ls ./${TILENAME}_*); do ifdh cp -D ${f} ${OUTPUT}/fitvd; done;

cd ../../pizza_cutter_info
ifdh mkdir ${OUTPUT}/pizza_cutter_info
for f in $(ls ./${TILENAME}_*); do ifdh cp -D ${f} ${OUTPUT}/pizza_cutter_info; done;

#fitvd files
cd ../../true_positions
for f in $(ls ./${TILENAME}-*); do ifdh cp -D ${f} ${OUTPUT}; done;

cd ../truth_files
for f in $(ls ./${TILENAME}-*); do ifdh cp -D ${f} ${OUTPUT}; done;


################################
#Now do bfd steps
################################

cd ${WORK_DIR}

ifdh cp -D /pnfs/des/persistent/Y6balrog/setupBFDRun.sh .
ifdh cp -D /pnfs/des/persistent/Y6balrog/configs/bfd_config.yaml .

ifdh cp -D /pnfs/des/persistent/Y6balrog/BFD_data/PSF_cuts.npy .
ifdh cp -D /pnfs/des/persistent/Y6balrog/BFD_data/coadd_id_reserved_stars_c.npy.npz .
ifdh cp -D /pnfs/des/persistent/Y6balrog/BFD_data/zero_point_efficiency.npy .

conda deactivate
source setupBFDRun.sh

mkdir MEDS
mkdir SOF

ls -lsh

#Copy over meds + sof file to current directory, 
#so we have the right directory structure
for f in $(ls ./y6-image-sims/${MYPATH}/des-pizza-slices-y6/${TILENAME}/DES*meds-des-*.fits.fz); do cp ${f} ./MEDS/; done;
for f in $(ls ./y6-image-sims/${MYPATH}/des-pizza-slices-y6/${TILENAME}/fitvd/*sof.fits); do cp ${f} ./SOF/; done;


ls -lsh

#Substitute env variables in yaml file
envsubst < bfd_config.yaml > tmp_config.yaml
cat tmp_config.yaml

#Clone bfd repo
#Remove instances of frogress in source code since progressbars 
#don't work on DEGrid :P
git clone https://github.com/mgatti29/BFD_pipeline.git --branch v0.5.2

cd BFD_pipeline
find . -type f -name "*.py" -exec sed -i 's/frogress.bar(/(/g' {} +
cd ../

#Actually run BFD :P
python -u ./BFD_pipeline/run_bfd.py --config ./tmp_config.yaml --output_label _BFD > logbfd_${TILENAME}

found_file=$(find ./SOF/ -type f -name "*sof.fits")
file_name=$(basename "$found_file")
new_file_name="${file_name//"sof"/"bfd"}"

echo "GETTING NEW FILE NAME"
echo $new_file_name

#Transfer over!
ifdh mkdir ${OUTPUT}/bfd
ifdh cp -D logbfd_${TILENAME} ${OUTPUT}/bfd
ifdh cp targets/*BFD.fits ${OUTPUT}/bfd/${new_file_name}
