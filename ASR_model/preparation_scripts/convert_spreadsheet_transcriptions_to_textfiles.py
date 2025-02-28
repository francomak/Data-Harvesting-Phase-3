"""
For broadcast news, we compiled a spreadsheet containing initial transcriptions and sent it to iTranscribe to manually verify and correct transcription errors. 
The columns in the spreadsheet (from left to right): "Duration (s)", "Flag", "Filename", and "Transcription". If the spreadsheet has different columns, update pd.Dataframe in line 19 below
Use this script to import sentences from the spreadsheet, remove bracket errors, and save each segment's transcription into individual textfiles.
"""

import pandas as pd
import re
import string
import random
import shutil

spreadsheet_file = '/media/franco_linux/CSIR/Datasets/Audio/Data_Harvesting/radio_news/ssw/iTranscribe/sama_ssw_10h_iTranscribe.xlsx'
audio_dir = '/media/franco_linux/CSIR/Datasets/Audio/Data_Harvesting/radio_news/ssw/iTranscribe/source_audio'
transcriptions_dir = '/media/franco_linux/CSIR/Datasets/Audio/Data_Harvesting/radio_news/ssw/iTranscribe/transcriptions'
list_dir = '/media/franco_linux/CSIR/Datasets/Audio/Data_Harvesting/radio_news/ssw/iTranscribe/lists'

data = pd.read_excel(spreadsheet_file)
df = pd.DataFrame(data, columns=['Duration (s)', 'Flag', 'Filename', 'Transcription'])
df = df.rename(columns={"Duration (s)": "duration", "Flag": "flag", "Filename": "filename", "Transcription": "transcription"})
df = df[df.filename.notnull()]  # Filter out any empty rows by removing rows that don't contain a filename
df['filename'] = df['filename'].apply(lambda x: x.split('.')[0])  # Drop the '.wav' portion of the filename
df.reset_index(drop=True, inplace=True)

def rename_bulletin_portion_of_filename(filename):
    split = filename.split('_')
    day = split[2]
    month = str(split[3]).lower()
    year = split[4]
    hour = split[5]+'h'
    bulletin = f'{hour}{day}{month}{year}'

    correct_filename = "_".join([split[0], split[1], bulletin, split[7]])
    return correct_filename

### NB: comment out the function below if it is not applicable
### For ssw, the filenames were automatically generated e.g. "LigwalagwalaFM_news_19_Oct_2022_13_capture_17.wav"
### However, the corresponding bulletin folder (from source_audio) is 13h19oct2022. In Lhotse dataprep, it extracts the bulletin folder name by extracting it after the second underscore, so rename each segment to:
### "LigwalagwalaFM_news_19_Oct_2022_13_capture_17.wav"  becomes "LigwalagwalaFM_news_13h19oct2022_17.wav"
df['filename'] = df['filename'].apply(lambda x: rename_bulletin_portion_of_filename(x))

error_list = [] # Stores a list of errors. Errors are any text marked between [ ]
error_free_sentence_list = []  # List to store error free sentences
error_free_flag_list = [] # List to store whether or not an error was found in that sentence. Only perfect sentences will be used in the first set of training data 
unique_errors = set()

for i in range(len(df)):
    sentence = df['transcription'][i]
    sentence = str(sentence).lower() # Use lower case letters to avoid duplicate words in dictionary
    error_free_flag = True
    if '[' in sentence:
        error_free_flag = False
        list_of_errors = re.findall('\[.*?\]', sentence)
        for error in list_of_errors:
            unique_errors.add(error)
            error_list.append([error, df['filename'][i], df['transcription'][i]])
            if '+' in error:
                foreign_word = error.split('+')[1].strip() # foreign words are indicated with the following format: [foreign_eng + yes]
                sentence = sentence.replace(error, foreign_word)  # replace the bracket error with the foreign word
            else:
                sentence = sentence.replace(error, '')  # Replace error word with a blank space to remove it from the sentence
    sentence = ' '.join(sentence.split())  # Remove any extra spaces that might have been introduced from replacing words above

    for word in sentence.split():  
        if '_' in word: 
            word = word.replace('_', ' ') # replace underscores with a space so that t_v becomes t v 
        word = word.translate(str.maketrans('', '' , string.punctuation)) # Remove all punctuation
        
    if '_' in sentence: 
        sentence = sentence.replace('_', ' ') # replace underscores with a space so that t_v becomes t v  
    sentence = sentence.translate(str.maketrans('', '' , string.punctuation)) # Remove all punctuation

    error_free_flag_list.append(error_free_flag)  
    error_free_sentence_list.append(sentence)

df['error_free'] = error_free_flag_list
df['error_free_sentence'] = error_free_sentence_list
df.head()

### Print out how many sentences in the spreadsheet contained no bracket errors
true_counter = 0
false_counter = 0
for flag in error_free_flag_list:
    if flag:
        true_counter += 1
    else:
        false_counter += 1
print(f'In the spreadsheet there is a total of {true_counter} sentences that contained no bracket error')
print(f'In the spreadsheet there is a total of {false_counter} sentences that contained at least 1 bracket error')
print('')

### print out bracket error related data into text files
df_all_errors = pd.DataFrame(error_list, columns=['error', 'filename', 'original_sentence'])
base_dir = "/".join(audio_dir.split('/')[:-1])
df_all_errors.to_csv(f'{base_dir}/all_errors_compilation.csv', index=False)

with open(f'{base_dir}/all_unique_bracket_errors.txt', 'w') as f:
    for error in unique_errors:
        f.write(f'{error}\n')

### Filter the spreadsheet for news-only segments i.e. segments that iTranscribe flagged as "N". Make adjustments here to include other types of segment flags
only_news = df[df['flag'] == 'N']
perfect_only_news = only_news[only_news['error_free'] == True]  ## This filters for sentences that don't have any bracket errors
print(f'Total duration of segments flagged as news: {round(only_news["duration"].sum()/3600, 2)} hours')
print(f"Total duration of segments that don't contain errors: {round(perfect_only_news['duration'].sum()/3600, 2)} hours")
print('')

### Save transcriptions into individual textfiles
for i in only_news.index:
    row = only_news.loc[i]
    with open(f"{transcriptions_dir}/{row['filename']}.txt", 'w') as file:
        file.write(row['error_free_sentence'])