#!/bin/bash


repos=(Csv Cli Lang Chart Gson)

revisions_dir=/data/share/defects4j_revisions
repo_type=b

export_revisions() {
	for repo in ${repos[@]}; do
		cd $revisions_dir
		results=(`defects4j query -p ${repo} -q "bug.id"`)
		for id in ${results[@]}; do
			repo_name=${repo}_${id}_${repo_type}
			( defects4j checkout -p $repo -v ${id}${repo_type} -w ${revisions_dir}/${repo_name} ) || continue
			cd $repo_name && defects4j compile
		done
	done
}


export_revisions


export_focal_classes() {
	json_array=[]
	for repo in ${repos[@]}; do
		results=`defects4j query -p ${repo} -q "classes.modified"`
		results=($(echo "$results" | sed 's/\"//g'))
		for res in ${results[@]}; do
			bugid=$(echo $res | cut -d "," -f 1)
			focal_classes=$(echo $res | cut -d "," -f 2)
			# IFS=';' read -ra focal_classes <<< "$focal_classes"
			focal_classes=$(echo $focal_classes | jq -R -s -c 'split(";")')
			revision=${repo}_${bugid}_${repo_type}
			echo "projcet: $revision class: ${focal_classes[@]}"
			json_array=$(echo "$json_array" | jq --arg project "${revision}" --argjson classes "$focal_classes" '. += [{"project": $project, "classes": $classes}]')
		done
	done
	echo $json_array > focal_classes.json
}

# export_focal_classes


export_focal_classes_json() {
	json_array=[]
	for i in ${!repos[@]}; do
		results=`defects4j query -p ${repos[$i]} -q "classes.modified"`
		results=$(echo "$results" | sed 's/[0-9]*,//g')
		results=$(echo "$results" | sed 's/\"//g')
		results=$(echo "$results" | sed 's/\;/\n/g')
		results=$(echo "$results" | sort | uniq)
		tag_array=$(echo "$results" | jq -R -s -c 'split("\n")')
		json_array=$(echo "$json_array" | jq --arg project "${repos[$i]}" --argjson classes "$tag_array" '. += [{"project": $project, "classes": $classes}]')
	done
	echo $json_array > focal_classes_nodup.json
}
