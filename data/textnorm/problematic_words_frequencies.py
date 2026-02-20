#!/usr/bin/python

import sys

def is_problematic(word):
    for i in word:
        if ord(i)>127:
            return True
    return False

if len(sys.argv)<2:
    sys.stderr.write("Provide file name as argument.\n")
    sys.stderr.flush()
    sys.exit(1)
    words = []
try:
    f = open(sys.argv[1])
    words = f.read().split()
    f.close()
except:
    sys.stderr.write("Error reading file.\n")
    sys.stderr.flush()
    sys.exit(2)

wordmap={}
for word in words:
    if is_problematic(word):
        if word in wordmap:
            wordmap[word]+=1
        else:
            wordmap[word]=1

freqwords = list(wordmap.keys())
freqwords.sort(key=lambda x: wordmap[x], reverse=True)
print("%d Words"%(len(freqwords)))
wordcount = len(words)
for word in freqwords:
    print("%s: %d, %f"%(word, wordmap[word], wordmap[word]/wordcount))
