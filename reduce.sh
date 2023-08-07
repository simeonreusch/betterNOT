#!/bin/bash
# DATE="2023-08-06"
DATE=$(date -v -1d +%Y-%m-%d)
STANDARD="SP2209+178"
declare -a OBJECTS=("ZTF23aarrwwl")

DL_DIR="/Users/simeon/Downloads"
PYPEIT_DIR="/Users/simeon/not/pypeit_alfosc_env"
REDUCER_NAME="Simeon Reusch"

cp ${DL_DIR}/${DATE}.zip ${PYPEIT_DIR}/raw/
unzip ${PYPEIT_DIR}/raw/${DATE}.zip -d ${PYPEIT_DIR}/raw
mv ${PYPEIT_DIR}/raw/${DATE}/alfosc/*.fits  ${PYPEIT_DIR}/raw/${DATE}/
mv ${PYPEIT_DIR}/raw/${DATE}/alfosc/calib/*.fits  ${PYPEIT_DIR}/raw/${DATE}/
rm -rf ${PYPEIT_DIR}/raw/${DATE}/alfosc/calib ${PYPEIT_DIR}/raw/${DATE}/alfosc
rm ${PYPEIT_DIR}/raw/${DATE}.zip

cd ${PYPEIT_DIR}

scripts/create_datasets.py $DATE
ls datasets/$DATE*pypeit | grep "ZTF\|$STANDARD" | xargs -n 1 -P 4 run_pypeit
scripts/create_sensfunc.py $DATE
ls sci/$DATE-ZTF${DATE:2:2}a*/spec1d*.fits | grep ZTF | xargs -n 1 -P 1 scripts/apply_fluxcal.py

for OBJ in ${OBJECTS[@]}; do
 scripts/combine_spectra.py -o sci/${DATE}-${OBJ}/${OBJ}_combined.fits sci/${DATE}-${OBJ}/spec1d_*.fits
 scripts/convert_spec1d.py sci/${DATE}-${OBJ}/${OBJ}_combined.fits datasets/${DATE}-${OBJ}.pypeit --obs-name $REDUCER_NAME --red-name $REDUCER_NAME
done