#!/bin/bash

if test -z $2; then
echo "Usage: $0 <destination> <lang>";
exit 1;
fi


destination=$1
lang=$2
bin_dir=`dirname $0`
script_root=${bin_dir}/../phone_align/

echo "Creating destination directory."
mkdir ${destination}

echo "Linking files"

for i in ${script_root}/base/*; do
ln -s `realpath $i` ${destination};
done

mkdir ${destination}/data
for i in ${script_root}/data_template/${lang}/*; do
ln -s `realpath $i` ${destination}/data;
done

mkdir ${destination}/exp
ln -s `realpath ${script_root}/exp_template/${lang}/extractor` ${destination}/exp
mkdir ${destination}/exp/tdnn_f_chain_1d
for i in `realpath ${script_root}/exp_template/${lang}/tdnn_f_chain_1d`/*; do
ln -s `realpath ${script_root}/exp_template/${lang}/tdnn_f_chain_1d`/$i ${destination}/exp/tdnn_f_chain_1d;
done
ln -s `realpath ${script_root}/exp_template/${lang}/tri3_${lang}` ${destination}/exp

