#!/bin/bash
# Make dir-structure by package declaration
# Usage: bash make_struct test_source

WD=$(pwd)/tmp
test_suite=$1

mkdir $WD

echo $WD
prepare_test_suite() {
	cd $WD
	java_files=(`find $test_suite -name "*.java"`)
	for java_file in ${java_files[@]}; do
		process_single_test $java_file
	done
#	tar cvjf $tar_suite_name $PACKAGE_PATH > /dev/null
	echo prepare test suite finished
}

process_single_test() {
	cd $WD
	class=$1
	PACKAGE_PATH=$(grep -m 1 -o 'package.*;' $class | sed 's/package //;s/;//;s/\./\//g')
	# echo "========= package path : $PACKAGE_PATH ==========="
	if [ -n "$PACKAGE_PATH" ]; then
		mkdir -p $PACKAGE_PATH
	else
		PACKAGE_PATH=$class
	fi
#	echo $PACKAGE_PATH
  cp -r $class $PACKAGE_PATH
}

prepare_test_suite
