import os
import pandas as pd
import unidecode
from fuzzywuzzy import process, fuzz
from .utils import PUNCTUATION, INEXISTENT_SALARY_MESSAGE
from .binary_search import binary_search
from .api_request import make_request
from .assemble_strings import assemble_key_for_maping, assemble_api_string

OCCUPATIONS = {}
OCCUPATIONS_FUZZY = {}
OCCUPATIONS_FUZZY_CBO_INDEX = {}
BIG_GROUPS = {}
MAIN_SUB_GROUPS = {}
SUB_GROUPS = {}
FAMILIES = {}

def find(occupation, type_of_match):
    generate_occupation_groups_dicts()
    # check if the occupation is already the cbo
    if str(occupation).isdigit():
        cbo_code = str(occupation)
        occupation_found = get_occupation_by_cbo(cbo_code)
        if occupation_found == "":
            cbo_code = None
    else:
        cbo_code, occupation_found = get_cbo_and_closest_occupation(occupation, type_of_match)

    occupation_salary = get_occupation_salary(occupation_found, cbo_code)
    occupation_groups = get_occupation_groups(cbo_code)
    occupation_response = {
        "requested_occupation": occupation,
        "occupation_found": occupation_found,
        "cbo_code": cbo_code,
        "salary": occupation_salary,
        "big_group": occupation_groups[0],
        "main_sub_group": occupation_groups[1],
        "sub_group": occupation_groups[2],
        "family": occupation_groups[3],
    }

    return occupation_response

def read_data(path):
    return pd.read_csv(os.path.join(os.getcwd(), path), delimiter=";", encoding="ISO-8859-9")

def generate_occupation_groups_dicts():
    global OCCUPATIONS
    global OCCUPATIONS_FUZZY
    global OCCUPATIONS_FUZZY_CBO_INDEX
    global BIG_GROUPS
    global MAIN_SUB_GROUPS
    global SUB_GROUPS
    global FAMILIES
    if OCCUPATIONS == {}:
        df = read_data("occupations/api/data/CBO2002 - Sinonimo.csv")
        OCCUPATIONS = generate_occupations_hash_table(df["TITULO"], df["CODIGO"])
        OCCUPATIONS_FUZZY = {key: value for key, value in enumerate(df["TITULO"])}
        OCCUPATIONS_FUZZY_CBO_INDEX = {key: value for key, value in enumerate(df["CODIGO"])}

        df = read_data("occupations/api/data/CBO2002 - Grande Grupo.csv")
        BIG_GROUPS = generate_group_hash_table(df["CODIGO"], df["TITULO"])

        df = read_data("occupations/api/data/CBO2002 - SubGrupo Principal.csv")
        MAIN_SUB_GROUPS = generate_group_hash_table(df["CODIGO"], df["TITULO"])

        df = read_data("occupations/api/data/CBO2002 - SubGrupo.csv")
        SUB_GROUPS = generate_group_hash_table(df["CODIGO"], df["TITULO"])

        df = read_data("occupations/api/data/CBO2002 - Familia.csv")
        FAMILIES = generate_group_hash_table(df["CODIGO"], df["TITULO"])

def get_occupation_by_cbo(cbo_code):
    global OCCUPATIONS_FUZZY
    df = read_data("occupations/api/data/CBO2002 - Sinonimo.csv")
    index_of_occupation = binary_search(df["CODIGO"], int(cbo_code))
    if index_of_occupation == -1:
        return ""
        
    return OCCUPATIONS_FUZZY[index_of_occupation]

def get_cbo_and_closest_occupation(occupation, type_of_match):
    global OCCUPATIONS
    global OCCUPATIONS_FUZZY_CBO_INDEX
    if type_of_match == "exact":
        closest_occupation_found = occupation
        key_to_find = assemble_key_for_maping(occupation)
        try:
            cbo_code = str(OCCUPATIONS[key_to_find])
        except KeyError:
            cbo_code = None
    else:
        result = process.extract(occupation, OCCUPATIONS_FUZZY, limit=1, scorer=fuzz.ratio)
        closest_occupation_found = result[0][0]
        index_of_cbo = result[0][2]
        cbo_code = str(OCCUPATIONS_FUZZY_CBO_INDEX[index_of_cbo])

    return cbo_code, closest_occupation_found

def get_occupation_salary(occupation, cbo_code):
    if cbo_code == None:
        return INEXISTENT_SALARY_MESSAGE
    # generate api string
    api_string = assemble_api_string(occupation, cbo_code)
    # api request
    occupation_salary = make_request(api_string)

    return occupation_salary

def get_occupation_groups(cbo_code):
    if cbo_code == None:
        return 4 * [""]
    elif len(cbo_code) == 5:
        cbo_code = "0" + cbo_code

    big_group = BIG_GROUPS[int(cbo_code[:1])]
    main_sub_group = MAIN_SUB_GROUPS[int(cbo_code[:2])]
    sub_group = SUB_GROUPS[int(cbo_code[:3])]
    family = FAMILIES[int(cbo_code[:4])]

    return [big_group, main_sub_group, sub_group, family]

def generate_occupations_hash_table(keys, values):
    global PUNCTUATION
    # remove blank spaces and turn lower case
    keys_without_blank_space = [key.replace(" ", "").lower() for key in keys]
    # remove punctuation, accent and other special characters
    keys_without_punctuation = []
    for key in keys_without_blank_space:
        temp_key = unidecode.unidecode(key)
        for c in PUNCTUATION:
            temp_key = temp_key.replace(c, "")
        keys_without_punctuation.append(temp_key)

    hash_table = dict(zip(keys_without_punctuation, values))

    del keys_without_blank_space[:]
    del keys_without_punctuation[:]

    return hash_table

def generate_group_hash_table(keys, values):
    # trim values
    temp_values = [value.strip() for value in values]
    return dict(zip(keys, temp_values))
