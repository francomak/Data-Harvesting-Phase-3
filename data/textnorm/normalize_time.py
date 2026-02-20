#!/usr/bin/python3

""" Sot speect voice has an issue with time. This script changes values of the form 08h00 or 08:00 to 08 00. """

import sys

def convert_times(line):
    ret = ""
    for i in range(0,len(line)):
        if i>0 and i < len(line)-1 and line[i] in "Hh:" and line[i-1].isnumeric() and line[i+1].isnumeric():
            ret+=" "
        else:
            ret+=line[i]
    return ret


if len(sys.argv)<2:
    sys.stderr.write("Provide file name as argument.\n")
    sys.stderr.flush()
    sys.exit(1)
lines = []
try:
    f = open(sys.argv[1])
    lines = f.read().split("\n")
    f.close()
except:
    sys.stderr.write("Error reading file.\n")
    sys.stderr.flush()
    sys.exit(2)

for line in lines:
    print(convert_times(line))
        
