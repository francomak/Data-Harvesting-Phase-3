# Normalization Scripts

## Main Normalization Procedure

This folder contains scripts for normalizing text corpora, to be used for training ASR language models.

To configure the scripts for a specific text corpus, use the script configure_simple.py like so:

```sh
./configure_simple.py <text file> <lang>
```

Where lang is the three-letter language ISO code.

It will generate a makefile in the current directory, which can be used to execute all normalization scripts in succession:

```sh
make
```

After running make, the normalized text should be contained in a file ending in "_norm.txt", and the phonemic representation will be in a file ending in ".phon".

## Additional Preprocessing Before Normalizing

Some corpora require additional preprocessing before the main normalization procedure can be utilized. This may envolve stripping xml tags, or extracting text from TTS utterances etc. Some scripts that can be used for this include:

* dexml.py: remove XML tags from text
* strip_tts.sh: Remove text from utterances, as contained in TTS aligned data
* second_column.sh: Extract only the second column from a text file (i.e. numbered lines in a text file)
