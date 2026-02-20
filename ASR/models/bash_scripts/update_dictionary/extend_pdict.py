# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Predict pronunciations using G2P for tokens not in original pronunciation dictionary. This script is based off of "extend_pdict_g2p.py" that was written by Jaco Badenhorst
"""

__author__     = "Franco Mak" # but based on the script from "Jaco Badenhorst"
__version__    = "1.0"
__email__      = "fmak@csir.co.za"

import codecs
from optparse import OptionParser
from g2p_rewrites import G2Prewrites

def lookup_dict_words(tokens, main_dict):
    """
    Lookup a list if tokens in the main dictionary and return tokens that
    are OOV.

    Args:
        tokens (list): List of tokens to lookup.

    Returns:
        tuple(list, dict): A tuple with a list of out-of-vocabulary tokens
                        and a dictionary of existing pronunciaitons.
    """

    # dict_tokens = []
    # dict_pronuns = []
    existing_pronunciations = {}
    with open(main_dict, mode="r", encoding="utf-8") as file:
        lines = file.read().split('\n')
        for line in lines:
            if len(line) > 0:
                line_parts = line.split('\t')
                dict_token = line_parts[0]
                dict_pronuns = line_parts[1]
                existing_pronunciations[dict_token] = dict_pronuns

    oov_tokens = []
    for token in tokens:
        if token not in existing_pronunciations and len(token) > 0:
            # len(words) > 0, Don't add empty string
            oov_tokens.append(token)
        # else:     # FM: not sure what this else loop does. The token in existing_pronunciations is already done inside the with loop above
            # already in dict
            # token_index = dict_tokens.index(token)
            # existing_pronunciations[token] = dict_pronuns[token_index]

    return oov_tokens, existing_pronunciations

def g2p_pronunciations(tokens, rules_path, gnulls_path, graph_map_path, phone_map_path):
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
        new_dict = {}
        for token in tokens:
            new_dict[token] = " ".join(rewrites.apply(token))

        return new_dict
    
def apply_phone_mapping(token_dict, dict_map_path):
        """
        Apply a phone mapping to the given dictionary with it's associated
        phones as a list.

        Args:
            token_dict (dict): A dictionary of tokens with their
            associated pronunciations as a list.

        Returns:
            (dict): The received dictionary with possibly replaced
                    phone strings due to the mapping.
        """

        ph_map = {}  # left to right phone map
        with codecs.open(dict_map_path, "r", "utf-8") as map_handle:
            for line in map_handle:
                line_parts = line.split()
                if len(line_parts) > 1:
                    # do not attempt to add empty lines
                    ph_map[line_parts[0]] = line_parts[1]

        for token in token_dict.keys():
            phones = token_dict[token]
            for count, phone in enumerate(phones):
                if phone in ph_map:
                    phones[count] = ph_map[phone]

        return token_dict



def create_dict(word_tokens, main_dict, rules_path, gnulls_path, graph_map_path, phone_map_path, dict_map_path):
    """
    Generate a pronunciation dictionary containing pronunciations for
    the words tokens of the grammar file.

    Args:
        word_tokens (list): A list of words.

    Returns:
        (str): Full path and file name of the final dictionary.
    """

    # 1) Do dictionary lookup
    # Words not in main dictionary
    oov_words, dictionary = lookup_dict_words(word_tokens, main_dict)

    # print("OOV words:\n------------")
    print(f'Number of oov_words is {len(oov_words)}')

    # 2) Predict the pronunciations of all words not found in primary dict
    new_dict = g2p_pronunciations(oov_words, rules_path, gnulls_path, graph_map_path, phone_map_path)

    # 3) Apply phone mapping to predicted dictionary (if required)
    new_dict_mappings = apply_phone_mapping(new_dict, dict_map_path)
    dictionary.update(new_dict_mappings)

    return dictionary

def getWordTokens(word_txt):
    """
    Given a text file (seperate lines of text) return a unique list of word tokens
    """
    
    unique_word_tokens = []
    
    trans_handle = codecs.open(word_txt, "r", "utf-8")
    for line in trans_handle:
        line_tokens = line.split()
        for ltoken in line_tokens:
            if ltoken not in unique_word_tokens:
                unique_word_tokens.append(ltoken)
    trans_handle.close()
    
    return unique_word_tokens

def extendDict(word_txt, pdict, rules_path, gnulls_path, graph_map_path, phone_map_path, dict_map_path, new_pdict, swap_ph_map):
    """
    """
    
    word_tokens = getWordTokens(word_txt)
    
    if swap_ph_map != None:
        ph_handle_out = codecs.open(swap_ph_map, "w", "utf-8")
        ph_handle = codecs.open(phone_map_path, "r", "utf-8")
        for line in ph_handle:
            line_parts = line.strip("\n").split()
            ph_handle_out.write("".join([line_parts[1],"\t",line_parts[0],"\n"]))
        ph_handle.close()
        ph_handle_out.close()
    
        final_dict = create_dict(word_tokens, pdict, rules_path, gnulls_path, graph_map_path, swap_ph_map, dict_map_path)
    else:
        final_dict = create_dict(word_tokens, pdict, rules_path, gnulls_path, graph_map_path, phone_map_path, dict_map_path)
    
    #Output dictionary
    with codecs.open(new_pdict, "w", "utf-8") as dict_handle:
        for token_item in sorted(final_dict.keys()):
            dict_handle.write(token_item)
            dict_handle.write("\t")
            dict_handle.write(final_dict[token_item])
            dict_handle.write("\n")
            if len(final_dict[token_item]) < 1:
                print("WARNING: ",token_item," ",final_dict[token_item])

def get_unique_words(text_corpus):
    """
    The original extend_pdict_g2p.py uses a textfile containing unique words/tokens. This script will take a textfile containing sentences, and generate a list of unique words
    """
    print(f"Loading sentences from {text_corpus}")

    unique_words = set()
    with open(text_corpus, encoding='utf-8') as file:
        sentences = file.read().split('\n')
        for sentence in sentences:
            if len(sentence) > 0:
                for word in sentence.split():
                    if (len(word)>1) and (word not in unique_words):
                        unique_words.add(word)

    print('Obtaining list of unique words')
    sorted_words = sorted(unique_words)
    with open('temp/unique_words.txt', mode='w', encoding='utf-8') as file:
        for word in sorted_words:
            file.write(f'{word}\n')

if __name__ == "__main__":
    # Manually adjust the three variables below:
    LANG = 'xho'
    text_corpus = f'/media/franco_linux/CSIR/Datasets/Text_corpus/{LANG}/NCHLT_Leipzig_comp.txt' # Textfile containing sentences. Will be used to first extract unique words, and then obtain g2p approximations for new words
    output_filename = f"{LANG}_nchlt_leipzig.dict"
    
    word_txt = "temp/unique_words.txt" # Input word text file
    pdict = f"base_nchlt_dicts/nchlt_{LANG}.dict" # Input pdict
    rules = f"aux_pdicts_rules/nchlt_{LANG}.rules" # Input g2p rules file
    gnulls = f"aux_pdicts_rules/nchlt_{LANG}.gnulls" # Input g2p gnulls file
    graph_map = f"aux_pdicts_rules/nchlt_{LANG}.map.graphs" # Input g2p grapheme map file
    phone_map = f"aux_pdicts_rules/nchlt_{LANG}.map.phones" # Input g2p phone map file
    dict_map = f"temp/empty.map" # Input dictionary phone map file (convert phone labels)
    new_pdict = output_filename # Output extended pdict filename
    swap_ph_map = None # If not None, outputs phone map file with columns swapped

    get_unique_words(text_corpus)
    print('Unique words obtained. Beginning g2p predictions for new words')
    extendDict(word_txt, pdict, rules, gnulls, graph_map, phone_map, dict_map, new_pdict, swap_ph_map)
    