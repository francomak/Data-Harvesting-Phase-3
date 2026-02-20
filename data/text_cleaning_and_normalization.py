'''
This script does text pre-processing by performing the following steps for each segment:
> Convert all text to lower case
> Replace dashes (-) and colons (:) with a space (e.g. specifically for time so that 2:30 doesn't become 230)
> Replace percentage symbol (%) with 'percent', and ampersand (&) with 'and'
> Remove all other remaining punctuation
> Convert accented characters (like é, ñ, ü) to their base ASCII letters (e, n, u)
> Replace numeric digits with their English word equivalents
> Remove/ignore any character not in the 26 basic English letters or whitespace
> Normalize multiple spaces to a single space
> Trim leading/trailing spaces
'''

import re
import string
import unicodedata
from num2words import num2words
from pathlib import Path
from lhotse import CutSet
from tqdm import tqdm

def clean_text(text: str) -> str:
    """
    Cleans a line of text by performing a full normalization pipeline.
    """
    # Step 1: Lowercase the text
    text = text.lower()

    # Step 2: Normalize Unicode characters (e.g., é -> e)
    # This converts accented characters to their base ASCII form
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

    # Step 3: Number-to-Word Conversion
    def number_replacer(match):
        num_str = match.group()
        try:
            num = int(num_str)
            # Heuristic for years: a 4-digit number between 1000 and 2999
            if len(num_str) == 4 and 1500 <= num <= 2999:
                return num2words(num, to='year', lang='en')
            # For all other numbers
            else:
                return num2words(num, lang='en')
        except ValueError:
            return num_str

    # Use re.sub with a function to process each found number
    text = re.sub(r'\d+', number_replacer, text)
    
    # Step 4: Replace dashes and colons with a single space, and symbols with their English spelling
    text = text.replace('-', ' ')
    text = text.replace(':', ' ')
    text = text.replace('%', ' percent')
    text = text.replace('&', 'and')

    # Step 5: Remove all remaining punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)

    # Step 6: Remove any characters that are not basic English letters or spaces
    text = re.sub(r'[^a-z ]+', '', text)
    
    # Step 7: Normalize whitespace (e.g., multiple spaces to a single one)
    text = re.sub(r'\s+', ' ', text)

    # Step 8: Strip any leading/trailing whitespace
    return text.strip()
