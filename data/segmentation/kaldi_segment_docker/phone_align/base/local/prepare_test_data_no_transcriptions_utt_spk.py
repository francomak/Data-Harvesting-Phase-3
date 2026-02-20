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
        out_line = " ".join([fname, "sox", os.path.join(audio_dir, ".".join([fname,"wav"])) ,"-t","wav","-r","16000","-","|"])
        file_handle.write("".join([out_line,"\n"]))
    file_handle.close()
    

def createTxtEmpty(in_dir):
    """
    """
    
    file_handle = codecs.open(os.path.join(in_dir,"wav.scp"), "r", "utf-8")
    out_handle = codecs.open(os.path.join(in_dir,"text_tmp"), "w", "utf-8")
    for line in file_handle:
        line_parts = line.split()
        fname_tag = line.split()[0]
        
        out_line = " ".join([fname_tag, "\n"])
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
        #spk_tag = "_".join(line.split("_")[0:4])
        spk_tag = fname_tag
        id_file_handle.write(" ".join([fname_tag, spk_tag, "\n"]))
    file_handle.close()
    id_file_handle.close()
    
    cmd_string = " ".join(["cat", os.path.join(out_dir,"utt2spk"), "|", "utils/utt2spk_to_spk2utt.pl", ">", os.path.join(out_dir,"spk2utt"), "||", "exit 1;"])
    os.system(cmd_string)
    
def prepareData(audio_dir, lang, list_file):
    """
    """
   
    #Create test data directory
    test_dir = os.path.join("data", "_".join(["harvest",lang]))
    os.makedirs(test_dir)
    test_list = list_file
    #createTxtScp(test_list, trans_dir, test_dir) #Not creating txt.scp
    createWavScp(test_list, audio_dir, test_dir)
    createReco(test_dir)
    createUttIds(test_dir)
    createSpkMaps(test_dir)
    
    createTxtEmpty(test_dir)
    
    
    #Check that data directory is okay
    
    #cmd_string = " ".join(["utils/validate_data_dir.sh --no-feats", test_dir,"|| exit 1"])
    #os.system(cmd_string)
    
    

if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    
    parser.add_option("-A", action="store", type="string", dest="audio_dir", help="Input database location")
    #parser.add_option("-T", action="store", type="string", dest="trans_dir", help="Input directory location containing all proprocessed transcriptions")
    parser.add_option("-L", action="store", type="string", dest="language", help="Input language/location/name of data set")
    parser.add_option("-S", action="store", type="string", dest="list_file", help="Input txt list of audio fnames")
    options, args = parser.parse_args()
    
    prepareData(options.audio_dir, options.language, options.list_file)
