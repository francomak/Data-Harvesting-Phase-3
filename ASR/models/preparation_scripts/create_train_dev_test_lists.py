"""
News datasets don't have pre-built train, dev and test sets, or I may want to create custom sets. Lhotse dataprep is coded to use a list textfile to pull in filenames, so use this script to create those lists
"""

import os
import librosa
import pandas as pd

lang = "ssw"
audio_dir = "Datasets/Audio/Data_Harvesting/radio_news/ssw/iTranscribe/source_audio"
transcription_dir = "Datasets/Audio/Data_Harvesting/radio_news/ssw/iTranscribe/transcriptions"
list_dir = "Datasets/Audio/Data_Harvesting/radio_news/ssw/iTranscribe/lists"

text_filenames = os.listdir(transcription_dir)
segments = [x.split(".")[0] for x in text_filenames if len(x)>0]  # remove ".txt" from the filenames

### Check total available duration
segments_list = []
bulletin_list = []
duration_list = []
total_duration = 0
for segment in segments:
    bulletin = segment.split('_')[2]
    dur = librosa.get_duration(path=f'{audio_dir}/{bulletin}/{segment}.wav')
    segments_list.append(segment)
    bulletin_list.append(bulletin)
    duration_list.append(round(dur, 2))
    total_duration += dur

print(f"Total available duration of audio files that have corresponding sentences in the transciptions folder is {round(total_duration/3600, 2)} hours")

### Allocate segments into train, dev and test sets
data_df = pd.DataFrame(data={"filename": segments_list, "duration": duration_list})
data_df = data_df.sample(frac=1, random_state=42).reset_index(drop=True)  # randomly shuffle all the rows
data_df["cumulative_dur"] = data_df["duration"].cumsum()  # Get the cumulative total duration in seconds for each successive row

df_test = data_df[data_df["cumulative_dur"] <= (30*60)]  # assign first 30 min of the randomly shuffled rows to the test set. Since cumulative time is in seconds, convert min to seconds
test_set = sorted(df_test["filename"])

df_dev = data_df[(data_df["cumulative_dur"] > (30*60)) & (data_df["cumulative_dur"] <= (60*60))]  # assign the next 30 min to the dev set, which are the rows with a cumulative duration between 30 min and 60 min
dev_set = sorted(df_dev["filename"])

df_train = data_df[data_df["cumulative_dur"] > (60*60)] ## Assign the rest into the training set. Add "& (data_df["cumulative_dur"] <= (9*3600))" to limit the training set to a fixed number of hours (between 1h and 9h creates an 8h training set)
train_set = sorted(df_train["filename"])

output_files = [[f"news_{lang}.trn.lst", train_set],  
                [f"news_{lang}_30min.tst.lst", test_set],
                [f"news_{lang}_30min.dev.lst", dev_set]]

for list_filename, segment_names in output_files:
    with open(f"{list_dir}/{list_filename}", 'w') as file:
        for segment in segment_names:
            file.write(f'{segment}\n')