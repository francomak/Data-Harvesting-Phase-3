#!/usr/bin/python

import sys

if len(sys.argv) < 2:
    sys.stderr.write("Provide input file\n")
    sys.stderr.flush()
    sys.exit(1)

f = open(sys.argv[1])
lines = f.read().strip().split("\n")
f.close()
for line in lines:
    word, phones = line.split("\t")
    phones = phones.replace("pS_h", "pS")
    phones = phones.replace("pS_>", "pS")
    phones = phones.replace("BZ", "b d_0Z")
    print("%s\t%s"%(word,phones))
