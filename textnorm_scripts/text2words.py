#!/usr/bin/python3

import sys

f = open(sys.argv[1])
words = f.read().strip().split()
f.close()

word_dict = {}
for word in words:
	word_dict[word]=True


word_list = list(word_dict.keys())
word_list.sort()
for word in word_list:
	print(word)


