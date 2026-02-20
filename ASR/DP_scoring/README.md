This directory contains a script, score_tras.py, which scores two tra files according to the phones (or labels) in each entry. Mismatched entries are ignored, and a warning is written to standard out.

The tra files should each have the following format:

```
<key> <label1> <label2> ...
```

Where <key> is the name of an entry (the segment identifier for example), and <label1>, <label2> etc are the labels.

To use the script:

```sh
python3 score_tras.py <tra_file_1> <tra_file_2> > <output_file>
```

Output is written to standard out, and can be redirected as in the example above.

