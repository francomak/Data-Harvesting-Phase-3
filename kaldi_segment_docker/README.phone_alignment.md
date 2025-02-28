First setup an out-of-tree build directory for Kaldi 1 using the steps discussed within the main readme within this directory.

Once you have your out-of-tree directory, you may perform phone alignment using the "run_phone_rec.sh" script within your build directory.

```sh
./run_phone_rec.sh <language> <audio directory> <audio list file>
```

Where "language" is the preconfigured language code (e.g. tsn), "audio directory" is a directory of audio files, and "audio list file" is a textfile containing a list of audio files (without extensions) that will be aligned.

