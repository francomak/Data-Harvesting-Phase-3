#!/usr/bin/python

import sys

if len(sys.argv)<2:
    sys.stderr.write("Provide file name as argument.\n")
    sys.stderr.flush()
    sys.exit(1)
text = []
try:
    f = open(sys.argv[1])
    text = f.read()
    f.close()
except:
    sys.stderr.write("Error reading file.\n")
    sys.stderr.flush()
    sys.exit(2)

output = ""
for i in text:
    if ord(i)<128:
        output+=i
    else:
        output+=" "
print(output)
