#!/bin/bash
# Usage: bash run_extract_class.sh

#######################################################
# Only need to modify the following variables 

repos_path=/root/data/defects4j_dataset_src
grammar_file=/root/TestGPT_ASE/src/parse_scripts/java-grammar.so
output_path=/root/data/defects4j_dataset_parsed

#######################################################

repos=(`ls ${repos_path}`)

if [ ! -d $output_path ]; then
	mkdir $output_path
fi

for repo in ${repos[@]}; do
	python extract_classes_info.py --repo_path ${repos_path}/${repo} --grammar ${grammar_file}  --output ${output_path}/${repo}
done
