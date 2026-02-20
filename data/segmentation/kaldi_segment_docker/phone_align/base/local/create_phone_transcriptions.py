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
        if dict_token not in dict_words: #Just use first variant
            dict_words[dict_token] = pronun
    dict_handle.close()
    
    return dict_words

def getPhTrans(trans_dir, pdict, ph_trans_dir):
    """
    """
    
    dict_words = readDict(pdict)
    
    fnames = os.listdir(trans_dir)
    for fname in fnames:
        #print fname
        try:
            trans_handle = codecs.open(os.path.join(trans_dir, fname), "r", "utf-8")
            line = trans_handle.readlines()[0]
            trans_words = line.strip("\n").split()
            trans_handle.close()
        except:
            continue
        
        ph_trans_handle = codecs.open(os.path.join(ph_trans_dir, fname), "w", "utf-8")
        utt_ph_list = []
        for trans_word in trans_words:
            utt_ph_list.extend(dict_words[trans_word])
        utt_ph_str = " ".join(utt_ph_list)
            
        
        #Add start and ending silence
        utt_ph_str = " ".join(["sil", utt_ph_str,"sil\n"])
        
        ph_trans_handle.write(utt_ph_str)
        ph_trans_handle.close()
        

if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    
    parser.add_option("-P", action="store", type="string", dest="trans_dir", help="Input processed transc dir")
    parser.add_option("-D", action="store", type="string", dest="pdict", help="Input pdict")
    parser.add_option("-o", action="store", type="string", dest="ph_trans_dir", help="Output directory for phone transcriptions")
    
    options, args = parser.parse_args()
    
    getPhTrans(options.trans_dir, options.pdict, options.ph_trans_dir)
