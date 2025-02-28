#!/bin/bash

if [ $# -ne 3 ]; then
  echo "Usage: build_n_gram.sh <in:text> <in:order_n> <out:arpa>"
  echo "NB: Use full paths!!"
  exit 1
fi


text_in=$1
order=$2
lm_out=$3

lm_train_text=`dirname ${text_in}`/lm_train.txt
interm_lm=`dirname ${text_in}`/lm.ilm.gz

cat $text_in | sed -e 's:^:<s> :' -e 's:$: </s>:' > $lm_train_text
irstlm build-lm -i $lm_train_text -n $order -o $interm_lm
irstlm compile-lm $interm_lm -t=yes /dev/stdout | grep -v '<unk>'  > $lm_out
