#!/bin/bash
# This helps prevent errors in later steps if an earlier one fails
set -Eeuo pipefail

# ------- Configuration Section ---------------------------------------

# Define input directory paths
DATA_LANGUAGE="zul"
DATA_TEXT_CORPUS_COMPILATION_FILE="/run/media/franco_linux/Data/Text/zul/zul_news_training_set_compilation.txt"  # A single textfile containing a compilation of text sentences for language model training

# Define output directory paths
## Below are related to language models
OUTPUT_NEW_LM_FOLDER="zul/news_only"  ## Set a new folder name in which to store "lang_phone", "lang_bpe", and "lm"

# Define current working directory paths (to cd into during script execution)
CWD_UPDATE_DICTIONARY="update_dictionary"
CWD_NGRAM_LANGUAGE_MODEL="Language_models/ngram"
LM_OUTPUT_DIR="example_outputs"

# Define other/experiment parameters
BPE_VOCABULARY_SIZE=500
USE_OTC_TOKEN=no   ## Choose between yes or no. WSASR model requires an OTC token ("<star>") in the lexicon, but Conformer CTC does not use it.

# Path variables (so that the script execution section is more readable)
LANG_PHONE=languages/$OUTPUT_NEW_LM_FOLDER/lang_phone
LANG_BPE=languages/$OUTPUT_NEW_LM_FOLDER/lang_bpe_$BPE_VOCABULARY_SIZE
LM=languages/$OUTPUT_NEW_LM_FOLDER/lm

# ------- Script Execution Section ------------------------------------
echo "Step 1: Update pronunciation dictionary"
mkdir -p $LM_OUTPUT_DIR/$LANG_PHONE   # Creating it here to save the updated lexicon into lang_phone
cd $CWD_UPDATE_DICTIONARY

echo "Running add_oov_words_to_dict.py to add G2P predictions for oov words"
python add_oov_words_to_dict.py --language $DATA_LANGUAGE --text_corpus_name $DATA_TEXT_CORPUS_COMPILATION_FILE --lexicon_output $LM_OUTPUT_DIR/$LANG_PHONE/lexicon.txt


echo "Step 2: Creating lang_phone"
cd $CWD_NGRAM_LANGUAGE_MODEL

echo "Running prepare_lang.py"
python ngram_scripts/prepare_lang.py --lang-dir $LM_OUTPUT_DIR/$LANG_PHONE

echo "Running convert-k2-to-openfst.py"
python ngram_scripts/convert-k2-to-openfst.py --olabels aux_labels $LM_OUTPUT_DIR/$LANG_PHONE/L.pt $LM_OUTPUT_DIR/$LANG_PHONE/L.fst
python ngram_scripts/convert-k2-to-openfst.py --olabels aux_labels $LM_OUTPUT_DIR/$LANG_PHONE/L_disambig.pt $LM_OUTPUT_DIR/$LANG_PHONE/L_disambig.fst

echo "Step 3: Creating lang_bpe"
mkdir -p $LM_OUTPUT_DIR/$LANG_BPE
echo "Running get_words_from_lexicon.py"
python bpe_scripts/get_words_from_lexicon.py --lang-dir $LM_OUTPUT_DIR/$LANG_PHONE --otc-token "<star>"
cp $LM_OUTPUT_DIR/$LANG_PHONE/words.txt $LM_OUTPUT_DIR/$LANG_BPE

echo "Running train_bpe_model.py"
python bpe_scripts/train_bpe_model.py --lang-dir $LM_OUTPUT_DIR/$LANG_BPE --vocab-size $BPE_VOCABULARY_SIZE --transcript $DATA_TEXT_CORPUS_COMPILATION_FILE

echo "Running prepare_lang_bpe.py to generate L.pt and L_disambig.pt"

if [ "$USE_OTC_TOKEN" = yes ] ;
then
    python bpe_scripts/prepare_otc_lang_bpe.py --lang-dir $LM_OUTPUT_DIR/$LANG_BPE --otc-token "<star>"

elif [ "$USE_OTC_TOKEN" = no ] ;
then
    python bpe_scripts/prepare_lang_bpe.py --lang-dir $LM_OUTPUT_DIR/$LANG_BPE
fi

python bpe_scripts/validate_bpe_lexicon.py --lexicon $LM_OUTPUT_DIR/$LANG_BPE/lexicon.txt --bpe-model $LM_OUTPUT_DIR/$LANG_BPE/bpe.model --otc-token "<star>"

echo "Running convert-k2-to-openfst.py"
python bpe_scripts/convert-k2-to-openfst.py --olabels aux_labels $LM_OUTPUT_DIR/$LANG_BPE/L.pt $LM_OUTPUT_DIR/$LANG_BPE/L.fst
python bpe_scripts/convert-k2-to-openfst.py --olabels aux_labels $LM_OUTPUT_DIR/$LANG_BPE/L_disambig.pt $LM_OUTPUT_DIR/$LANG_BPE/L_disambig.fst


echo "Step 4: Creating lm"
mkdir -p $LM_OUTPUT_DIR/$LM
echo "Creating 3-gram and 4-gram language models using KenLM"
lmplz -o 3 < $DATA_TEXT_CORPUS_COMPILATION_FILE > $LM_OUTPUT_DIR/$LM/3_gram.arpa
#lmplz -o 4 < $DATA_TEXT_CORPUS_COMPILATION_FILE > $LM/4_gram.arpa

echo "Step 5: Creating G"
python -m kaldilm --read-symbol-table=$LM_OUTPUT_DIR/$LANG_PHONE/words.txt --disambig-symbol='#0' --max-order=3 $LM_OUTPUT_DIR/$LM/3_gram.arpa > $LM_OUTPUT_DIR/$LM/G_3_gram.fst.txt
#python -m kaldilm --read-symbol-table=$LANG_PHONE/words.txt --disambig-symbol='#0' --max-order=4 $LM/4_gram.arpa > $LM/G_4_gram.fst.txt

echo "Step 6: Compiling HLG"
python bpe_scripts/compile_hlg.py --lang-dir $LM_OUTPUT_DIR/$LANG_BPE --lm $LM_OUTPUT_DIR/$LM/G_3_gram
python ngram_scripts/compile_hlg.py --lang-dir $LM_OUTPUT_DIR/$LANG_PHONE --lm $LM_OUTPUT_DIR/$LM/G_3_gram

exit 0
