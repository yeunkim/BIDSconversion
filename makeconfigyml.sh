#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ $# -lt 2 ]; then  
	echo "usage: $0 [file_with_input_directory_paths] [full_path_to_output_directory]"
	exit 1;	
fi;

in_dir=$1
out_dir=$2

if [ -f header.txt ]; then 
	cat header.txt
else
	cat ${DIR}/header.txt
fi;


# echo "input directory= " ${in_dir}
# echo "output directory= " ${out_dir}

for i in `cat "${in_dir}"`; do
fn="$(basename ${i})"
mkdir ${out_dir}/${fn}
done;

for i in `cat "${in_dir}"`; do
fn="$(basename ${i})"
echo "    -"
echo "      in_dir: " ${i}
echo "      out_dir: " ${out_dir}/${fn}
echo "      filename: " ${fn}

done

