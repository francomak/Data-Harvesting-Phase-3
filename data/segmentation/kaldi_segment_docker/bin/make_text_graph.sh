#!/bin/bash

dimensions=3

if test $# -ne 3; then
echo "Usage: $0 <dictionary_file> <language_code> <input_text_file>" >&2
exit 1;
fi

base_dir=`dirname $0`
utils_dir=${base_dir}/../phone_align/base/utils/
dict_file=$1
lang=$2
chain_dir=${base_dir}/../phone_align/exp_template/${lang}/tdnn_f_chain_1d
${base_dir}/build_n_gram.sh $3 ${dimensions} text.arpa
${base_dir}/create_kaldi_arpa_based_decoding_graph.py -M ${chain_dir} -U ${utils_dir} -D ${dict_file} -T text.arpa -s text_graph
cp -r text_graph exp/tdnn_f_chain_1d/textgraph

