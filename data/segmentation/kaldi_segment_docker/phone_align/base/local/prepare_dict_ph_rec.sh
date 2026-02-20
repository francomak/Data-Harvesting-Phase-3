#!/bin/bash
#
# Copyright  2015 University of Tehran (Author: Bagher BabaAli)
# Apache 2.0

. path.sh

export LC_ALL=C
if [ $# -ne 1 ]; then
   echo "Argument should be the path to lexicon, see ../run.sh for example."
   exit 1;
fi

lang=$1
dir=data/local/dict_${lang}
mkdir -p $dir


# silence phones, one per line.
(echo sil; echo nse;) > $dir/silence_phones.txt
echo sil > $dir/optional_silence.txt

# nonsilence phones; on each line is a list of phones that correspond
# really to the same base phone.

# Create the lexicon, which is just an identity mapping
cut -d' ' -f2- data/train_${lang}/text | tr ' ' '\n' | sort -u | sed '/^$/d' > $dir/phones.txt
paste $dir/phones.txt $dir/phones.txt > $dir/lexicon.txt || exit 1;
grep -v -F -f $dir/silence_phones.txt $dir/phones.txt > $dir/nonsilence_phones.txt 


echo -n >$dir/extra_questions.txt

# Check that the dict dir is okay!
utils/validate_dict_dir.pl $dir || exit 1