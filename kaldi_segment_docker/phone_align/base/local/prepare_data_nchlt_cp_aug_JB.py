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

def createTxtScpold(list_file, trans_dir, out_dir):
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
    
def createWavScpold(list_file, audio_dir, out_dir):
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
        spk_dir = fname.split("_")[2][:-1]
        out_line = " ".join([fname, "sox", os.path.join(audio_dir, spk_dir, ".".join([fname,"wav"])) ,"-t","wav","-r","16000","-","|"])
        file_handle.write("".join([out_line,"\n"]))
    file_handle.close()

def readListFile(list_file):
    """
    """
    
    fnames = []
    file_handle = codecs.open(list_file, "r", "utf-8")
    for line in file_handle:
        fnames.append(line.split()[0])
    file_handle.close()
    
    fnames.sort()
    
    return fnames

def createTxtScp(train_list_nchlt, train_list_aux, trans_dir_nchlt, trans_dir_aux, out_dir):
    """
    """
    
    fnames_nchlt = readListFile(train_list_nchlt)
    fnames_aux = readListFile(train_list_aux)
    
    file_handle = codecs.open(os.path.join(out_dir,"txt.scp"), "w", "utf-8")
    for fname in fnames_nchlt:
        out_line = " ".join([fname, os.path.join(trans_dir_nchlt,".".join([fname,"txt"]))])
        file_handle.write("".join([out_line,"\n"]))
    for fname in fnames_aux:
        out_line = " ".join([fname, os.path.join(trans_dir_aux,".".join([fname,"txt"]))])
        file_handle.write("".join([out_line,"\n"]))
    file_handle.close()
    
def createWavScp(train_list_nchlt, train_list_aux, audio_dir_nchlt, audio_dir_aux, out_dir):
    """
    """
    
    fnames_nchlt = readListFile(train_list_nchlt)
    fnames_aux = readListFile(train_list_aux)
    
    file_handle = codecs.open(os.path.join(out_dir,"wav_scp.txt"), "w", "utf-8")
    for fname in fnames_nchlt:
        spk_dir = fname.split("_")[2][:-1]
        out_line = " ".join([fname, "sox", os.path.join(audio_dir_nchlt, spk_dir, ".".join([fname,"wav"])) ,"-t","wav","-r","16000","-","|"])
        file_handle.write("".join([out_line,"\n"]))
   
    for fname in fnames_aux:
        spk_dir = fname.split("_")[2][:-1]
        spk_dir_path = fname.split("_")[2]
        out_line = " ".join([fname, "sox", os.path.join(audio_dir_aux, spk_dir_path, ".".join([fname,"wav"])) ,"-t","wav","-r","16000","-","|"])
        file_handle.write("".join([out_line,"\n"]))
        
    file_handle.close()
    
    #Sort newly created wav.scp file
    cmd_string = " ".join(["sort -t=",os.path.join(out_dir,"wav_scp.txt"),">",os.path.join(out_dir,"wav.scp")])
    os.system(cmd_string)
    #sort -t= data/train_afr/wav.scp > data/train_afr/wav.scp.sorted
    

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
        trans_file_handle.close()
        out_line = " ".join([fname, trans])
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
    TODO: Sort wav.scp first
    """
    
    file_handle = codecs.open(os.path.join(out_dir, "wav.scp"), "r", "utf-8")
    id_file_handle = codecs.open(os.path.join(out_dir, "utt2spk"), "w", "utf-8")
    for line in file_handle:
        fname_tag = line.split()[0]
        spk_tag = fname_tag.split("_")[2]
        id_file_handle.write(" ".join([fname_tag, spk_tag, "\n"]))
    file_handle.close()
    id_file_handle.close()
    
    cmd_string = " ".join(["cat", os.path.join(out_dir,"utt2spk"), "|", "utils/utt2spk_to_spk2utt.pl", ">", os.path.join(out_dir,"spk2utt"), "||", "exit 1;"])
    os.system(cmd_string)
    
def prepareData(audio_dir_nchlt, audio_dir_cp, trans_dir_nchlt, trans_dir_cp, lang, list_dir):
    """
    """
    #list_dir = "SABN_selected_datasets/final_input_lists/"
    
    #Create train data directory
    train_dir = os.path.join("data", "_".join(["train",lang]))
    os.makedirs(train_dir)
    train_list_nchlt = os.path.join(list_dir, "".join(["nchlt_",lang,".trn.lst"]))
    
    train_list_aux = os.path.join(list_dir, "".join(["cp1_plus_cp2_afr_utt_score_flat_mat_ordered_10737_selection_point85_dp_first_column_no_testset_no_devset_spks.txt"]))
    
    createTxtScp(train_list_nchlt, train_list_aux, trans_dir_nchlt, trans_dir_cp, train_dir)
    createWavScp(train_list_nchlt, train_list_aux, audio_dir_nchlt, audio_dir_cp, train_dir)
    createReco(train_dir)
    createUttIds(train_dir)
    createSpkMaps(train_dir)
    
    #Create test data directory
    test_dir = os.path.join("data", "_".join(["test",lang]))
    os.makedirs(test_dir)
    test_list = os.path.join(list_dir, "nchlt_afr.tst.lst")
    createTxtScpold(test_list, trans_dir_nchlt, test_dir)
    createWavScpold(test_list, audio_dir_nchlt, test_dir)
    createReco(test_dir)
    createUttIds(test_dir)
    createSpkMaps(test_dir)
    
    #Create dev data directory
    dev_dir = os.path.join("data", "_".join(["dev",lang]))
    os.makedirs(dev_dir)
    dev_list = os.path.join(list_dir, "nchlt_afr.dev.lst")
    createTxtScpold(dev_list, trans_dir_nchlt, dev_dir)
    createWavScpold(dev_list, audio_dir_nchlt, dev_dir)
    createReco(dev_dir)
    createUttIds(dev_dir)
    createSpkMaps(dev_dir)
    
    #Create text files
    
    createTxt(train_dir)
    createTxt(test_dir)
    createTxt(dev_dir)
    
    #Check that data directory is okay
    cmd_string = " ".join(["utils/validate_data_dir.sh --no-feats", train_dir,"|| exit 1"])
    os.system(cmd_string)
    cmd_string = " ".join(["utils/validate_data_dir.sh --no-feats", test_dir,"|| exit 1"])
    os.system(cmd_string)
    cmd_string = " ".join(["utils/validate_data_dir.sh --no-feats", dev_dir,"|| exit 1"])
    os.system(cmd_string)
    

if __name__ == "__main__":


    #Add possible arguments
    parser = OptionParser()
    
    parser.add_option("-A", action="store", type="string", dest="audio_dir_nchlt", help="Input database location")
    parser.add_option("-B", action="store", type="string", dest="audio_dir_cp", help="Input database location")
    parser.add_option("-T", action="store", type="string", dest="trans_dir_nchlt", help="Input directory location containing all proprocessed transcriptions")
    parser.add_option("-R", action="store", type="string", dest="trans_dir_cp", help="Input directory location containing all proprocessed transcriptions")
    parser.add_option("-L", action="store", type="string", dest="language", help="Input language location")
    parser.add_option("-S", action="store", type="string", dest="list_dir", help="Input list directory location")
    options, args = parser.parse_args()
    
    prepareData(options.audio_dir_nchlt, options.audio_dir_cp, options.trans_dir_nchlt, options.trans_dir_cp, options.language, options.list_dir)
