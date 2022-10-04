from django.http import JsonResponse

import json
import occupations.api.find_occupation as find_occupation

def index(request):
    occupation_response = process_data(request)
    return JsonResponse(occupation_response)

def process_data(request):
    jsonResponse = json.loads(request.body.decode("utf-8"))
    try:
        occupation = find_occupation.find(jsonResponse["occupation"], jsonResponse["type_of_match"])
    except KeyError:
        occupation = {"error": "Fields are invalid"}
    return occupation