#!/bin/bash

if [ $# -lt 2 ]; then  
	echo "usage: $0 [input_directory] [output_directory]"
	exit 1;	
fi;

in_dir=$1
out_dir=$2

if [ -f header.txt ]; then 
	cat header.txt
else
	cat /home/yeunkimlocal/Documents/BIDS_conversion/header.txt
fi;


# echo "input directory= " ${in_dir}
# echo "output directory= " ${out_dir}

for i in `ls -d "${in_dir}"/* | xargs -n 1 basename`; do 

echo "    -"
echo "      in_dir: " ${in_dir}/${i}
echo "      out_dir: " ${out_dir}/${i}
echo "      filename: " ${i}

done

