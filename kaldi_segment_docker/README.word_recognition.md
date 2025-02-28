First setup an out-of-tree build directory for Kaldi using the steps discussed within the main readme within this directory.

Next, create a word recognition model using the script located at bin/make_text_graph.sh. Use it like so:

```sh
bin/make_text_graph.sh <dictionary> <language_code> <text_file>
```

Where <dictionary> is a dictionary mapping word labels to phone labels, <language_code> is the language code (eg tsn), and <text_file> is a file containing text for training the word recognition model. Dictionaries for South African languages can be found on the Sadilar repository.

Once you have your word recognition model, you may perform word recognition using the "run_text_rec.sh" script within your build directory.

```sh
./run_text_rec.sh <language> <audio directory> <audio list file>
```

Where "language" is the preconfigured language code (e.g. tsn), "audio directory" is a directory of audio files, and "audio list file" is a textfile containing a list of audio files (without extensions) that will be aligned.

