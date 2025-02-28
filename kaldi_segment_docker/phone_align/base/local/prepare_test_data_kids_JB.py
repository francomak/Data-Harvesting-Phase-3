# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Script to prepare data folder for Kaldi
"""

__author__     = "Jaco Badenhorst"
__version__    = "0.1"
__email__      = "jbadenhorst@csir.co.za"

import sys
import os
import codecs
import string
from optparse import OptionParser

def createTxtScp(list_file, trans_dir, out_dir):
    """
    """
    
    fnames = []
    file_handle = codecs.open(list_file, "r", "utf-8")
    for line in file_handle:
        fnames.append(line.split()[0])
    file_handle.close()
    
    fnames.sort()
    
    file_handle = codecs.open(os.path.join(out_dir,"txt.scp"), "w", "utf-8")
    for fname in fnames:
        print fname
        out_line = " ".join([fname, os.path.join(trans_dir,".".join([fname,"txt"]))])
        file_handle.write("".join([out_line,"\n"]))
    file_handle.close()
    
def createWavScp(list_file, audio_dir, out_dir):
    """
    """
    
    fnames = []
    file_handle = codecs.open(list_file, "r", "utf-8")
    for line in file_handle:
        fnames.append(line.split()[0])
    file_handle.close()
    
    fnames.sort()
    
    
    file_handle = codecs.open(os.path.join(out_dir,"wav.scp"), "w", "utf-8")
    for fname in fnames:
        spk_dir = "_".join(fname.split("_")[:5])
        out_line = " ".join([fname, "sox", os.path.join(audio_dir, spk_dir,".".join([fname,"wav"])) ,"-t","wav","-r","16000","-","|"])
        file_handle.write("".join([out_line,"\n"]))
    file_handle.close()
    

def createTxt(in_dir):
    """
    """
    
    file_handle = codecs.open(os.path.join(in_dir,"txt.scp"), "r", "utf-8")
    out_handle = codecs.open(os.path.join(in_dir,"text_tmp"), "w", "utf-8")
    for line in file_handle:
        line_parts = line.split()
        fname = line_parts[0]
        fpath = line_parts[1]
        
        trans_file_handle = codecs.open(fpath, "r", "utf-8")
        trans = trans_file_handle.readlines()[0]
        trans = trans.strip("\n")
        trans_file_handle.close()
        out_line = " ".join([fname, trans+"\n"])
        out_handle.write(out_line)
        
    file_handle.close()
    out_handle.close()
    
    #Sort entries in text file
    cmd_line = " ".join(["cat", os.path.join(in_dir,"text_tmp"), "|","sort","-u",">",os.path.join(in_dir,"text")])
    #print cmd_line
    os.system(cmd_line)
  
def createReco(out_dir):
    """
    """
    
    file_handle = codecs.open(os.path.join(out_dir, "wav.scp"), "r", "utf-8")
    reco_file_handle = codecs.open(os.path.join(out_dir, "reco2file_and_channel"), "w", "utf-8")
    for line in file_handle:
        fname_tag = line.split()[0]
        
        reco_file_handle.write(" ".join([fname_tag, fname_tag, "A\n"]))
        
    file_handle.close()
    reco_file_handle.close()
  
def createUttIds(out_dir):
    """
    """
    
    file_handle = codecs.open(os.path.join(out_dir, "wav.scp"), "r", "utf-8")
    id_file_handle = codecs.open(os.path.join(out_dir, "uttids"), "w", "utf-8")
    for line in file_handle:
        fname_tag = line.split()[0]
        id_file_handle.write("".join([fname_tag, "\n"]))
    file_handle.close()
    id_file_handle.close()

def createSpkMaps(out_dir):
    """
    """
    
    file_handle = codecs.open(os.path.join(out_dir, "wav.scp"), "r", "utf-8")
    id_file_handle = codecs.open(os.path.join(out_dir, "utt2spk"), "w", "utf-8")
    for line in file_handle:
        fname_tag = line.split()[0]
        spk_tag = line.split("_")[2]
        #spk_tag = line[:4]
        id_file_handle.write(" ".join([fname_tag, spk_tag, "\n"]))
    file_handle.close()
    id_file_handle.close()
    
    cmd_string = " ".join(["cat", os.path.join(out_dir,"utt2spk"), "|", "utils/utt2spk_to_spk2utt.pl", ">", os.path.join(out_dir,"spk2utt"), "||", "exit 1;"])
    os.system(cmd_string)
    
def prepareData(audio_dir, trans_dir, lang, list_dir):
    """
    """
    #list_dir = "SABN_selected_datasets/final_input_lists/"
    
    
    #Create test data directory
    test_dir = os.path.join("data", "_".join(["test",lang]))
    os.makedirs(test_dir)
    test_list = os.path.join(list_dir, "test.lst")
    createTxtScp(test_list, trans_dir, test_dir)
    createWavScp(test_list, audio_dir, test_dir)
    createReco(test_dir)
    createUttIds(test_dir)
    createSpkMaps(test_dir)
    
    
    
    #Create text files
    
    
    createTxt(test_dir)
    
    
    #Check that data directory is okay
    
    cmd_string = " ".join(["utils/validate_data_dir.sh --no-feats", test_dir,"|| exit 1"])
    os.system(cmd_string)
    
    

if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    
    parser.add_option("-A", action="store", type="string", dest="audio_dir", help="Input database location")
    parser.add_option("-T", action="store", type="string", dest="trans_dir", help="Input directory location containing all proprocessed transcriptions")
    parser.add_option("-L", action="store", type="string", dest="language", help="Input language location")
    parser.add_option("-S", action="store", type="string", dest="list_dir", help="Input list directory location")
    options, args = parser.parse_args()
    
    prepareData(options.audio_dir, options.trans_dir, options.language, options.list_dir)
