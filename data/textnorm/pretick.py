#!/usr/bin/python

""" Replace ticks in xho text with something unlikely to be corrupted by speect, taking context into account. """

import sys

def pretick(line):
    if "aiaiaiai" in line:
        sys.stderr.write("Error replacing! Text contains replacement!\n")
        sys.stderr.flush()
        sys.exit(2)
    ret = ""
    ticks = "'’"
    for i in range(0,len(line)): 
        if i==0 or line[i] not in ticks:
            ret+=line[i]
        else:
            if line[i-1].isalpha():
                ret+='aiaiaiai'
            else:
                ret+=line[i]
    return ret

if len(sys.argv)<2:
    sys.stderr.write("Provide file name.\n")
    sys.stderr.flush()
    sys.exit(1)
f = open(sys.argv[1])
lines = f.read().strip().split("\n")
f.close()
for line in lines:
    print(pretick(line))
