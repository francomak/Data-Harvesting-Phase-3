### ssw audio files had this naming convention: LigwalagwalaFM_news_2_Nov_2023_05_capture_14.wav. This did not match the speaker folder name, so change it so that it looks like LigwalagwalaFM_news_05h2nov2023_14.wav 

import os

audio_dir = "Datasets/Audio/Data_Harvesting/radio_news/ssw/iTranscribe/source_audio"
bulletins = os.listdir(audio_dir)

for bulletin in bulletins:
    audio_filenames = os.listdir(f'{audio_dir}/{bulletin}')
    for filename in audio_filenames:
        split = filename.split('_')
        correct_filename = f'{audio_dir}/{bulletin}/{"_".join([split[0], split[1], bulletin, split[7]])}'
        current_filename = f'{audio_dir}/{bulletin}/{filename}'
        os.rename(current_filename, correct_filename)
