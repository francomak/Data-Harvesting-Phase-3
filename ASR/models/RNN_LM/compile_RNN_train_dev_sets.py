"""
To train a RNN LM, you need a single text file containing sentences. 
Available text data is currently the following: NCHLT text, Leipzig text, and manually verified News & Drama segments
Transcriptions for corpuses are available as a textfile for each utterance (News), or already compiled in separate text files (NCHLT & Leipzig).
This script compiles all those textfiles together into a single file. It will split 90% of the text into a training set, and 10% into a validation set
""" 

import os
import random

# lang = 'tsn'
# compilation_textfile_paths = ["/media/franco_linux/CSIR/Datasets/Text_corpus/tsn/nchlt_JB.txt",
#                               "/media/franco_linux/CSIR/Datasets/Text_corpus/tsn/tsn_news_sentences_compilation.txt"]

lang = 'zul'
compilation_textfile_paths = ["/run/media/franco_linux/CSIR/Datasets/Text_corpus/zul/NCHLT_compilation.txt", 
                              "/run/media/franco_linux/CSIR/Datasets/Text_corpus/zul/zul_news_adaptation_sentence_compilation.txt",
                              "/run/media/franco_linux/CSIR/Datasets/Text_corpus/zul/Leipzig_compilation.txt"]

training_compilation = []
dev_compilation = []

random.seed = 42
### Corpus = News
# 
# news_filenames = os.listdir(NEWS_TRANS_DIR)
# random.shuffle(news_filenames)
# training_len = int(round(len(news_filenames)*0.9, 0))
# for i, filename in enumerate(news_filenames):
#     with open(f'{NEWS_TRANS_DIR}/{filename}') as file:
#         transcription = file.read().strip()
#         if i <= training_len:
#             training_compilation.append(transcription)
#         else:
#             dev_compilation.append(transcription)

def read_from_single_compilation_textfile(directory_paths):
    for filename in directory_paths:
        with open(filename) as file:
            all_transcriptions = file.read().split('\n')
            random.shuffle(all_transcriptions)
            training_len = int(round(len(all_transcriptions)*0.9, 0))
            for i, transcription in enumerate(all_transcriptions):
                if i <= training_len:
                    training_compilation.append(transcription)
                else:
                    dev_compilation.append(transcription)       

read_from_single_compilation_textfile(compilation_textfile_paths)
 
with open(f'languages/{lang}/nchlt_news_leipzig/nchlt_news_leipzig_training_sentences.txt', 'w') as file:
    for sentence in training_compilation:
        file.write(f'{sentence}\n')

with open(f'languages/{lang}/nchlt_news_leipzig/nchlt_news_leipzig_validation_sentences.txt', 'w') as file:
    for sentence in dev_compilation:
        file.write(f'{sentence}\n')