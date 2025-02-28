# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Calculate PERs containing no sil labels
"""

__author__     = "Jaco Badenhorst"
__version__    = "0.1"
__email__      = "jbadenhorst@csir.co.za"

import sys
import os
import codecs
import string
from optparse import OptionParser

def calculateScores(tra_dir, data_dir, lang_or_graph_dir, decode_dir):
    """
    """
    
    #Convert .tra files to text label format
    
    tra_files = os.listdir(tra_dir)
    for tra_file in tra_files:
        if os.path.splitext(tra_file)[1] == ".tra":
            cmd_string = " ".join(["cat", os.path.join(tra_dir, tra_file), "|","utils/int2sym.pl -f 2-", os.path.join(lang_or_graph_dir, "words.txt"), ">", "".join([os.path.join(tra_dir, tra_file),".txt"])])
            os.system(cmd_string)
    
    #Remove sil from .tra files
    for tra_file in tra_files:
        if ".tra.txt" in tra_file and os.path.splitext(tra_file)[1] == ".txt":
            cmd_string = " ".join(["cat", os.path.join(tra_dir, tra_file), "|","sed 's/sil//g'", ">", "".join([os.path.join(tra_dir, tra_file),".sil"])])
            os.system(cmd_string)
    
    
    #Create new hyp file with no silence labels
    cmd_string = " ".join(["cat", os.path.join(tra_dir, "test_filt.txt"), "|","sed 's/sil//g'", ">", "".join([os.path.join(tra_dir, "test_filt.txt"),".sil"])])
    os.system(cmd_string)
    
    #Compute PER
    for tra_file in tra_files:
        if ".tra.txt.sil" in tra_file and os.path.splitext(tra_file)[1] == ".sil":
            
            cmd_string = " ".join(["compute-wer --text --mode=present", "".join(["ark:",os.path.join(tra_dir, tra_file)]), "".join(["ark:",os.path.join(tra_dir, "test_filt.txt"),".sil"]),"> ", os.path.join(decode_dir, "".join(["per_",tra_file.split(".tra.txt.sil")[0]]))])
            print cmd_string
            
            os.system(cmd_string)
            
            
if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    
    parser.add_option("-T", action="store", type="string", dest="tra_dir", help="Input directory containing .tra files")
    parser.add_option("-D", action="store", type="string", dest="data_dir", help="Input data dir")
    parser.add_option("-L", action="store", type="string", dest="lang_or_graph_dir", help="Input language or graph dir")
    parser.add_option("-M", action="store", type="string", dest="min_lmwt", help="Input min LMWT value")
    parser.add_option("-N", action="store", type="string", dest="max_lmwt", help="Input max LMWT value")
    parser.add_option("-d", action="store", type="string", dest="decode_dir", help="Output PERs to decode dir")
    
    
    options, args = parser.parse_args()
    
    calculateScores(options.tra_dir, options.data_dir, options.lang_or_graph_dir, options.decode_dir)