#!/usr/bin/python3

import sys 
def is_word(word):
	if len(word)==1 and ord(word[0])>ord('z'):
		return False
	for ch in word:
		if not ch.isalpha() and ch!="'":
			return False
	return True

f = open(sys.argv[1])
lines = f.read().strip().split("\n")
f.close()

for line in lines:
	words = line.split()
	result = []
	for word in words:
		if is_word(word):
			result.append(word)
	print(" ".join(result))

