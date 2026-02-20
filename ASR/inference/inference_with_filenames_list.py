 
import os
import codecs

epoch = 6
batch_size = 1 #Must be 10 and larger
max_dur = 100

fnames_list = "fnames_not_decoded.txt"

exp_dir = "exp_nbl_news_610h_only_bpe_200_add_nchlt_words"
lang_dir = "data_nbl_news_50h_itr1/lang_bpe_200_manual_trans_add_nchlt_words"
manifest_dir = "data_nbl_news_610h_itr2"

decode_manifest = "nbl_sama_nbl_fnames_1_cuts.jsonl"
temp_decode_manifest = "nbl_sama_nbl_fnames_1_cuts_batch.jsonl"

batch_out_file = "recogs-train-ctc-decoding.txt" #The file in exp dir from which output should be copied
out_file = "all_recogs_retry_cuts.txt"

#Read fname fnames_list
required_fnames = []
in_handle = codecs.open(fnames_list, "r", "utf-8")
for line in in_handle:
    fname = line.split()[0]
    required_fnames.append(fname)

#Perform recognition per limited batch of cutsets at a time -> Iterate through cutset file -> batch of lines at a time
line_counter = 0
in_handle = codecs.open(os.path.join(manifest_dir, decode_manifest), "r", "utf-8")
out_handle = codecs.open(os.path.join(manifest_dir, temp_decode_manifest), "w", "utf-8")
for line in in_handle:
    if line_counter < batch_size:
        line_fname = line.split("{\"id\": \"")[1].split("-")[0]
        if line_fname in required_fnames:
            out_handle.write(line)
            line_counter += 1
    else:
        
        out_handle.close()
        line_counter = 0
    
        #Run recognition on batch
        cmd_string = "".join(["python decode_wsasr_nbl_retranscribe.py --epoch ",str(epoch)," --avg ",str(1)," --use-averaged-model=False --method ctc-decoding --exp-dir ",exp_dir, " --lang-dir ", lang_dir, " --manifest-dir ", manifest_dir, " --feature-dim 80 --num-decoder-layers=0 --bucketing-sampler=False --max-duration=",str(max_dur)," --decode-manifest ", temp_decode_manifest])
        print(cmd_string)
    
        os.system(cmd_string)
    
        #Collate results
        res_handle = codecs.open(os.path.join(exp_dir, batch_out_file), "r", "utf-8")
        collate_handle = codecs.open(os.path.join(exp_dir, out_file), "a", "utf-8")
        for line in res_handle:
            collate_handle.write(line)
        res_handle.close()
        collate_handle.close()
        out_handle = codecs.open(os.path.join(manifest_dir, temp_decode_manifest), "w", "utf-8")
        
#Collate last batch
out_handle.close()

    
#Run recognition on batch
cmd_string = "".join(["python decode_wsasr_nbl_retranscribe.py --epoch ",str(epoch)," --avg ",str(1)," --use-averaged-model=False --method ctc-decoding --exp-dir ",exp_dir, " --lang-dir ", lang_dir, " --manifest-dir ", manifest_dir, " --feature-dim 80 --num-decoder-layers=0 --bucketing-sampler=False --max-duration=",str(max_dur)," --decode-manifest ", temp_decode_manifest])
print(cmd_string)
    
os.system(cmd_string)
    
#Collate results
res_handle = codecs.open(os.path.join(exp_dir, batch_out_file), "r", "utf-8")
collate_handle = codecs.open(os.path.join(exp_dir, out_file), "a", "utf-8")
for line in res_handle:
    collate_handle.write(line)
res_handle.close()
collate_handle.close()
in_handle.close()
