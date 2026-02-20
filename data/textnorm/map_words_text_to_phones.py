# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Create phone level transcriptions via dictionary lookup
"""

__author__     = "Jaco Badenhorst"
__version__    = "0.1"
__email__      = "jbadenhorst@csir.co.za"

import sys
import os
import codecs
import string
from optparse import OptionParser 

def readDict(pdict):

    dict_words = {}
    dict_handle = codecs.open(pdict, "r", "utf-8")
    for line in dict_handle:
        line_parts = line.strip("\n").split()
        dict_token = line_parts[0]
        pronun = line_parts[1:]
        if len(pronun) < 1:
            print("ERROR: No pronunciation for: ",dict_token)
        if dict_token not in dict_words: #Just use first variant
            dict_words[dict_token] = pronun
            
        if len(dict_token) < 2: #spelled out
            print(line)
    dict_handle.close()
    
    return dict_words

def getPhTrans(word_txt, pdict, ph_txt):
    """
    """
    
    dict_words = readDict(pdict)
    
    trans_handle = codecs.open(word_txt, "r", "utf-8")
    ph_trans_handle = codecs.open(ph_txt, "w", "utf-8")
    
    for line in trans_handle:
        trans_words = line.split()
        
        utt_ph_list = []
        for trans_word in range(0,len(trans_words)):
            utt_ph_list.extend(dict_words[trans_words[trans_word]])
            utt_ph_str = " ".join(utt_ph_list)
            
        #Add start and ending silence
        utt_ph_str = " ".join(["sil", utt_ph_str,"sil\n"])
        
        ph_trans_handle.write(utt_ph_str)
    
    ph_trans_handle.close()
    trans_handle.close()
        

if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    
    parser.add_option("-P", action="store", type="string", dest="word_txt", help="Input word text file")
    parser.add_option("-D", action="store", type="string", dest="pdict", help="Input pdict")
    parser.add_option("-o", action="store", type="string", dest="ph_txt", help="Output phone string file")
    
    options, args = parser.parse_args()
    
    getPhTrans(options.word_txt, options.pdict, options.ph_txt)
