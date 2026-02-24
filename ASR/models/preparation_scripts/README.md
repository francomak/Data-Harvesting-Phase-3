The following three scripts are used to create train, dev and test sets:        
- rename_audio_segments.py  
- convert_spreadsheet_transcriptions_to_textfiles.py    
- create_train_dev_test_lists.py    

The contents in the scripts are for Siswati broadcast news. Make adjustments inside each script if used for new datasets

Quick comments regarding each script:   
- rename_audio_segments.py:     
This script was used to rename the audio files. For ssw, the source audio segments were organised into bulletin folders. However, the exact bulletin name was not in each individual segment filename.
For example: bulletin name is "05h2nov2023", but segment name inside was "LigwalagwalaFM_news_2_Nov_2023_05_capture_14.wav". Lhotse data preparation scripts will look for the bulletin name after the second underscore (which is the naming convention used in NCHLT), so rename each audio segment to "LigwalagwalaFM_news_05h2nov2023_14.wav". If using this script for a new dataset, adjust the contents to match the required formatting or naming convention.

- convert_spreadsheet_transcriptions_to_textfiles.py    
This will import the transcription spreadsheet received from the transcription company, remove and compile bracket errors, and then save the transcription into a textfile for each individual segment.
This script does not accept user inputs into the terminal. Instead, open up the script, and make the following adjustments for new datasets:
    1. Change the path variables located at the very top, under the imports.
    2. `load_spreadsheet()` function imports the spreadsheet contents into a pandas dataframe. The expected columns (from left to right) are: 'bulletin', 'filename', 'duration', 'flag', 'transcription'. If this is not the case, change it in the spreadsheet, or update the code to match the new spreadheet column names
    3. `change_filename_convention()` function is used to rename the segments names (as mentioned under `rename_audio_segments.py` above). Update this function to match the new dataset's naming convention, or set `change_filename` variable to False to skip this step.

- create_train_dev_test_lists.py    
This script creates train, dev and test lists that contain filenames for segments assigned to each set. This script will only consider segments that have corresponding sentences in the transcription folder. The methodology is as follows:   

    1) Import all transcription segments into a pandas dataframe    
    2) Get corresponding audio duration     
    3) Randomly shuffle the order of rows   
    4) Calculate a cumulative total duration for each successive row    
    5) Allocate the first 30 min to the test set, which corresponds with a total cumulative duration of (30*60) seconds. Similarly, allocate the next 30 min to the dev set, and then all segments with a cumulative duration greater than 1 hour is assigned to the training set. This section of the code can be adjusted to create custom sets containing custom total durations by making changes to the cut-off points
