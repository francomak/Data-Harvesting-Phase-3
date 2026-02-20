#!/usr/bin/python3

import sys

f = open(sys.argv[1])
lines = f.read().strip().split("\n")
f.close()

started = False

for line in lines:
	if line.startswith("<fn>"):
		started=True
	if started and not line.startswith("<fn"):
		print(line)


