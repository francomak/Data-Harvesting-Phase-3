'''
Summary
-------
This script will load all transcript sentences from a compilation textfile, split them into unique words, compare each word to a pronunciation dictionary, and then return a list of out-of-vocabulary (OOV) words
It will then generate G2P pronunciations for these OOV words, append them to the existing pronunciation dictionary (which will be stored as a list), sort it, and output/write the updated dictionary into a file

Input:
1. An existing pronunciation dictionary (set it in dictionary_location)
2. A single text file corpus containing potentially out of vocabulary (OOV) words. 
3. Existing g2p scripts and rule files for the required language (rules, gnulls, graph and phone map)

'''

import os
from g2p_rewrites import G2Prewrites
import codecs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--language', type=str, help='The language represented with a 3-digit iso code (e.g. zul, xho, etc.)')
parser.add_argument('--text_corpus_name', type=str, help='Path to a compilation of text corpus sentences with which to update the pronunciation dictionary')
parser.add_argument('--lexicon_output', type=str, help='Path to store the updated lexicon')
parser.add_argument('--dictionary', type=str, default=None, help='Path to existing pronunciation dictionary. Uses NCHLT by default if no dictionary is specified')
args = parser.parse_args()

lang = args.language
text_corpus = args.text_corpus_name
lexicon_output_filename = args.lexicon_output
dictionary_location = args.dictionary

### Define paths to rule files for G2P
rules_dir = "aux_pdicts_rules"
rules_path = f'{rules_dir}/nchlt_{lang}.rules'
gnulls_path = f'{rules_dir}/nchlt_{lang}.gnulls'
graph_map_path = f'{rules_dir}/nchlt_{lang}.map.graphs'
phone_map_path = f'{rules_dir}/nchlt_{lang}.map.phones'

### Loads an existing pronunciation dictionary into a list.
if  dictionary_location == None:
    dictionary_location = f'/run/media/franco_linux/CSIR/Workspace/Tasks/Data/update_dictionary/base_nchlt_dicts/nchlt_{lang}.dict'

with open(dictionary_location) as file:
    lexicon = file.read().split('\n')  
    lexicon = [x for x in lexicon if x != '']  # Remove empty strings
    existing_lexicon_words = set([x.split('\t')[0] for x in lexicon])  # Get list of unique words contained in the dictionary

### Load the sentences from the text corpus, and get a list of all unique words
all_unique_words = set()
with open(text_corpus) as file:
    contents = file.read().split('\n')
    for line in contents:
        if len(line) > 1:  # Skip empty lines
            for word in line.split(): 
                all_unique_words.add(word.lower())

### From the list of unique words, extract the oov words (those that are not found in the current pronunciation dictionary)
oov_words = []
for word in all_unique_words:
    if word not in existing_lexicon_words:
        oov_words.append(word)

### Create a function to generate the G2P pronunciations, and then parse the list of oov words to obtain predictions for each oov word
def g2p_pronunciations(tokens):
        """
        Predict the pronunciations of the given list of tokens.

        Args:
            tokens (list): A list of tokens for which the pronunciations are
                           to be predicted.
        Returns:
            (dict): Dictionary of tokens with their associated
                    pronunciations as a list.
        """

        rewrites = G2Prewrites(rules_path, gnulls_path,
                               graph_map_path, phone_map_path)

        oov_pronunciations = []
        for token in tokens:
                oov_pronunciations.append(f"{token}\t{' '.join(rewrites.apply(token))}")

        return oov_pronunciations # new_dict

oov_g2p_list = g2p_pronunciations(oov_words)

### Combine existing lexicon list with new G2P predictions
lexicon.extend(oov_g2p_list)  # Adds the content of new oov_g2p_list into existing lexicon dictionary
lexicon.sort() # Sort updated lexicon by key

with codecs.open(lexicon_output_filename, 'w', 'utf-8') as file:
    file.write('<SIL>\tSIL\n')
    file.write('!SIL\tSIL\n')
    file.write('<UNK>\tSPN\n')   ## These were added for BPE and WSASR
    file.write('<SPOKEN_NOISE>\tSPN\n')
    for line in lexicon:
        word = line.split('\t')[0]
        pronunciation = line.split('\t')[1]
        file.write(f'{word}\t{pronunciation}\n')
