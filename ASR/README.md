# ASR tools and experiments

This repository is a work‑in‑progress collection of tools used for automatic speech recognition (ASR) experiments.

It contains:

- **Data preparation scripts** for turning raw audio + transcripts into ASR‑ready datasets.
- **Model recipes** (training, decoding, export) for several ASR architectures.
- **Inference utilities** to run models on new audio.
- **Scoring tools** to compare model outputs against reference transcriptions.

---

## Repository layout

At a high level:

- `DP_scoring/` – scoring tools for label files.
- `inference/` – scripts to run ASR models on lists of audio files.
- `models/` – model recipes, data prep, and helper scripts.

### `DP_scoring/`

Tools for scoring `.tra` label files using dynamic programming.

- `score_tras.py`
  Compares two `.tra` files (e.g. reference vs. hypothesis), where each line has the form:

  ```text
  <key> <label1> <label2> ...
  ```

  Mismatched entries are ignored with a warning; scores are written to standard output.

  Basic usage (from the `DP_scoring` directory):

  ```bash
  python3 score_tras.py <tra_file_1> <tra_file_2> > scores.txt
  ```

- `dpScores.py`
  Additional DP‑based scoring utilities (see the script itself for details).

See `DP_scoring/README.md` for the low‑level format and usage.

---

### `inference/`

Utilities to run inference (decoding) on audio files.

- `inference_with_filenames_list.py`
  Runs an ASR model over a list of filenames. Typical workflow:
  - Prepare a text file listing audio segment names or paths.
  - Configure paths/model settings at the top of the script (or via config).
  - Run the script to generate hypotheses for each segment.

- `vosk_decode/`
  Simple inference using Vosk models.
  - `vosk_decode.py`
    A wrapper around Vosk to decode audio.
  - `README.md`
    Short instructions on how to run this script and where to get models.

---

### `models/`

This directory holds most of the **recipe‑style ASR code**: data preparation, model training, decoding, and export.

Subdirectories include:

- `preparation_scripts/`
- `WSASR/`
- `zipformer/`
- `conformer_ctc2/`
- `RNN_LM/`
- `bash_scripts/`

#### `models/preparation_scripts/`

Dataset‑specific pre‑processing to get from raw audio + spreadsheets to train/dev/test lists.

- `create_train_dev_test_lists.py`
  - Creates train/dev/test lists (plain `.lst` files with one segment name per line).
  - Uses the available transcriptions and audio durations to:
    - Ensure segments have both audio and text.
    - Randomly shuffle and split according to duration targets (e.g. 30 min validation, 30 min test, remaining into train).

If you are preparing a new dataset, start by reading `models/preparation_scripts/Readme.txt` and then adapt these scripts (mainly paths and any dataset‑specific naming conventions).

---

#### `models/WSASR/`

A full ASR recipe (training + decoding) built on top of Lhotse, K2, and related tools.

Key components:

- `Lhotse_data_preparation.py`, `Lhotse_data_preparation_mixed_datasets.py`
  - Turn train/dev/test lists into:
    - Lhotse `RecordingSet` / `SupervisionSet` manifests.
    - `CutSet`s with fbank features precomputed and stored on disk.

- `asr_datamodule.py`, `asr_datamodule_multiple_cutsets.py`
  - Data loading / batching logic (bucketing samplers, SpecAugment, etc).
  - Arguments are partially driven by YAML configs (see below).

- `conformer.py`, `transformer.py`, `attention.py`, `subsampling.py`, `scaling.py`, etc.
  - Model architecture definitions (Conformer / Transformer‑style encoder, attention, etc.).

- `train.py`, `train_multiple_cutsets.py`
  - Training entry points for single or multiple cutsets.

- `decode_no_sil.py`
  - Different decoding modes (e.g. word‑level, phone‑level, with/without silence).

- `export.py`, `get_avg_results.py`, etc.
  - Utilities for exporting models and aggregating decoding results.

- `main_config.yaml`, `configs/`
  - Main experiment configuration and per‑experiment configs (paths, dataset names, hyperparameters, etc.).

Also see `Instructions.txt` in this directory for a higher‑level description of how to run WSASR experiments.

---

#### `models/zipformer/`

A Zipformer‑based ASR recipe (similar structure to WSASR, but with a different architecture and more ONNX/export options).

Representative files:

- `Lhotse_data_preparation.py`
  - Same idea as in WSASR: create manifests and `CutSet`s using Lhotse.

- `asr_datamodule.py`
  - Data loading and augmentation configuration (using YAML configs).

- `zipformer.py`, `model.py`, `attention_decoder.py`, `encoder_interface.py`, `subsampling.py`, `scaling.py`
  - Zipformer model definition and supporting modules.

- `train.py`, `finetune.py`
  - Training / fine‑tuning entry points.

- `decode.py`, `ctc_decode.py`, `streaming_decode.py`, `onnx_decode.py`, etc.
  - Various decoding options (greedy search, beam search, streaming, CTC, ONNX‑based decoding).

- `export.py`, `export-onnx*.py`, `jit_pretrained*.py`, `onnx_pretrained*.py`
  - Export to TorchScript / ONNX and helpers to run pre‑trained models.

- `main_config.yaml`, `configs/`
  - Configuration files controlling datasets, manifests, features, and model/training parameters.

---

#### Other `models/` subdirectories

- `conformer_ctc2/`
  - Alternative Conformer + CTC recipe (training/decoding for a different setup).

- `RNN_LM/`
  - Language‑model–related scripts 

- `bash_scripts/`
  - Helper bash scripts that chain together common steps (e.g. data prep → training → decoding).

---

## Typical workflows

This section gives a high‑level view of how pieces fit together. Exact commands and parameters are **in the scripts themselves** and may differ between projects.

### 1. Prepare a new dataset

1. **Start from raw audio + transcripts.**
   - Audio organised in folders (sometimes by speaker or bulletin).
   - Transcription spreadsheet (e.g. from external transcription company) with flags, filenames, and transcriptions.

2. **Fix filenames (if needed).**
   - Use `models/preparation_scripts/rename_audio_segments.py`  
     to bring filenames into a consistent format that later scripts expect.

3. **Convert spreadsheet to per‑segment text files.**
   - Use `models/preparation_scripts/convert_spreadsheet_transcriptions_to_textfiles.py`.
   - Edit the path variables and any dataset‑specific logic at the top of the script.
   - This will create one `.txt` per segment.

4. **Create train/dev/test lists.**
   - Use `models/preparation_scripts/create_train_dev_test_lists.py`.
   - This reads the transcription files (and corresponding audio durations) and produces `.lst` files.
 
5. **Generate Lhotse manifests and features.**
   - Pick a recipe (`models/WSASR` or `models/zipformer`).
   - Configure dataset paths and output directories in `main_config.yaml` and the relevant config in `configs/`.
   - Run `Lhotse_data_preparation.py` (in the chosen recipe) to:
     - Create `RecordingSet` / `SupervisionSet` manifests.
     - Create `CutSet`s with fbank features and save them.

### 2. Train a model

1. Choose a recipe: `models/WSASR`, `models/zipformer`, or `models/conformer_ctc2`.
2. Set up `main_config.yaml` and the file under `configs/` for your experiment.
3. Run the appropriate training script, e.g.:
   - `python train.py` (from inside the recipe directory)
4. Monitor logs/metrics as defined in the script (tensorboard, text logs, etc.).

### 3. Run inference

Options include:

- **Recipe‑specific decoding**
  - Use `decode.py`, `ctc_decode.py`, `streaming_decode.py`, `onnx_decode.py`, etc. inside the chosen model recipe directory.
  - These scripts typically take arguments like `--exp-dir`, `--epoch`, `--avg`, `--decoding-method`, etc. (see script docstrings / usage blocks).

- **Generic inference on a list of filenames**
  - `inference/inference_with_filenames_list.py`
    for running a model over a list of segments.

- **Using Vosk**
  - `inference/vosk_decode/vosk_decode.py`
    for a simpler pipeline based on Vosk models (see `inference/vosk_decode/README.md`).

### 4. Score results

- For **low‑level label comparison** (e.g. phone or token sequences):
  - Use `DP_scoring/score_tras.py` to compare two `.tra` files.

- For **word error rate (WER) and overall ASR performance**:
  - Use the result aggregation utilities provided in the chosen recipe
    (e.g. `get_asr_results.py`, `get_avg_results.py`, or scripts documented inside the model directory).

---

## Dependencies and environment

This repo is **not yet packaged** as a standalone library. Different parts rely on:

- Python 3
- Common scientific/ML stack (e.g. PyTorch, PyYAML, pandas, librosa, Lhotse, k2/icefall, sentencepiece, etc.)
- Vosk (for `inference/vosk_decode`)

For now:

- Check the **imports at the top of each script** to see what is required.
- Use your existing ASR environment, or create a new one and install the required packages.

A more systematic list of dependencies / environment files may be added later.
