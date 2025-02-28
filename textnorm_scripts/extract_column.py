#!/usr/bin/python3

import sys

def extract_column(line):
    columns = line.split("\t")
    if len(columns)<2:
        return ""
    phrases = columns[1].split(";")
    return "\n".join(map(lambda x: x.strip(), phrases)).strip()

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
    print(extract_column(line))


