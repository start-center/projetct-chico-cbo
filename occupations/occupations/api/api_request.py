import requests
from .utils import BASE_STRING_TO_FIND_SALARY, INEXISTENT_SALARY_MESSAGE

def make_request(url):
    response = requests.get(url)
    salary = extract_salary(response.text)

    return salary
  
def extract_salary(response_string):
    salary = ""
    found_salary = False
    # extract salary based on the html of the response
    for s in response_string.split("\n"):
        if not found_salary:
            if s.startswith(BASE_STRING_TO_FIND_SALARY):
                salary = split_string_to_get_salary(s)
                found_salary = True
                break
       
    if not found_salary:
        return INEXISTENT_SALARY_MESSAGE

    return salary

def split_string_to_get_salary(string):
    temp_string = string.split(">")
    temp_string = temp_string[1].split("<")

    return temp_string[0]