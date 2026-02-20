This directory contains a collection of tools for the data harvesting procedure for raw broadcast recordings.

Broadly, the steps of the audio harvesting procedure are as follows:

1. Obtain raw recordings.
2. Perform forced alignment on recordings using a Kaldi1 baseline model.
3. Split recordings according to silence markers obtained in step 2.
4. Perform word recognition of recordings split up in step 3.
5. Filter final segments by performing PDP scoring of the phone labels of segments from step 3 with the phone labels from segments from step 4. Use a dictionary to lookup the phone labels for each word recognised for segments in step 4.

