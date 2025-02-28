## Description
This directory contains the scripts required to train a Conformer CTC 2 model from the Kaldi 2 Icefall repository, and modified to support a custom dataset instead of the default LibriSpeech dataset.

## Installation
The programming environment used for ASR model training consisted of the following:
1. Python 3.11 through the Anaconda Python distribution
2. CUDA 12.1 and CuDNN 9.0.0
3. Linux (Tested on Ubuntu 22.04)

See the K2 and Icefall Github repositories for updated installation instructions. Steps below are installation instructions that was used to setup the Python virtual environment:
1. Install CUDA 12.1 (because K2 had a pre-compiled wheel that uses CUDA 12.1)
```
wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda_12.1.1_530.30.02_linux.run
sudo sh cuda_12.1.1_530.30.02_linux.run         (in the GUI, un-select the option to install an older driver version. Just install the toolkit)
```

2. Install CuDNN version 9.0.0
```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cudnn-cuda-12
```

3. Create a virtual environment containing Python 3.11, and install packages
```
conda create -n kaldi2 python=3.11
conda activate kaldi2
pip install torch torchvision torchaudio (version was torch-2.2.1-cp311-cp311-manylinux1_x86_64.whl) (after installation, torch version was 2.2.1+cu121)
pip install k2==1.24.4.dev20240301+cuda12.1.torch2.2.1 -f https://k2-fsa.github.io/k2/cuda.html
pip install git+https://github.com/lhotse-speech/lhotse
pip install tensorflow[and-cuda]==2.16.1
pip install ffmpeg pandas matplotlib
```

4. Clone the Icefall Git repository, and install the packages inside the “requirements.txt” file found in the main directory of icefall
```
git clone https://github.com/k2-fsa/icefall 
cd icefall
pip install -r requirements.txt
```

5. Add the path where Icefall repository was downloaded at the bottom of “.bashrc”
```
export PYTHONPATH=/full/path/to/icefall:$PYTHONPATH
```

## Usage
To train a new model:
1. If new language, create a new language folder with the iso code as foldername, and create the following inside of it:
    a) Create a "data" folder containing lang_phone and lm folders inside
    b) Create an "exp" folder where epochs will be stored.

2. Inside the folder "conformer_ctc2/configs/", create (or duplicate) a config.yaml file with appropriate parameters

3. Open the main configuration file located at "conformer_ctc2/main_config.yaml", and update the "config_filename" field to the correct config file to use for the experiment. All scripts will pull from the config file specified in this field.

4. Open a bash console and activate the "kaldi2" virtual environment, and then run the following scripts:
```
python conformer_ctc2/Lhotse_data_preparation.py
python conformer_ctc2/train.py
python conformer_ctc2/get_results.py
```
