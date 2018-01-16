#!/bin/bash


if [ $# -lt 2 ]; then  
	echo "usage: $0 [file_with_input_directory_paths] [full_path_to_output_directory]"
	exit 1;	
fi;

in_dir=$1
out_dir=$2

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f header.txt ]; then 
	cat header.txt
else
	cat ${DIR}/header.txt
fi;

filterDirs () {
    subString=$1
    longString=$2
    outdirString=$3
    longStringdir="${longString##*/}"

    if [[ ${longStringdir} == *"${subString}"* ]] && [[ ${longStringdir} != *"SETTER"* ]] && [[ ${longStringdir} != *"PHYSIOLOG"* ]] && [[ ${longStringdir} != *"ASL"* ]] ; then
        fn="$(basename ${i})"
        mkdir -p ${outdirString}/${fn}

        echo "    -"
        echo "      in_dir: " ${longString}
        echo "      out_dir: " ${outdirString}/${fn}
        echo "      filename: " ${fn}
    fi
}
# echo "input directory= " ${in_dir}
# echo "output directory= " ${out_dir}

for i in `cat "${in_dir}"`; do
    case $i in

        *"T1W"*)
            filterDirs T1W ${i} ${out_dir}
            ;;
        *"T2W"*)
            filterDirs T2W ${i} ${out_dir}
            ;;
        *"RFMRI"*)
            filterDirs RFMRI ${i} ${out_dir}
            ;;
        *"FIELDMAP"*)
            filterDirs FIELDMAP ${i} ${out_dir}
            ;;
        *"TFMRI"*)
            filterDirs TFMRI ${i} ${out_dir}
            ;;
        *"DMRI"*)
            filterDirs DMRI ${i} ${out_dir}
            ;;
        *"DWI"*)
            filterDirs DWI ${i} ${out_dir}
            ;;
    esac
done




