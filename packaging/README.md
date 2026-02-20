# Speech Corpus XML Metadata Generator

A Python tool for generating XML metadata files for speech datasets using [generateDS](https://www.davekuhlman.org/generateDS.html).

## Quick Start

```bash
python build_corpus.py --config corpus_config.yaml
```

## Installation

### Requirements
- Python 3.7+
- PyYAML (`pip install pyyaml`)
- openpyxl (`pip install openpyxl`)
- six (`pip install six`)

## Usage

The script is driven by a YAML configuration file:

```bash
python build_corpus.py --config corpus_config.yaml
python build_corpus.py --config corpus_config.yaml --verbose
```

## Configuration File

The configuration file (`corpus_config.yaml`) has three sections:

### 1. Corpus Details
User-specified metadata for the `<corpus>` root element:

```yaml
name: "sama_nbl"
language: "nbl"
source: "IkwekweziFM"
genre: "studio_bulletins"
```

### 2. Recording Metadata
User-defined default values for `<recording>` elements:

```yaml
audio_format: "MP3_128_kb/s_bitrate"
confidence_score: "-1"
```

### 3. Data Source Options

**Option 1: Excel File** (set `xlsx_file` to the path)
```yaml
xlsx_file: "verified_metadata_spreadsheet.xlsx"  # Expected columns: filename, duration, transcription
```

**Option 2: Source Directories** (set `xlsx_file` to `null`)
```yaml
xlsx_file: null
audio_dir: "./audio"
text_dir: "./transcriptions"
```

### 4. Output
```yaml
output_file: "sama_nbl.xml"
```

## Directory Structure

When using Option 2 (source directories), organize files as:

```
project/
├── audio/
│   └── <speaker_id>/          # Folder name becomes speaker ID
│       ├── file1.wav
│       └── file2.wav
├── transcriptions/            # Flat directory
│   ├── file1.txt              # Same base name as audio
│   └── file2.txt
└── corpus_config.yaml
```

## Output XML Structure

```xml
<corpus name="sama_nbl" language="nbl" source="IkwekweziFM" genre="studio_bulletins">
    <speaker id="05h04jan2024">
        <recording audio="..." md5sum="..." duration="7.68" 
                   confidence_score="-1" recording_date="05h_04_jan_2024" 
                   audio_format="MP3_128_kb/s_bitrate">
            <transcript_word>transcription text here</transcript_word>
        </recording>
    </speaker>
</corpus>
```

## Modifying the XML Schema

To change the XML structure:

1. **Edit `corpus_radio.xsd`** to add/remove fields
2. **Regenerate the API**:
   ```bash
   generateDS -o corpus_api.py corpus_xml_structure.xsd
   ```
3. **Update `build_corpus.py`** to use the new fields

### Example: Adding a new recording attribute

1. Add to `corpus_xml_structure.xsd`:
   ```xml
   <xs:attribute name="new_field" type="xs:string"></xs:attribute>
   ```

2. Regenerate:
   ```bash
   generateDS -o corpus_api.py corpus_xml_structure.xsd
   ```

3. Update `build_corpus.py` in the `build()` method:
   ```python
   recording_elem = api.recordingType(
       ...
       new_field="value"
   )
   ```

## Files

| File | Description |
|------|-------------|
| `build_corpus.py`  |  Main script |
| `corpus_api.py`  |  generateDS-generated API |
| `corpus_xml_structure.xsd`  |  XML schema definition |
| `corpus_config.yaml`  |  Example configuration |
