#!/usr/bin/python3

import sys

if len(sys.argv)<2:
    sys.stderr.write("Provide file name as argument.\n")
    sys.stderr.flush()
    sys.exit(1)
try:
    f = open(sys.argv[1])
    s = f.read()
    f.close()
    print(s.lower())
except:
    sys.stderr.write("Error reading file.\n")
    sys.stderr.flush()
    sys.exit(2)


