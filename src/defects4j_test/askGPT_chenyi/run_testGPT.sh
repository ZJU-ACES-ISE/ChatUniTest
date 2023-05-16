#!/bin/bash
# Usage: bash run_testGPT.sh

#########################################

CLASS_INFO_DIR=/data/share/testGPT_dataset_parsed
RESULT=../results

#########################################

# repos=(`ls ${CLASS_INFO_DIR}`)
repos=(jfreechart gson)

for repo in ${repos[@]}; do
	class_infos=(`ls ${CLASS_INFO_DIR}/${repo}/0/`)
	for class_info in ${class_infos[@]}; do
		python testGPT.py --class ${CLASS_INFO_DIR}/${repo}/0/${class_info} --output ${RESULT}/${repo}/
	done
done
