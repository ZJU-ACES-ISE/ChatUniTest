#!/bin/bash

# Find all directories with coverage.xml files

target_dir=$1
xml_dirs=(`find $target_dir -name "coverage.xml"`)
temp_dirs=(`find $target_dir -name temp -type d`)

echo "######################################## Success tests more than 1 round #########################################"

# Iterate through each directory
count1=0
for dir in ${xml_dirs[@]}; do
    # Check if the directory contains any GPT JSON files
	dir=${dir%/temp/coverage.xml}
    num_json=$(find "$dir" -name "*GPT*.json" | wc -l)
    
    # If there are GPT JSON files, print the directory name and the number of files
    if [[ $num_json -gt 1 ]]; then
        # echo "Directory: $dir"
        echo "Number: $num_json"
		((count1++))
    fi
done

echo "count: $count1"

# echo "Total num: ${#temp_dirs}"
# echo "Success num: ${#xml_dirs}"

echo "######################################## All tests more than 1 round #########################################"

count2=0
for dir in ${temp_dirs[@]}; do
    # Check if the directory contains any GPT JSON files
	dir=${dir%/temp}
    num_json=$(find "$dir" -name "*GPT*.json" | wc -l)
    
    # If there are GPT JSON files, print the directory name and the number of files
    if [[ $num_json -gt 1 ]]; then
        # echo "Directory: $dir"
        echo "Number: $num_json"
		((count2++))
    fi
done

echo "count: $count2"

