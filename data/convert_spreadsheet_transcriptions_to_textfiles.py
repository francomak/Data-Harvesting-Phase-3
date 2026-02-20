"""
Context: 
For radio broadcast news, we compiled a spreadsheet containing initial ASR predictions and sent it to an external transcription company (iTranscribe/Tuming-Lee) to manually verify and correct transcription errors. 
The columns in the spreadsheet (from left to right): "bulletin", "filename", "duration", "flag", and "transcription"
Use this script to load data from the spreadsheet, remove bracket error tags, and save each segment's transcription into individual textfiles. There are also functions to create train/dev/test sets
"""

import pandas as pd
import re
import string
import random
import shutil

spreadsheet_file = '/run/media/franco_linux/CSIR/Datasets/Audio/Data_Harvesting/radio_news/nbl/adaptation_set/received_nbl_adaptation_set_ndebele.xlsx'
spreadsheet_column_names = ['bulletin', 'filename', 'duration', 'flag', 'transcription']

output_transcriptions_dir = '/run/media/franco_linux/CSIR/Datasets/Audio/Data_Harvesting/radio_news/nbl/adaptation_set/transcriptions'  # Empty dir to save each individual segment's transcription
output_list_dir = '/run/media/franco_linux/CSIR/Datasets/Audio/Data_Harvesting/radio_news/nbl/adaptation_set/lists' # Lists dir to save train/dev/test splits 
lang = 'nbl'
change_filename = True # Boolean value. True if filenaming convention needs to be updated to conform to previously used naming convention. See change_filenaming_convention function below for explanation

def change_filename_convention(filename):
    '''
    For nbl, the filenames in the adaptation set (and spreadsheet) is labelled as follows: "sama_nbl_05h02feb2022_capture_4"
    Previous datasets looked like this: "sama_zul_06h02jan2022_0002"
    Therefore, slightly rename the end-portion of the nbl segments from "capture_4" to "0004"
    '''
    split = filename.split('_')
    seg_number = split[-1]
    correct_filename = "_".join([split[0], split[1], split[2], seg_number.zfill(4)])  # Use zfill() to pad with zeros until the specified width is reached
    return correct_filename

def load_spreadsheet():
    data = pd.read_excel(spreadsheet_file)
    df = pd.DataFrame(data, columns=spreadsheet_column_names)
    df = df[df.filename.notnull()]  # Filter out any empty rows by removing rows that don't contain a filename
    df['filename'] = df['filename'].apply(lambda x: x.split('.')[0])  # Drop the '.wav' portion of the filename
    df.reset_index(drop=True, inplace=True)

    if change_filename:
        df['filename'] = df['filename'].apply(lambda filename: change_filename_convention(filename))

    print(df.head())
    print(len(df.transcription))
    return df

def remove_bracket_errors(df):
    '''
    iTranscribe marked unintelligible words or partial word segments in the audio within square brackets. Remove them from the training transcriptions, and store them in a textfile
    '''
    error_list = [] # Stores a list of errors. Errors are any text marked between [ ]
    error_free_sentence_list = []  # List to store error free sentences
    error_free_flag_list = [] # List to store whether or not an error was found in that sentence. Only perfect sentences will be used in the first set of training data 

    for i in df.index:
        sentence = df['transcription'][i]
        sentence = str(sentence).lower() # Use lower case letters to avoid duplicate words in dictionary
        error_free_flag = True
        if '[' in sentence:
            error_free_flag = False
            list_of_errors = re.findall('\[.*?\]', sentence)
            for error in list_of_errors:
                error_list.append([error, df['filename'][i], df['transcription'][i]])
                if '+' in error:
                    foreign_word = error.split('+')[1].strip() # foreign words are indicated with the following format: [foreign_eng + yes]
                    sentence = sentence.replace(error, foreign_word)  # replace the bracket error with the foreign word
                else:
                    sentence = sentence.replace(error, '')  # Replace error words without a plus (e.g. [?]) with a blank space to remove it from the sentence
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
    return df, error_list

def count_errors(df):
    error_free_list = df['error_free']
    true_counter = 0
    false_counter = 0
    for flag in error_free_list:
        if flag:
            true_counter += 1
        else:
            false_counter += 1
    print(f'In the spreadsheet there is a total of {true_counter} sentences that contained no bracket errors')
    print(f'In the spreadsheet there is a total of {false_counter} sentences that contained at least 1 bracket error')
    print('')
 
def filter_by_flag(df, flag):
    '''
    In the spreadsheet, iTranscribe was asked to assign a flag to each segment to indicate the content of the speech. 'N' is for news-only speech
    '''
    filtered_df = df[df['flag'] == flag]
    print(f'Total duration of segments flagged as news: {round(filtered_df["duration"].sum()/3600, 2)} hours')
    return filtered_df

def assign_train_dev_test_sets(news_only):
    perfect_news_only = news_only[news_only['error_free'] == True]  ## This filters for sentences that don't have any bracket errors. These are the highest quality sentences that get priority for test and dev sets
    imperfect_news = news_only[news_only['error_free'] == False]
    
    print(f"Total duration of segments that don't contain bracket errors: {round(perfect_news_only['duration'].sum()/3600, 2)} hours")
    
    data_df = perfect_news_only.sample(frac=1, random_state=42).reset_index(drop=True)
    data_df["cumulative_dur"] = data_df["duration"].cumsum()

    df_test = data_df[data_df["cumulative_dur"] <= (30*60)]  # assign first 30 min of the randomly shuffled rows to the test set. Since cumulative time is in seconds, convert min to seconds
    test_set = sorted(df_test["filename"])

    df_dev = data_df[(data_df["cumulative_dur"] > (30*60)) & (data_df["cumulative_dur"] <= (60*60))]  # assign the next 30 min to the dev set, which are the rows with a cumulative duration between 30 min and 60 min
    dev_set = sorted(df_dev["filename"])

    df_train = data_df[data_df["cumulative_dur"] > (60*60)] ## Assign the rest into the training set. Add "& (data_df["cumulative_dur"] <= (9*3600))" to limit the training set to a fixed number of hours (between 1h and 9h creates an 8h training set)
    train_set = sorted(list(df_train["filename"]) + list(imperfect_news["filename"]))

    output_lists = [[f"news_{lang}.trn.lst", train_set],  
                    [f"news_{lang}_30min.tst.lst", test_set],
                    [f"news_{lang}_30min.dev.lst", dev_set]]
    return output_lists

def save_lists(output_lists):
    for list_filename, segment_names in output_lists:
        with open(f"{output_list_dir}/{list_filename}", 'w') as file:
            for segment in segment_names:
                file.write(f'{segment}\n')

def save_errors_to_file(error_list):
    df_all_errors = pd.DataFrame(error_list, columns=['error', 'filename', 'original_sentence'])
    unique_errors = set(df_all_errors['error'])
    base_dir = "/".join(output_transcriptions_dir.split('/')[:-1])
    df_all_errors.to_csv(f'{base_dir}/all_errors_compilation.csv', index=False)

    with open(f'{base_dir}/all_unique_bracket_errors.txt', 'w') as f:
        for error in unique_errors:
            f.write(f'{error}\n')

def save_transcriptions_to_file(df):
    base_dir = "/".join(output_transcriptions_dir.split('/')[:-1])
    for i in df.index:
        row = df.loc[i]
        sentence = row['error_free_sentence']
        filename = row['filename']
        if len(sentence) < 2: 
            print(f"{filename} skipped because transcription was empty, or contained a single word")
            with open(f"{base_dir}/skipped_filenames.txt", 'a') as file:
                file.write(f"{filename}\t{sentence}\n")
        else:
            with open(f"{output_transcriptions_dir}/{filename}.txt", 'w') as file:
                file.write(sentence)


'''
Run the extraction for adaptation set spreadsheets sent to iTranscribe for manual verification
'''
df = load_spreadsheet()
df, error_list = remove_bracket_errors(df)
save_transcriptions_to_file(df)
count_errors(df)
save_errors_to_file(error_list)

news_only_df = filter_by_flag(df, flag='N')
output_lists = assign_train_dev_test_sets(news_only_df)
save_lists(output_lists)

