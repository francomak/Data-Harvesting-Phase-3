#!/usr/bin/python

import sys

if len(sys.argv)< 3:
    sys.stderr.write("Provide at least two pdicts as input.\n")
    sys.stderr.flush()
    sys.exit(1)

pdicts = list(map(open, sys.argv[1:]))

pydicts = []
uniset = {}
for pdict in pdicts:
    pydicts.append({})
    for line in pdict.read().strip().split("\n"):
        word, phones = line.split("\t")
        pydicts[-1][word] = phones
        uniset[word]=True

words = list(uniset.keys())
words.sort()
for word in words:
    phones = ""
    for pydict in pydicts:
        try:
            if phones!=pydict[word]:
                if phones=="":
                    phones=pydict[word]
                else:
                    sys.stderr.write("%s in multiple pdicts with different phones!\n"%(word))
                    sys.stderr.flush()
        except KeyError:
            continue
    print("%s\t%s"%(word, phones))

for pdict in pdict:
    pdict.close()

