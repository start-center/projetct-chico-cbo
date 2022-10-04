import unidecode
from .utils import API_BASE_URL, PUNCTUATION

def assemble_key_for_maping(key):
    # remove blank spaces and turn lower case
    temp_key = key.replace(" ", "").lower()
    # remove accent and other special characters
    temp_key = unidecode.unidecode(temp_key)
    # remove punctuation
    for c in PUNCTUATION:
        temp_key = temp_key.replace(c, "")

    return temp_key

def assemble_api_string(string, cbo_code):
    # trim string
    temp_string = string.strip()
    # remove accent and other special characters
    temp_string = unidecode.unidecode(temp_string)
    # remove punctuation
    for c in PUNCTUATION:
        temp_string = temp_string.replace(c, "")
    # change blank spaces for "-" and turn lower case
    temp_string = temp_string.replace(" ", "-").lower()
    # add cbo code
    temp_string = temp_string + "-cbo-" + str(cbo_code)
    # add url
    api_string = API_BASE_URL + temp_string

    return api_string