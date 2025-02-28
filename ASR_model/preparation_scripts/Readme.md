The following three scripts are used to create train, dev and test sets:
- rename_audio_segments.py
- convert_spreadsheet_transcriptions_to_textfiles.py
- create_train_dev_test_lists.py

The contents in the scripts are for Siswati broadcast news. Make adjustments inside each script if used for new datasets

Quick comments regarding each script:
- rename_audio_segments.py:
This script was used to rename the audio files. For ssw, the source audio segments were organised into bulletin folders. However, the exact bulletin name was not in each individual segment filename.
For example: bulletin name is "05h2nov2023", but segment name inside was "LigwalagwalaFM_news_2_Nov_2023_05_capture_14.wav". Lhotse data prep scripts will look for the bulletin name after the second underscore (which is the naming convention used in NCHLT), so rename each audio segment to "LigwalagwalaFM_news_05h2nov2023_14.wav"

- convert_spreadsheet_transcriptions_to_textfiles.py
This will import the transcription spreadsheet received from iTranscribe, remove and compile bracket errors, and then save the transcription into a textfile for each individual segment.
This script does not accept user inputs into the terminal. Instead, open up the script, and make the following adjustments for new datasets:
1. Change the path variables located at the very top, under the imports.
2. In line 19, import the spreadsheet contents into a pandas dataframe. The expected columns (from left to right) are: "Duration (s)", "Flag", "Filename", and "Transcription". If this is not the case, change it in the spreadsheet, or update the code to match the new spreadheet column names
3. As mentioned in the script above, there was a filenaming issue with ssw news where the bulletin name did not match the filename. This issue is also present in the spreadsheet. Line 40 renames each filename given in the "Filename" column of the spreadsheet. Make adjustments here if the naming convention for a new dataset is different, or comment out this line if no renaming is needed
4. In line 102, I filter for news-only segments that iTranscribe marked as 'N'. Update this line if you want to include other flags. Alternatively, update lines 109 and 110 to "for i in df.index" and "row = df.loc[i]" to write all segment transcriptions into individual textfiles.

- create_train_dev_test_lists.py
This script creates train, dev and test lists that contain filenames for segments assigned to each set. This script will only consider segments that have corresponding sentences in the transcription folder. The methodology is as follows:
a) import all transcription segments into a pandas dataframe
b) get corresponding audio duration
c) randomly shuffle the order of rows
d) calculate a cumulative total duration for each successive row
e) allocate the first 30 min to the test set, which corresponds with a total cumulative duration of (30*60) seconds. Similarly, allocate the next 30 min to the dev set, and then all segments with a cumulative duration greater than 1 hour is assigned to the training set. This section of the code can be adjusted to create custom sets containing custom total durations by making changes to the cut-off points
