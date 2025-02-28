#!/usr/bin/python

import sys

if len(sys.argv) < 2:
    sys.stderr.write("Provide input file\n")
    sys.stderr.flush()
    sys.exit(1)

f = open(sys.argv[1])
s = f.read()
f.close()
a = s.replace("pS_h", "pS")
a = a.replace("pS_>", "pS")
sys.stdout.write(a)
sys.stdout.flush()
