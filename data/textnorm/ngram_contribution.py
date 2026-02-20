#!/usr/bin/python3

import sys

def calculate_ngrams(text, count):
    ngrams = {}
    tokens = text.split()
    for i in range(0, len(tokens)):
        ngram = ""
        ngram_parts = []
        for j in range(i, min(i+count, len(tokens))):
            ngram_parts.append(tokens[j])
        ngram = " ".join(ngram_parts)
        if not ngram in ngrams:
            ngrams[ngram]=1
        else:
            ngrams[ngram]+=1
    return ngrams

def compare_ngrams(ngrams1, ngrams2):
    count = 0
    for ngram in ngrams2:
        if not ngram in ngrams1:
            count+=1
    return count

if len(sys.argv)<3:
    print("Usage: %s <file1> <file2>"%(sys.argv[0]), file=sys.stderr)
    sys.exit(1)
f = open(sys.argv[1])
text1 = f.read()
f.close()
f = open(sys.argv[2])
text2 = f.read()
f.close()

for i in range(2,6):
    ngrams = (calculate_ngrams(text1,i), calculate_ngrams(text2,i))
    count = compare_ngrams(ngrams[0], ngrams[1])
    print("Contribution of ngram%d: %d, which is %f%%"%(i, count, (count/len(ngrams[1])*100.0)))
