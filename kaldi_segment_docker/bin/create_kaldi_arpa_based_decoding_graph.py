#!/usr/bin/env python

"""
Create decoding graphs based on ARPA and acoustic models given a Kaldi installation.
"""

__author__     = "Jaco Badenhorst"
__version__    = "0.1"
__email__      = "jbadenhorst@csir.co.za"

import sys
import os
import codecs
import string
from optparse import OptionParser
import shutil

from prep_kaldi import GetGraph


       
def create_working_dirs(out_dir, conf_prep_dirs):
    """
    Set up output location for recognition files
    """
        
    #Clean and create required output directories
    main_output = out_dir
    if os.path.exists(main_output):
        shutil.rmtree(main_output)
    os.mkdir(main_output)
    for dirname in conf_prep_dirs:
        if dirname != "MAIN_DIR":
            os.mkdir(os.path.join(main_output, conf_prep_dirs[dirname]))
            
            
def createGraph(arpa_in, model_in_dir, utils_dir, dict_file, out_dir):
    """
    """
    
    os.system(". ./path.sh")
    
    prep_kaldi_dirs_conf = {
            "DICT_DIR":"kaldi_dict",
            "GRAM_DIR":"kaldi_gram",
            "LANG_DIR":"kaldi_lang",
            "GRAPH_DIR":"kaldi_graph",
            "TMP_DIR":"kaldi_tmp",
            "UTT_DATA_DIR":"kaldi_data"
            }
    
    create_working_dirs(out_dir, prep_kaldi_dirs_conf)
           
    prep_kaldi_conf = {
                "MAIN_DIR" : out_dir,
                "UTILS": utils_dir,
                "MODEL_DIR": model_in_dir,
                "DICT": dict_file,
                "LM": arpa_in,
                "DICT_OUT": "lexicon.txt",
                "NO_SIL_PHS": "nonsilence_phones.txt",
                "SIL_PHS": "silence_phones.txt",
                "OPT_SIL_PHS": "optional_silence.txt",
                "EXTRA_QUES": "extra_questions.txt",
                "FSM": "grammar.fsm",
                "SYMTAB": "grammar.symtab",
                "MAPPED_SYMTAB": "grammar.map_symtab",
                "FST": "grammar.fst"
            }
    
    #prep_graph(config)
    prep_kaldi_conf["LM_SWITCH"] = True
    prep_kaldi_conf.update(prep_kaldi_dirs_conf)
    g = GetGraph(prep_kaldi_conf)
    
    
            
            
if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    
    parser.add_option("-T", action="store", type="string", dest="arpa_in", help="Input ARPA file")
    parser.add_option("-M", action="store", type="string", dest="model_in_dir", help="Input model directory - the tdnnf directory")
    parser.add_option("-U", action="store", type="string", dest="utils_dir", help="Input utils directory path")
    parser.add_option("-D", action="store", type="string", dest="dict_file", help="Input pronunciation dictionary file")
    parser.add_option("-s", action="store", type="string", dest="out_dir", help="Output directory")
    
    options, args = parser.parse_args()
    
    createGraph(options.arpa_in, options.model_in_dir, options.utils_dir, options.dict_file, options.out_dir)
