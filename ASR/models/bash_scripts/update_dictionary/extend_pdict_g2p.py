# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Predict pronunciations using G2P for tokens not in original pdict.
"""

__author__     = "Jaco Badenhorst"
__version__    = "0.1"
__email__      = "jbadenhorst@csir.co.za"

import sys
import os
import codecs
import string
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

    include_all_dict_tokens = True #include the whole existing dict for now

    dict_tokens = []
    dict_pronuns = []
    existing_pronunciations = {}
    with codecs.open(main_dict, "r", "utf-8") as dict_handle:
        for line in dict_handle:
            line_parts = line.split()
            dict_token = line_parts[0]
            dict_tokens.append(dict_token)
            dict_pronuns.append(" ".join(line_parts[1:]))
            if include_all_dict_tokens:
                existing_pronunciations[dict_token] = " ".join(line_parts[1:])

    oov_tokens = []
    for token in tokens:
        if token not in dict_tokens and len(token) > 0:
            # len(words) > 0, Don't add empty string
            oov_tokens.append(token)
        else:
            # already in dict
            token_index = dict_tokens.index(token)
            existing_pronunciations[token] = dict_pronuns[token_index]

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

    print("OOV words:\n------------")
    print(oov_words)

    #oov_words.sort()
    #print "oov_words: "
    #for ow in oov_words: #JB
    #    print(ow)

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

if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    
    parser.add_option("-T", action="store", type="string", dest="word_txt", help="Input word text file")
    parser.add_option("-D", action="store", type="string", dest="pdict", help="Input pdict")
    parser.add_option("-R", action="store", type="string", dest="rules", help="Input g2p rules file")
    parser.add_option("-N", action="store", type="string", dest="gnulls", help="Input g2p gnulls file")
    parser.add_option("-G", action="store", type="string", dest="graph_map", help="Input g2p grapheme map file")
    parser.add_option("-P", action="store", type="string", dest="phone_map", help="Input g2p phone map file")
    parser.add_option("-M", action="store", type="string", dest="dict_map", help="Input dictionary phone map file (convert phone labels)")
    parser.add_option("-o", action="store", type="string", dest="new_pdict", help="Output extended pdict file")
    parser.add_option("-s", action="store", type="string", dest="swap_ph_map", help="Output phone map file with columns swapped")
    
    options, args = parser.parse_args()
    
    extendDict(options.word_txt, options.pdict, options.rules, options.gnulls, options.graph_map, options.phone_map, options.dict_map, options.new_pdict, options.swap_ph_map)
