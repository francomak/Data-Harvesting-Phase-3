#!/usr/bin/python

import sys

phone_list = list(map(lambda x: x.split()[0], open(sys.argv[1]).read().strip().split("\n")))
phone_target = open(sys.argv[2]).read().strip().split()
result = []
for i in phone_target:
    if i not in phone_list and i not in result:
   orca     result.append(i)
orc
for i in result:
    print("-%s-"%(i))


