#!/bin/bash 
#
# Copyright  2014 Nickolay V. Shmyrev 
# Apache 2.0


. path.sh
export LC_ALL=C
export IRSTLM=/home/bagher/kaldi-trunk/tools/irstlm
#if [ $# -ne 2 ]; then
#   echo "Arguments should be the path to text corpus and language type, see ../run.sh for example."
#   exit 1;
#fi

text=$1
lang=$2

# run this from ../
srcdir=data/train_${lang}
dir=data/local/dict_${lang}
lmdir=data/local/nist_lm_${lang}
tmpdir=data/local/lm_tmp_${lang}
rm -rf $dir $lmdir $tmpdir
mkdir -p $dir $lmdir $tmpdir

[ -z "$IRSTLM" ] && \
   echo "LM building won't work without setting the IRSTLM env variable" && exit 1;
#! which build-lm.sh 2>/dev/null  && \
#   echo "IRSTLM does not seem to be installed (build-lm.sh not on your path): " && \
#   echo "go to <kaldi-root>/tools and try 'make irstlm_tgt'" && exit 1;

# cat $text | sed -e 's:^:<s> :' -e 's:$: </s>:' > $srcdir/lm_train.text
# #cut -d' ' -f2- data/train_${lang}/text | sed -e 's:^:<s> :' -e 's:$: </s>:' > $srcdir/lm_train.text #Get text of train utterances
# 
# /home/bagher/kaldi-trunk/tools/irstlm/bin/build-lm.sh -i $srcdir/lm_train.text -n 3 -o $tmpdir/lm.ilm.gz
# 
# /home/bagher/kaldi-trunk/tools/irstlm/bin/compile-lm $tmpdir/lm.ilm.gz -t=yes /dev/stdout | grep -v unk  > $lmdir/lm.arpa 
# 
# 
# arpa_lm=$lmdir/lm.arpa 

arpa_lm=$1 #Read existing LM as input

[ ! -f $arpa_lm ] && echo No such file $arpa_lm && exit 1;

lang_test=data/lang_test_${lang}
rm -rf ${lang_test}
cp -r data/lang_${lang} ${lang_test}
cat $arpa_lm | utils/find_arpa_oovs.pl ${lang_test}/words.txt > ${lang_test}/oovs.txt

# grep -v '<s> <s>' etc. is only for future-proofing this script.  Our
# LM doesn't have these "invalid combinations".  These can cause 
# determinization failures of CLG [ends up being epsilon cycles].
# Note: remove_oovs.pl takes a list of words in the LM that aren't in
# our word list.  Since our LM doesn't have any, we just give it
# /dev/null [we leave it in the script to show how you'd do it].
cat "$arpa_lm" | \
   grep -v '<s> <s>' | \
   grep -v '</s> <s>' | \
   grep -v '</s> </s>' | \
   arpa2fst - | fstprint | \
   utils/remove_oovs.pl ${lang_test}/oovs.txt | \
   utils/eps2disambig.pl | utils/s2eps.pl | fstcompile --isymbols=${lang_test}/words.txt \
     --osymbols=${lang_test}/words.txt  --keep_isymbols=false --keep_osymbols=false | \
    fstrmepsilon | fstarcsort --sort_type=ilabel > ${lang_test}/G.fst


echo  "Checking how stochastic G is (the first of these numbers should be small):"
fstisstochastic ${lang_test}/G.fst

utils/validate_lang.pl ${lang_test} || exit 1;

exit 0;
