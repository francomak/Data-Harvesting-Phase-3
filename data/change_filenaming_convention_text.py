import os
import shutil 

text_dir = 'CSIR/Datasets/Audio/Data_Harvesting/radio_news/nbl/adaptation_set/transcriptions'
sub_folders_used = False # True/False . True if audio files are organized into sub-folders
rename_or_copy = "copy" # Choose between "rename" or "copy". Rename will directly rename the original file, while copy will create a copy which leaves the original as a backup

def new_naming_convention(filename):
    ### Current usage e.g. for nbl: sama_nbl_05h02feb2022_capture_4.wav
    split = filename.split('.')[0].split('_')
    corpus_name = f"{split[0]}_{split[1]}"
    date = split[2]
    seg_num = split[4].zfill(4)
    
    new_name = f"{corpus_name}_{date}_{seg_num}.txt"
    return new_name

if rename_or_copy == "copy":
    parent_dir = os.path.dirname(text_dir)
    target_folder_name = os.path.basename(text_dir) + "_new"
    target_folder_path = os.path.join(parent_dir, target_folder_name)  # This will be the new parent folder to store the renamed files
    if not os.path.exists(target_folder_path):
        os.makedirs(target_folder_path) 

outputs = []
if sub_folders_used:
    folders = os.listdir(text_dir)
    for folder in folders:
        text_filenames = os.listdir(f"{text_dir}/{folder}")
        for text_file in text_filenames:
            try:
                new_name = new_naming_convention(text_file)
                source_file = f"{text_dir}/{folder}/{text_file}"
                
                if rename_or_copy == 'rename':
                    dest_path = f"{text_dir}/{folder}/{new_name}"
                    os.rename(src=source_file, dst=dest_path)

                elif rename_or_copy == 'copy':
                    dest_dir = f"{target_folder_path}/{folder}"
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)

                    dest_path = os.path.join(dest_dir, new_name)
                    shutil.copy2(src=source_file, dst=dest_path)
            except:
                print(f"Skipped file with unexpected name format: {text_file}")

else:  ## No sub-folders used
    text_filenames = os.listdir(text_dir)
    for text_file in text_filenames:
        try:
            new_name = new_naming_convention(text_file)
            source_file = f"{text_dir}/{text_file}"
            
            if rename_or_copy == 'rename':
                dest_path = f"{text_dir}/{new_name}"
                os.rename(src=source_file, dst=dest_path)

            elif rename_or_copy == 'copy':
                dest_dir = f"{target_folder_path}"
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                dest_path = os.path.join(dest_dir, new_name)
                shutil.copy2(src=source_file, dst=dest_path)
        except:
            print(f"Skipped file with unexpected name format: {text_file}")


