#!/bin/bash
# DATE=$(date -v -1d +%Y-%m-%d)


DATE="2023-08-24"
STANDARD="SP2209+178"
declare -a OBJECTS=("ZTF23aaspcfl" "ZTF23aalftvv")

DL_DIR="/Users/simeon/Downloads"
PYPEIT_DIR="/Users/simeon/not/pypeit_alfosc_env"
REDUCER_NAME="Simeon Reusch"
cd ${PYPEIT_DIR}

cp ${DL_DIR}/${DATE}.zip ${PYPEIT_DIR}/raw/
unzip ${PYPEIT_DIR}/raw/${DATE}.zip -d ${PYPEIT_DIR}/raw
mv ${PYPEIT_DIR}/raw/${DATE}/alfosc/*.fits  ${PYPEIT_DIR}/raw/${DATE}/
mv ${PYPEIT_DIR}/raw/${DATE}/alfosc/calib/*.fits  ${PYPEIT_DIR}/raw/${DATE}/
rm -rf ${PYPEIT_DIR}/raw/${DATE}/alfosc/calib ${PYPEIT_DIR}/raw/${DATE}/alfosc
rm ${PYPEIT_DIR}/raw/${DATE}.zip

scripts/create_datasets.py $DATE
ls datasets/$DATE*pypeit | grep "ZTF\|$STANDARD" | xargs -n 1 -P 4 run_pypeit
scripts/create_sensfunc.py $DATE
ls sci/$DATE-ZTF${DATE:2:2}a*/spec1d*.fits | grep ZTF | xargs -n 1 -P 1 scripts/apply_fluxcal.py

for OBJ in ${OBJECTS[@]}; do
 scripts/combine_spectra.py -o sci/${DATE}-${OBJ}/${OBJ}_${DATE}.fits sci/${DATE}-${OBJ}/spec1d_*.fits
 scripts/convert_spec1d.py sci/${DATE}-${OBJ}/${OBJ}_${DATE}.fits datasets/${DATE}-${OBJ}.pypeit --obs-name "${REDUCER_NAME}" --red-name "${REDUCER_NAME}" --wlen-min 3700
done

jupyter notebook scripts/upload_fritz_pypeit_simeon.ipynb
