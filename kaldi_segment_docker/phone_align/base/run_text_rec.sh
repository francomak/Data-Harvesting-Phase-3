#!/bin/bash

#REMEMBER TO DELETE THE DATA AND DECODE DIRS FOR EACH RUN (CHECK MFCC AND IVECTORS)

. ./cmd.sh
[ -f path.sh ] && . ./path.sh

# Lexicon and Language Model Parameters
oovsymbol="<unk>"

train_nj=1
decode_nj=1
main_lang=$1 #required for tri3 alignment
lang=${main_lang}_aligned

. utils/parse_options.sh # accept options


audio_path=$2
audio_list_file=$3

gf_dir=textgraph #Decode graph to use - create/re-use one for free phone recognition
scoring_weight=3 #Used to copy best phone transcription for subsequent alignment

#if false; then
echo ============================================================================
echo "         Data files prep and MFCC Feature Extraction           "
echo ============================================================================


python2.7 local/prepare_test_data_no_transcriptions_utt_spk.py -A $audio_path -L $lang -S $audio_list_file || exit 1


mfccdir=mfcc_harvest_${lang}
for x in harvest; do
  echo steps/make_mfcc.sh --cmd "$train_cmd" --nj $train_nj data/${x}_${lang} exp/make_mfcc/${x}_${lang} $mfccdir
  steps/make_mfcc.sh --cmd "$train_cmd" --nj $train_nj data/${x}_${lang} exp/make_mfcc/${x}_${lang} $mfccdir
  utils/fix_data_dir.sh data/${x}_${lang}; # run by hand due to an error in previous step
done

cmvndir=mfcc_cmvn_harvest_${lang}
for x in harvest; do 
  steps/compute_cmvn_stats.sh data/${x}_${lang} exp/make_mfcc/$x_${lang} $cmvndir
  utils/fix_data_dir.sh data/${x}_${lang}; # run by hand due to an error in previous step
done

#fi

#if false; then

echo ============================================================================
echo "                        Decode                          "
echo ============================================================================

set -e -o pipefail

train_stage=-10
stage=0
train_set=train_$lang #Set this to the train directory in data
gmm=tri3_${lang}_ali
gmm_dir=exp/$gmm
num_threads_ubm=$train_nj

dir=exp/tdnn_f_chain_1d

ali_dir=exp/${gmm}_ali_${train_set}_sp

tree_dir=exp/tree_sp
lang_chain=data/lang_chain
lat_dir=exp/${gmm}_${train_set}_sp_lats

label_delay=0 #JB:changed to 0 to be consistent with chain BLSTM recipe in swbd
train_ivector_dir=exp/ivectors_${train_set}_sp_hires
train_data_dir=data/${train_set}_sp_hires
lores_train_data_dir=data/${train_set}_sp

get_egs_stage=-10

# TDNN options
frames_per_eg=150,110,100
remove_egs=true
common_egs_dir=
xent_regularize=0.1
dropout_schedule='0,0@0.20,0.5@0.50,0'

#if false; then
#------------------------------------------------------------------
# ivector extraction
#------------------------------------------------------------------
test_sets="harvest_$lang" #directory names in data dir

for datadir in ${test_sets}; do
    utils/copy_data_dir.sh data/$datadir data/${datadir}_hires
  done

  for datadir in ${test_sets}; do
    steps/make_mfcc.sh --nj $train_nj --mfcc-config conf/mfcc_hires.conf \
      --cmd "$train_cmd" data/${datadir}_hires
    steps/compute_cmvn_stats.sh data/${datadir}_hires
    utils/fix_data_dir.sh data/${datadir}_hires
  done
  
#ivectors

for data in ${test_sets}; do
    nspk=$(wc -l < data/${data}_hires/spk2utt)
    steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj "${nspk}" \
      data/${data}_hires exp/extractor \
      exp/ivectors_${data}_hires
  done

#fi


#------------------------------------------------------------------
# decode
#------------------------------------------------------------------

graph_dir=$dir/$gf_dir
frames_per_chunk=$(echo $chunk_width | cut -d, -f1)
           
data=harvest_$lang

#if false; then

steps/nnet3/decode.sh \
           --acwt 1.0 --post-decode-acwt 10.0 \
           --nj $decode_nj --cmd "$decode_cmd" --num-threads 4 \
           --online-ivector-dir exp/ivectors_${data}_hires \
           $graph_dir data/${data}_hires $dir/decode_harvest_${lang}_${gf_dir} || exit 1


echo ============================================================================
echo "     Get decode phone string from tra file & prep for tri3 align           "
echo ============================================================================

#fi

words_file=$graph_dir/words.txt
data=harvest_$lang

utils/int2sym.pl -f 2- $words_file $dir/decode_harvest_${lang}_${gf_dir}/scoring/$scoring_weight.tra > $dir/decode_harvest_${lang}_${gf_dir}/scoring/$scoring_weight.tra.txt

#Replace empty text in data dir with decode .tra

cat $dir/decode_harvest_${lang}_${gf_dir}/scoring/$scoring_weight.tra.txt > data/$data/text


echo ============================================================================
echo "                        Generate tri3 alignments                          "
echo ============================================================================

data=harvest_$lang

#retry_beam=160
beam=160
retry_beam=3500

steps/align_fmllr.sh --nj "$decode_nj" --cmd "$train_cmd" --beam $beam --retry-beam $retry_beam data/harvest_${lang} data/lang_${main_lang} exp/tri3_${main_lang} $dir/decode_harvest_${lang}_${gf_dir}/tri3_${lang}_ali_harvest_decode_text_big_beam


in_ali=$dir/decode_harvest_${lang}_${gf_dir}/tri3_${lang}_ali_harvest_decode_text_big_beam
mdl_file=$in_ali/final.mdl
graph_dir=$dir/$gf_dir
phones_file=$graph_dir/phones.txt
out_ctm=$dir/decode_harvest_${lang}_${gf_dir}/decode_harvest_${lang}_${gf_dir}_tri3_aligned_big_beam.ctm

ali-to-phones --ctm-output $mdl_file "ark:gunzip -c $in_ali/ali.*.gz |" - | utils/int2sym.pl -f 5 $phones_file > $out_ctm;

#fi
