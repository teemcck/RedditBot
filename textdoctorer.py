import regex as re

# List of corrected abbreviations
replacements = {
    "AITA": "Am I the a-hole",
    "AITA?": "Am I the a-hole?",
    "AITAH": "Am I the a-hole",
    "AITAH?": "Am I the a-hole?",
    "AH": "a-hole",
    "ATA": "am the a-hole",
    "WIBTA": "Would I be the a-hole",
    "WIBTAH": "Would I be the a-hole",
    "BC": "because",
    "IL": "in law",
    "ILs": "in laws",
    "MIL": "mother in law",
    "ML": "mother in law",
    "FIL": "father in law",
    "FL": "father in law",
    "SIL": "sister in law",
    "SL": "sister in law",
    "BIL": "brother in law",
    "BL": "brother in law",
    "MTF": "male transitioned female",
    "FTM": "female transitioned male",
    "AFAIK": "as far as I know",
    "AMA": "Ask me anything",
    "AMAA": "Ask me almost anything",
    "CMV": "change my view",
    "DM;HS": "it doesn't matter had intercourse",
    "DMHS": "it doesn't matter had intercourse",
    "ELI5": "explain like I'm 5",
    "FTFY": "fixed that for you",
    "FT4Y": "fix that for you",
    "FTFU": "fixed that for you",
    "FT4U": "fixed that for you",
    "IANAD": "I am not a doctor",
    "IANAL": "I am not a lawyer",
    "IMHO": "in my honest opinion",
    "ITT": "in this thread",
    "NSFL": "not safe for life",
    "NSFW": "not safe for work",
    "TIL": "today I learned",
    "TIFU": "Today I f'ed up",
    "TIFU -": "Today I f'ed up",
    "YSK": "you should know",
    "USK": "you should know",
    "YMMV": "your mileage may vary",
    "OP": "original poster",
    "OC": "original content",
    "DAE": "does anyone else",
    "IIRC": "if I recall correctly",
    "LPT": "life pro tip",
    "S/O": "significant other",
    "PSA": "Public Service Announcement",
    "GTFO": "get the eff out",
    "IRL": "in real life",
    "DIAF": "die in a fire",
    "IAMA": "I am a",
    "RN": "right now",
    "ATM": "at the moment",
    "TBM": "to be honest",
    "TMI": "too much information",
    "IDK": "I don't know",
    "IKR": "I know right",
    "HTH": "hope this helps",
    "LTR": "later",
    "L8R": "later",
    "LMK": "let me know",
    "SAHM": "stay-at-home mom",
    "SRS": "serious",
    "DEA": "Does anybody else",
    "AP": "affair partner",
    "w/": "with",
    "w/o": "without",
    "b/c": "because",
    "m/f": "male/female",
    "t/f": "true/false",
    "w/in": "within",
    "w/o ": "without ",
    "approx": "approximately",
    "AIW": "Am I wrong?",
    "MC": "Malicious compliance",
    "bf": "boyfriend",
    "gf": "girlfriend"
}

bugged_texts = {
    "x200B": "",
    "x200B;": "",
    "x200b": "",
    "&x200b": "",
    "x200b;": "",
    "&x200B": "",
    "x200B;": "",
    "&x200b;": "",
    "&x200B;": "",
    "&#": "",
    "&#;": "",
    "^1": "",
    "&nbsp;": ""
}

def unabbreviate(text):
    """
    Replaces specific series of characters in a text.

    Args:
        text (str): The text to be processed.

    Returns:
        str: The processed text with removed abbreviations.
    """
    try:
        # Remove all new line characters
        text = text.replace(" \n", "")
        text = text.replace("\n", " ")

        # Replace abbreviations
        for abbreviation, unabbreviated in replacements.items():
            # Add word boundary checks to the replacement term
            pattern = r"\b" + re.escape(abbreviation) + r"\b"
            text = re.sub(pattern, unabbreviated, text, flags=re.IGNORECASE)

        # Remove gender abbreviations in various formats
        # 1. Gender abbreviations within parentheses, brackets, or braces even if adjacent to text
        text = re.sub(r"[\(\[{]\d{1,2}[MFmfSs][\]\)}]", "", text)

        # 2. Gender abbreviations surrounded by spaces or at the beginning/end of the string
        text = re.sub(r"\b[MFmfSs]\d{1,2}\b", "", text)

        # 3. Gender abbreviations with potential punctuation at the end
        text = re.sub(r"\b[MFmfSs]\d{1,2}[/\\]?[\(\)\[\]{}\"\']?\b", "", text)

        # 4. Remove numbers followed by characters within parentheses, brackets, or braces
        text = re.sub(r"[\(\[{]\d+[MFmfSs][\)\]}]", "", text)

        # 5. Remove numbers followed by characters surrounded by spaces or at the beginning/end of the string
        text = re.sub(r"\b\d+[MFmfSs]\b", "", text)

        # 6. Year old abbreviation
        text = re.sub(r"\b\d{1,2}yo\b", "", text)

        # Remove any standalone or text-adjacent empty parentheses, brackets, or braces
        text = re.sub(r"\(\s*\)|\[\s*\]|\{\s*\}", "", text)
        text = re.sub(r"[^\s\w]\[\s*\]|\[\s*\][^\s\w]", "", text)

        # Remove any extra spaces left after the replacements
        text = re.sub(r'\s{2,}', ' ', text).strip()

        # Replace specific buggy texts
        for bugged_text, replacement in bugged_texts.items():
            text = text.replace(bugged_text, replacement)

        return text
    except Exception as e:
        print(f"Error in unabbreviate function: {e}")
    
def remove_keywords(text):
    # Define keywords to search for
    keywords = ['edit', 'tldr', 'tl;dr', 'tl:dr', 'update']

    # Create a regular expression pattern to match any of the keywords
    pattern = '|'.join(map(re.escape, keywords))

    # Use regex to find the first occurrence of any of the keywords
    match = re.search(pattern, text, flags=re.IGNORECASE)

    # If a match is found, return the text up until that point, else return the original text
    if match:
        text = text[:match.start()].strip()
        return text, len(text)
    else:
        return text, len(text)
    
def fixperiods(content):
    fixed_content = ''
    for i in range(len(content) - 1):
        if content[i] == '.' and content[i + 1] != ' ':
            fixed_content += '. '
        else:
            fixed_content += content[i]
    # Add the last character
    fixed_content += content[-1]
    return fixed_content