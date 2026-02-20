#!/usr/bin/python3

import sys

def separate_word(word):
    cut1=0
    while cut1<len(word) and not word[cut1].isalpha():
        cut1+=1
    cut2=cut1
    while cut2<len(word) and word[cut2].isalpha():
        cut2+=1
    return word[0:cut1], word[cut1:cut2], word[cut2:]

def expand_acronym(word):
    prefix, letters, suffix = separate_word(word)
    # the suffix might contain letters, leave unchanged if this is the case, not an acronym
    for i in suffix:
        if i.isalpha():
            return word
    if letters.isupper():
        letters = " ".join(list(letters))
    return prefix+letters+suffix

def expand_acronyms(text):
    lines = s.strip().split("\n")
    for line in lines:
        words = line.split()
        print(" ".join(map(expand_acronym, words)))

if len(sys.argv) <2:
    sys.stderr.write("Provide file name as argument.\n")
    sys.stderr.flush()
    sys.exit(1)

try:
    f = open(sys.argv[1])
    s = f.read()
    expand_acronyms(s)
    f.close()
except:
    sys.stderr.write("Error opening file.\n")
    sys.stderr.flush()
    sys.exit(2)
