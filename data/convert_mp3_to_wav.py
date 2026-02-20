'''
Convert mp3 format to wav. At the same time, also rename the original recordings to contract the date-related metadata into the SAMA news bulletin format. For example:
Original: IkwekweziFM_news_1_Apr_2025_09_capture.wav
Rename: IkwekweziFM_news_09h01apr2025.wav
'''

import os

original_audio_dir = "languages/nbl/nbl_adaptation_set_original_recordings"
output_dir = "languages/nbl/nbl_adaptation_set_wav"

def rename_file(original_name):
    split = original_name.split('_')
    new_filename = f"{split[0]}_{split[1]}_{split[5]}h{int(split[2]):02d}{split[3].lower()}{split[4]}.wav"
    return new_filename

audio_filenames = os.listdir(original_audio_dir)
for fname in audio_filenames:
    if fname.endswith(".mp3"):
        new_filename = rename_file(fname)
        cmd_line = f"ffmpeg -i {original_audio_dir}/{fname} -ar 16000 -ac 1 {output_dir}/{new_filename}"
        print(cmd_line)

        os.system(cmd_line)