import os
import sys


try:
	text = sys.argv[1]
	lm = sys.argv[2]
except:
	print '%s text lm' % sys.argv[0]
	sys.exit(1)


f = open(text, 'r')
data = f.read()
f.close()

data = data.replace('\n',' ')
words = data.split()

words = dict(zip(words, words))
words = words.keys()
words.sort()

import math

prob = math.log10(1.0 / float(len(words)))
f = open(lm, 'w')
f.write('\n\\data\\\nngram 1=%d\n\n\\1-grams:\n' % len(words))
out = ['%.5f\t%s\n' % (prob, wrd) for wrd in words]
f.write(''.join(out))
f.write('\n\\end\\\n')
f.close()

