#module load chpc/cuda/11.2/PCIe
#module load chpc/av/kaldi/2022.4
source $KALDI_ROOT/tools/config/common_path.sh
#module load chpc/cuda/11.2/PCIe/11.2


#export LD_LIBRARY_PATH=/apps/chpc/cuda/11.2/PCIe/lib64/stubs/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=${PWD}/links_to_include/:$LD_LIBRARY_PATH

export PATH=$PWD/utils/:${PWD}/links_to_include/:$PATH
#export PATH=$PWD/utils/:$PATH
