# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""

"""

__author__     = "Jaco Badenhorst"
__version__    = "0.1"
__email__      = "jbadenhorst@csir.co.za"

import sys
import os
import codecs
from optparse import OptionParser

def toFivephones(working_label_sequence):
    """
    """
    
    #Convert label sequence to context dependent representation
    new_labels = []
    for base_label_index in range(2,len(working_label_sequence)-2): #only convert phone labels not at ends of sequence
        new_phone_label = "".join([working_label_sequence[base_label_index-2],"-",working_label_sequence[base_label_index-1],"-",working_label_sequence[base_label_index],"+",working_label_sequence[base_label_index+1],"+",working_label_sequence[base_label_index+2]])
        new_labels.append(new_phone_label)
        
    return new_labels

def toFourphones(working_label_sequence):
    """
    Left context: -
    Right context: +
    Use left context only
    """
    
    #Convert label sequence to context dependent representation
    new_labels = []
    for base_label_index in range(2,len(working_label_sequence)-1): #only convert phone labels not at ends of sequence
        new_phone_label = "".join([working_label_sequence[base_label_index-2],"-",working_label_sequence[base_label_index-1],"-",working_label_sequence[base_label_index],"+",working_label_sequence[base_label_index+1]])
        new_labels.append(new_phone_label)
        
    return new_labels

def toTriphones(working_label_sequence):
    """
    """
    
    #Convert label sequence to context dependent representation
    new_labels = []
    for base_label_index in range(1,len(working_label_sequence)-1): #only convert phone labels not at ends of sequence
        new_phone_label = "".join([working_label_sequence[base_label_index-1],"-",working_label_sequence[base_label_index],"+",working_label_sequence[base_label_index+1]])
        new_labels.append(new_phone_label)
        
    return new_labels

def toBiphones(working_label_sequence):
    """
    Left context: -
    Right context: +
    Use left context only
    """
    
    #Convert label sequence to context dependent representation
    new_labels = []
    for base_label_index in range(1,len(working_label_sequence)): #only convert phone labels not at ends of sequence
        new_phone_label = "".join([working_label_sequence[base_label_index-1],"-",working_label_sequence[base_label_index]])
        new_labels.append(new_phone_label)
        
    return new_labels
            

def getNPhones(in_txt, out_dir):
    """
    """
    
    monophone_counts = {}
    biphone_counts = {}
    triphone_counts = {}
    fourphone_counts = {}
    fivephone_counts = {}
    
    in_handle = codecs.open(in_txt, "r", "utf-8")
    out_bi_handle = codecs.open(os.path.join(out_dir,"biphones.txt"), "w", "utf-8")
    out_tri_handle = codecs.open(os.path.join(out_dir,"triphones.txt"), "w", "utf-8")
    out_four_handle = codecs.open(os.path.join(out_dir,"fourphones.txt"), "w", "utf-8")
    out_five_handle = codecs.open(os.path.join(out_dir,"fivephones.txt"), "w", "utf-8")
    for line in in_handle:
        monophone_sequence = line.strip("\n").split()
        biphone_sequence = toBiphones(monophone_sequence)
        triphone_sequence = toTriphones(monophone_sequence)
        fourphone_sequence = toFourphones(monophone_sequence)
        fivephone_sequence = toFivephones(monophone_sequence)
        
        out_line_bi = "".join([" ".join(biphone_sequence),"\n"])
        out_bi_handle.write(out_line_bi)
        out_line_tri = "".join([" ".join(triphone_sequence),"\n"])
        out_tri_handle.write(out_line_tri)
        out_line_four = "".join([" ".join(fourphone_sequence),"\n"])
        out_four_handle.write(out_line_four)
        out_line_five = "".join([" ".join(fivephone_sequence),"\n"])
        out_five_handle.write(out_line_five)
        
        #update counts
        for plabel in monophone_sequence:
            if plabel not in monophone_counts: #new label
                monophone_counts[plabel] = 0
            monophone_counts[plabel] += 1
        
        for plabel in biphone_sequence:
            if plabel not in biphone_counts: #new label
                biphone_counts[plabel] = 0
            biphone_counts[plabel] += 1
            
        for plabel in triphone_sequence:
            if plabel not in triphone_counts: #new label
                triphone_counts[plabel] = 0
            triphone_counts[plabel] += 1
            
        for plabel in fourphone_sequence:
            if plabel not in fourphone_counts: #new label
                fourphone_counts[plabel] = 0
            fourphone_counts[plabel] += 1
            
        for plabel in fivephone_sequence:
            if plabel not in fivephone_counts: #new label
                fivephone_counts[plabel] = 0
            fivephone_counts[plabel] += 1
    
    in_handle.close()
    out_bi_handle.close()
    out_tri_handle.close()
    out_four_handle.close()
    out_five_handle.close()
    
    biphone_labels = biphone_counts.keys()
    biphone_labels.sort(key=lambda x:x[1],reverse=False)

    
    #Report on number of unqiue phone labes
    print("Unique phone counts:\n------------------------------")
    print("Monophones: ",len(monophone_counts.keys()))
    print("Biphones: ",len(biphone_counts.keys()))
    print("Triphones: ",len(triphone_counts.keys()))
    print("4-phones: ",len(fourphone_counts.keys()))
    print("5-phones: ",len(fivephone_counts.keys()))
    
    #Output phone counts
    out_mono_handle = codecs.open(os.path.join(out_dir,"monophone_counts.txt"), "w", "utf-8")
    sort_monophone_counts = sorted(monophone_counts.items(), key=lambda x: x[1], reverse=True)
    for i in sort_monophone_counts:
        out_mono_handle.write("".join([i[0]," : ",str(i[1]),"\n"]))
    out_mono_handle.close()
    
    out_bi_handle = codecs.open(os.path.join(out_dir,"biphone_counts.txt"), "w", "utf-8")
    sort_biphone_counts = sorted(biphone_counts.items(), key=lambda x: x[1], reverse=True)
    for i in sort_biphone_counts:
        out_bi_handle.write("".join([i[0]," : ",str(i[1]),"\n"]))
    out_bi_handle.close()
        
    out_tri_handle = codecs.open(os.path.join(out_dir,"triphone_counts.txt"), "w", "utf-8")
    sort_triphone_counts = sorted(triphone_counts.items(), key=lambda x: x[1], reverse=True)
    for i in sort_triphone_counts:
        out_tri_handle.write("".join([i[0]," : ",str(i[1]),"\n"]))
    out_tri_handle.close()
    
    out_four_handle = codecs.open(os.path.join(out_dir,"fourphone_counts.txt"), "w", "utf-8")
    sort_fourphone_counts = sorted(fourphone_counts.items(), key=lambda x: x[1], reverse=True)
    for i in sort_fourphone_counts:
        out_four_handle.write("".join([i[0]," : ",str(i[1]),"\n"]))
    out_four_handle.close()
    
    out_five_handle = codecs.open(os.path.join(out_dir,"fivephone_counts.txt"), "w", "utf-8")
    sort_fivephone_counts = sorted(fivephone_counts.items(), key=lambda x: x[1], reverse=True)
    for i in sort_fivephone_counts:
        out_five_handle.write("".join([i[0]," : ",str(i[1]),"\n"]))
    out_five_handle.close()

    return (len(monophone_counts.keys()), len(biphone_counts.keys()), len(triphone_counts.keys()), len(fourphone_counts.keys()), len(fivephone_counts.keys()))

