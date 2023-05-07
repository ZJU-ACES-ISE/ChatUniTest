#!/bin/bash

test_suite=$1
project_path=$2
# Optional
instrument_class=$3

source_dir=$(pwd)

project_name=`basename $project_path`
test_num=$(echo "$test_suite" | rev | cut -d/ -f2 | rev)
method_name=$(echo "$test_suite" | rev | cut -d/ -f3 | rev)
tar_suite_name=${project_name}_${method_name}.${test_num}.tar.bz2

WD=${test_suite%/temp}
WD=${WD}/runtemp

if [ ! -d $WD ]; then
	mkdir -p $WD
fi

# javapath=/data/chenyi/jvm/jdk1.8.0_202
# if [ ! "$JAVA_HOME" = "$javapath" ]; then
#     echo "JAVA_HOME should set to $javapath !!!"
# 	exit 1
# fi

prepare_test_suite() {
	cd $WD
	java_files=(`find $test_suite -name "*.java"`)
	for java_file in ${java_files[@]}; do
		process_single_test $java_file
	done
	tar cvjf $tar_suite_name $PACKAGE_PATH > /dev/null
	echo prepare test suite finished
}

process_single_test() {
	cd $WD
	class=$1
	PACKAGE_PATH=$(grep -o 'package.*;' $class | sed 's/package //;s/;//;s/\./\//g')
	# echo "========= package path : $PACKAGE_PATH ==========="
	if [ -n "$PACKAGE_PATH" ]; then
		mkdir -p $PACKAGE_PATH
		cp -r $class $PACKAGE_PATH
	else
		PACKAGE_PATH=$class
	fi

}

run_test() {
	cd $WD
	cp -r ${project_path} ${WD}
	project_path=${WD}/${project_name}
	# cd $project_path
	# remove_files
	if [ ! -n $instrument_class ]; then
		defects4j coverage -w $project_path -s ${WD}/${tar_suite_name} -i $instrument_class
	else
		defects4j coverage -w $project_path -s ${WD}/${tar_suite_name}
	fi

	if [ $? -ne 0 ];then
    rm -rf $WD
    cd $source_dir
		exit 1
	else
		get_results
    rm -rf $WD
    cd $source_dir
		exit 0
	fi
	cd $WD
}

get_results() {
	if [ -s ${project_path}/failing_tests ]; then
		cp ${project_path}/failing_tests ${test_suite}/runtime_error.txt
		return
	fi
	
	if [ -f ${project_path}/coverage.xml ]; then
		cp ${project_path}/coverage.xml ${test_suite} 
		cp ${project_path}/summary.csv  ${test_suite}
		cp ${project_path}/all_tests  ${test_suite}
	fi

}

get_errors() {
	if [ -f ${project_path}/failing_tests ]; then
		cp ${project_path}/failing_tests ${test_suite}/runtime_error.txt
	fi
}

get_full_classname() {
	repo=$1
	target_class=$2
	tmp_dirs=(`find $repo -wholename "*src/main/java" -type d`)	
	for tmp_dir in ${tmp_dirs[@]}; do
        java_files=(`find $tmp_dir -name "*.java" -type f`) 
        tmp_dir=${tmp_dir##*${repo}/}
        for file in ${java_files[@]}; do
			filename=`basename $file`
			filename=${filename%.*}
			if [[ $filename == $target_class ]]; then
				full_name=${file%.java}
				full_name=`echo ${full_name##*${tmp_dir}/} | tr "/" "."`
				echo $full_name
			fi
        done
    done
}
# get_full_classname $1 $2

remove_files() {
	files=(summary.csv all_tests failing_tests coverage.xml)
	for file in ${files[@]}; do
		if [ -f $file ]; then
			rm -f $file
		fi
	done
}

clean_wd() {
	echo clean working directory...
	if [ -d $WD ];then
		rm -rf ${WD}
	fi
}

prepare_test_suite
run_test

# should not clean if using threads or multi-process
# clean_wd

