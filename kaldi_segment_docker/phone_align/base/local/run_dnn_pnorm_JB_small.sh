train_stage=-10
use_gpu=false

. cmd.sh
. ./path.sh
. utils/parse_options.sh

lang=$1
ali_dir=$2

if $use_gpu; then
  if ! cuda-compiled; then
    cat <<EOF && exit 1 
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA 
If you want to use GPUs (and have them), go to src/, and configure and make on a machine
where "nvcc" is installed.
EOF
  fi
  parallel_opts="-l gpu=1" 
  num_threads=1
  minibatch_size=512
  dir=exp/nnet5d_gpu
else
  # Use 4 nnet jobs just like run_4d_gpu.sh so the results should be
  # almost the same, but this may be a little bit slow.
  num_threads=8
  parallel_opts="-pe smp $num_threads" 
  minibatch_size=64 #JB changed to half size - will have slower learning rate
  dir=exp_nnet2/nnet_small
fi

. ./cmd.sh
. utils/parse_options.sh

#Run training
steps/nnet2/train_pnorm_fast.sh --stage $train_stage \
   --samples-per-iter 400000 \
   --parallel-opts "$parallel_opts" \
   --num-threads "$num_threads" \
   --minibatch-size "$minibatch_size" \
   --num-jobs-nnet 8  --mix-up 8000 \
   --initial-learning-rate 0.02 --final-learning-rate 0.004 \
   --num-hidden-layers 4 \
   --pnorm-input-dim 1000 --pnorm-output-dim 200 \
   --cmd "$decode_cmd" \
    data/train_${lang} data/lang_${lang} $ali_dir $dir || exit 1

