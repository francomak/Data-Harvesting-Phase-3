#!/usr/bin/python3

import io
import sys
import os

import dpScores

def read_tra(tra_name):
    tra_dict = {}
    tra_file = open(tra_name)
    lines = tra_file.read().strip().split("\n")
    for line in lines:
        tokens = line.split()
        if len(tokens)<2:
            continue
        key, phones = tokens[0], tokens[1:]
        tra_dict[key] = phones
    tra_file.close()
    return tra_dict

def words_to_phones(word_dict, words):
    phones = ""
    for word in words:
        try:
            phones.append(word_dict[word])
        except KeyError:
            pass
    return " ".join(phones)

def create_phone_mlf(labels, segment_name, output_buffer):
    output_buffer.write(f'"*/{segment_name}.rec"\n')
    for label in labels:
        output_buffer.write("%f %f %s 0.0\n"%(0, 0, label))
    output_buffer.write(".\n")

def score_tras(tra_name1, tra_name2, output_buffer, smat=None):
    phone_buffers = []
    all_phones = {}
    tra_names = [tra_name1, tra_name2]
    for tra_name in tra_names:
        tra_dict = read_tra(tra_name)

        phone_buffer = io.StringIO()
        tra_keys_sorted = list(tra_dict.keys())
        tra_keys_sorted.sort()        
        for tra_key in tra_keys_sorted:
            create_phone_mlf(tra_dict[tra_key], tra_key, phone_buffer)
    
        phone_buffer.seek(0)
    
        # for line in phone_buffer:
        #     print(line.strip())
        # phone_buffer.seek(0)
        phone_buffers.append(phone_buffer)        
    if smat is None:
        for phone_set in tra_dict:
            for phone in phone_set:
                all_phones[phone] = True
    smat = dpScores.create_default_matrix(list(all_phones.keys()))
    dpScores.calc_utt_dp_scores_from_mlfs_buffers(phone_buffers[0], phone_buffers[1], smat, 0, output_buffer)

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <tra_file_1> <tra_file_2>", file=sys.stderr)
    sys.exit(1)
score_tras(sys.argv[1], sys.argv[2],sys.stdout)
