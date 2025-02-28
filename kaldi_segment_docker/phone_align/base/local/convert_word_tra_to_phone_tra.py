# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Convert a word level .tra to a phone level .tra given a pronunciation dictionary

"""

__author__     = "Jaco Badenhorst"
__version__    = "0.1"
__email__      = "jbadenhorst@csir.co.za"

import sys
import os
import codecs
import string
import json
from optparse import OptionParser

def readDict(pdict):

    dict_words = {}
    dict_handle = codecs.open(pdict, "r", "utf-8")
    for line in dict_handle:
        line_parts = line.strip("\n").split()
        dict_token = line_parts[0]
        pronun = line_parts[1:]
        if dict_token not in dict_words: #Just use first variant
            dict_words[dict_token] = pronun
    dict_handle.close()
    
    return dict_words

def convert(tra_in, pdict, tra_out):
    """
    """
    
    dict_words = readDict(pdict)
    
    tra_handle = codecs.open(tra_in, "r", "utf-8")
    tra_handle_out = codecs.open(tra_out, "w", "utf-8")
    
    for line in tra_handle:
        line_parts = line.strip("\n").split()
        trans_words = line_parts[1:]
        
        utt_ph_list = []
        for trans_word in trans_words:
            utt_ph_list.extend(dict_words[trans_word])
        utt_ph_str = " ".join(utt_ph_list)
        
        #Add start and ending silence
        utt_ph_str = " ".join(["sil", utt_ph_str,"sil\n"])
        
        tra_handle_out.write(" ".join([line_parts[0],utt_ph_str]))
    tra_handle.close()
    tra_handle_out.close()
    

if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    parser.add_option("-T", action="store", type="string", dest="tra_in", help="Input .tra file")
    parser.add_option("-D", action="store", type="string", dest="pdict", help="Input pdict")
    parser.add_option("-o", action="store", type="string", dest="tra_out", help="Output .tra file")

    options, args = parser.parse_args()

    convert(options.tra_in, options.pdict, options.tra_out)
