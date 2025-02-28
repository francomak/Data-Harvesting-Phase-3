# Data Harvesting Phase 3

## Description
This repository contains a collection of data harvesting tools for the creation of speech and text resources that would enable HLT development in South Africa. It covers both text and audio pre-processing steps required to create a speech corpus, and to train an ASR model. 

Broadly, the steps of the audio harvesting procedure are as follows:

1. Obtain raw recordings.
2. Perform forced alignment on recordings using a Kaldi1 baseline model.
3. Split recordings according to silence markers obtained in step 2.
4. Perform word recognition of recordings split up in step 3.
5. Filter final segments by performing PDP scoring of the phone labels of segments from step 3 with the phone labels from segments from step 4. Use a dictionary to lookup the phone labels for each word recognised for segments in step 4.

## Software components
Below is a description of the inventory of software components that have been compiled in this repository. Consult the README(s) in each directory for further information.

* "ASR_model": Contains modified Conformer CTC 2 scripts obtained from the Kaldi 2 Icefall repository. These scripts are used for data preparation of a speech dataset, as well as training and decoding an ASR model.
* "kaldi_segment_docker": Contains scripts for phone alignment, and phone and word recognition of audio using Kaldi. A dockerfile is provided containing Kaldi and other dependencies necessary for the scripts to run. 
* "scoring": Implementation of a DP algorithm to compute audio segment scores comparing two sets of phone speech label sequences. The first set is from a phone decode using an ASR model, and the second set is a word decode, followed by conversion to phonetic tokens using a pronunciation dictionary.
* "segment_on_silence": Given a .ctm file with Kaldi phone aligments create segment alignments for 5+ second segments given silences.
* "textnorm_scripts": Text normalisation functionality to remove or transform unwanted character strings such as writing out of numbers into words and deletion of non-word markups and/or document headers from the text. 
* "vosk_decode": Word recognition of input audio with word level labels using K1 models and Vosk configuration

## Authors

* Jaco Badenhorst - jbadenhorst@csir.co.za
* Franco Mak - fmak@csir.co.za
