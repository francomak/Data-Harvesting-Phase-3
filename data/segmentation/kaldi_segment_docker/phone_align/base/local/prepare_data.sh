#!/bin/bash
#
# Copyright  2015 University of Tehran (Author: Bagher BabaAli)
# Apache 2.0

. path.sh

export LC_ALL=C
if [ $# -ne 2 ]; then
   echo "Argument should be the speech data directory and language name, see ../run.sh for example."
   exit 1;
fi

lang=$2

dir=data/train_${lang}
mkdir -p $dir
gunzip -c $1/../nchlt_dictionaries/$lang/nchlt_${lang}.trn.lst.gz | ./local/flist2scp.pl - | awk -v lng=$lang '{printf("%s_%s\n",lng,$0);}' | sort | awk -v trans_path="$1/nchlt_${lang}/transcriptions/" '{printf"%s %s%s.txt\n",$1,trans_path,$2}' >$dir/txt.scp

dir=data/test_${lang}
mkdir -p $dir
gunzip -c $1/../nchlt_dictionaries/$lang/nchlt_${lang}.tst.lst.gz | ./local/flist2scp.pl - | awk -v lng=$lang '{printf("%s_%s\n",lng,$0);}' | sort | awk -v trans_path="$1/nchlt_${lang}/transcriptions/" '{printf"%s %s%s.txt\n",$1,trans_path,$2}' >$dir/txt.scp

dir=data/dev_${lang}
mkdir -p $dir
gunzip -c $1/../nchlt_dictionaries/$lang/nchlt_${lang}.dev.lst.gz | ./local/flist2scp.pl - | awk -v lng=$lang '{printf("%s_%s\n",lng,$0);}' | sort | awk -v trans_path="$1/nchlt_${lang}/transcriptions/" '{printf"%s %s%s.txt\n",$1,trans_path,$2}' >$dir/txt.scp

# Prepare: test, train,
for set in train test dev; do
  dir=data/${set}_${lang}
  # Do normalization step
  cat $1/../../kaldi_systems/NCHLT-PhonemeTranscriptions/${set}_${lang}/text.ph | sort > $dir/text || exit 1;

  # Create scp's with wav's
  awk '{printf("%s sox %s -t wav -r 16000 - |\n", $1, $2);}' < $dir/txt.scp | sed -e 's/transcriptions/audio/g' | sed -e 's/.txt/.wav/g' > $dir/wav.scp
  cat $dir/wav.scp | awk '{ print $1, $1, "A"; }' > $dir/reco2file_and_channel

  # Make the utt2spk and spk2utt files
  cut -d' ' -f1 $dir/txt.scp > $dir/uttids
  cut -c1-8 $dir/uttids | paste -d' ' $dir/uttids - > $dir/utt2spk
  cat $dir/utt2spk | utils/utt2spk_to_spk2utt.pl > $dir/spk2utt || exit 1;
 
 utils/validate_data_dir.sh --no-feats $dir || exit 1;
done

