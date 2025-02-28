#!/usr/bin/python

""" Replace ticks in xho text with something unlikely to be corrupted by speect, taking context into account. """

import sys

if len(sys.argv)<2:
    sys.stderr.write("Provide file name.\n")
    sys.stderr.flush()
    sys.exit(1)
f = open(sys.argv[1])
lines = f.read().strip().split("\n")
f.close()
for line in lines:
    print(line.replace('aiaiaiai', "'"))
