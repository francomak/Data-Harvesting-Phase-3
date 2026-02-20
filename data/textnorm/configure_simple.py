#!/usr/bin/python3

import sys, os

makefile_template = """
all: ${base}_noblank_expanded_lower_norm.phon

${base}_noblank.txt: ${base}.txt
	echo stripping blank lines
	${dir}/strip_blank_lines.py ${base}.txt > ${base}_noblank.txt

${base}_noblank_expanded.txt: ${base}_noblank.txt
	echo expanding
	${dir}/expand_acronyms.py ${base}_noblank.txt > ${base}_noblank_expanded.txt

${base}_noblank_expanded_lower.txt: ${base}_noblank_expanded.txt
	echo lower case
	${dir}/lowercase.py ${base}_noblank_expanded.txt > ${base}_noblank_expanded_lower.txt

${base}_noblank_expanded_lower_norm.txt: ${base}_noblank_expanded_lower.txt
	echo cleaning words
	${dir}/clean_words.py ${base}_noblank_expanded_lower.txt > ${base}_noblank_expanded_lower_norm.txt
	${dir}/text2words.py ${base}_noblank_expanded_lower_norm.txt > ${base}_sorted.words

empty.map:
	echo making empty map
	touch empty.map

${base}.dict: ${base}_noblank_expanded_lower_norm.txt empty.map
	echo building dictionary
	python ${dir}/extend_pdict/extend_pdict_g2p.py -T ${base}_sorted.words -D ${dir}/${lang}/nchlt_${lang}.dict -R ${dir}/${lang}/rules/nchlt_${lang}.rules -N ${dir}/${lang}/rules/nchlt_${lang}.gnulls -G ${dir}/${lang}/rules/nchlt_${lang}.map.graphs -P ${dir}/${lang}/rules/nchlt_${lang}.map.phones -M empty.map -o ${base}.dict

${base}_noblank_expanded_lower_norm.phon: ${base}.dict
	echo converting to phones
	python ${dir}/map_words_text_to_phones.py -P ${base}_noblank_expanded_lower_norm.txt -D ${base}.dict -o ${base}_noblank_expanded_lower_norm.phon
"""

def de_ext(path):
   return ".".join(path.split(".")[0:-1])

if len(sys.argv) < 3:
   print("Usage: %s <filename> <lang>"%(sys.argv[0]), file=sys.stderr)
   sys.exit(1)

lang = sys.argv[2]
result = makefile_template.replace("${base}", "%s"%(de_ext(sys.argv[1])))
result = result.replace("${dir}", "%s"%(os.path.dirname(sys.argv[0])))
result = result.replace("${lang}", lang)
f = open("Makefile", 'w')
f.write(result+"\n")
f.close()

