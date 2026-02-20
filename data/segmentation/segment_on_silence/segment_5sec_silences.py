# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Given a .ctm file with Kaldi phone aligments create segment alignments for 5+ second segments given silences
"""

__author__     = "Jaco Badenhorst"
__version__    = "0.1"
__email__      = "jbadenhorst@csir.co.za"

import sys
import os
import codecs
from optparse import OptionParser


def getUtterancePhonesCtm(ctm_handle, line, nosil=True):
    """
    Get phone label aligments from .ctm file
    Assumption: .ctm file must be sorted so that all alignments of fname occurs in consequtive lines. 
    """
    
    fname_alignments = []
    
    line_parts = line.strip("\n").split()
    fname = line_parts[0]
    
    while fname == line_parts[0]:
        start_time = line_parts[2]
        duration = line_parts[3]
        label = line_parts[4]
        
        if nosil:
            if label != "sil":
                fname_alignments.append([fname, float(start_time), float(duration), label])
        else:
            fname_alignments.append([fname, float(start_time), float(duration), label])
    
        line = ctm_handle.readline()
        if not line: #EOF
            break
        line_parts = line.strip("\n").split()
    
    return fname_alignments, ctm_handle, line

def mergeAlignments(alignments):
    """
    Merge duplicate phone label alignments
    """
    new_alignments = []
    prev_align_item = []
    for align_item in alignments:
        if len(prev_align_item) < 1:
            prev_align_item = align_item
        elif prev_align_item[3] != align_item[3]: #new phone
            new_alignments.append(prev_align_item)
            prev_align_item = align_item
        else: #Merge
            new_dur = prev_align_item[2]+align_item[2]
            temp_item = [align_item[0], prev_align_item[1], new_dur, align_item[3]]
            prev_align_item = temp_item
            
    new_alignments.append(prev_align_item)
    
    return new_alignments


def manageSegmenter(in_ctm_file, out_seg_align_file):
    """
    """
    
    min_sil_segment_duration = 0.1 #seconds - silence have to be at least this long
    min_segment_duration = 4.5
    
    prev_best_line = ""
    best_handle = codecs.open(in_ctm_file, "r", "utf-8")
    
    out_handle = codecs.open(out_seg_align_file, "w", "utf-8")

    line = best_handle.readline()
    while line:
        
        #Get utterance
        
        fname_alignments_best, best_handle, line = getUtterancePhonesCtm(best_handle, line, False) #keep sil labels
        fname_alignments_best = mergeAlignments(fname_alignments_best)
        
        fname = fname_alignments_best[-1][0]
        utt_labels = []
        segment_time_counter = 0 #in seconds
        segment_start_time = 0
        segment_counter = 1 #segment number given the larger utterance
        for item in fname_alignments_best:
            label = item[3]
            label_dur = item[2]
            
            if segment_time_counter < min_segment_duration:
                utt_labels.append(label)
                segment_time_counter += label_dur
            else: #find segmentation
                if label != "sil": #grow longer
                    utt_labels.append(label)
                    segment_time_counter += label_dur
                else:
                    if label_dur < min_sil_segment_duration: #grow longer
                        utt_labels.append(label)
                        segment_time_counter += label_dur
                        print "Warning: Short silence duration of ", label_dur, " not segmenting.."
                    else: #segment
                        
                        segment_fname = "_".join([fname, str(segment_counter)])
                        segment_end_time = segment_start_time + segment_time_counter + (label_dur/2.0)
                        utt_labels.append(label)
                        segment_duration = segment_end_time - segment_start_time
                        
                        if segment_duration > min_segment_duration*3:
                            print "Warning: Long segment duration: ",segment_duration
                        
                        segment_info_line = "".join([segment_fname,"\t",str(segment_duration),"\t",str(segment_start_time),"\t",str(segment_end_time),"\t"," ".join(utt_labels),"\n"])
                        
                        out_handle.write(segment_info_line)
                        
                        #Reset counters
                        utt_labels = []
                        utt_labels.append(label)
                        segment_time_counter = (label_dur/2.0)
                        segment_start_time = segment_end_time
                        segment_counter += 1 #segment number given the larger utterance
            
        line = best_handle.readline()
        
    out_handle.close()
    
    
    #out_line = " ".join(utt_labels)
        
    #out_handle = codecs.open(os.path.join(out_dir, "".join([fname,".txt"])), "w", "utf-8")
    #out_handle.write(out_line+"\n")
    


if __name__ == "__main__":
    

    #Add possible arguments
    parser = OptionParser()
    parser.add_option("-I", action="store", type="string", dest="in_ctm_file", help="Input ctm file for evaluation detector")
    parser.add_option("-o", action="store", type="string", dest="out_seg_align_file", help="Output segmentation")
    
    
    options, args = parser.parse_args()
    
    manageSegmenter(options.in_ctm_file, options.out_seg_align_file)
