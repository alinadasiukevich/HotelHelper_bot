import os
import requests
from dotenv import load_dotenv


load_dotenv()
url_locations = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_properties = "https://hotels4.p.rapidapi.com/properties/list"
url_get_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
headers = {
                'x-rapidapi-host': os.getenv('host_api'),
                'x-rapidapi-key': os.getenv('key_api')
            }
def request_to_api(url, headers, querystring):

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            return response
        else:
            response.raise_for_status()
    except requests.Timeout:
        print('Превышено время ожидания')
    except requests.HTTPError as err:
        code = err.response.status_code
        print(f"Ошибка url: {url}, code: {code}")

# def get_location(querystring):
#     response = requests.request("GET", url_locations, headers=headers, params=querystring, timeout=20)
#     if response.status_code == requests.codes.ok:
#         return response
#     else:
#         response.raise_for_status()
#
#
# def get_properties(querystring):
#     response = requests.request("GET", url_properties, headers=headers, params=querystring, timeout=20)
#     if response.status_code == requests.codes.ok:
#         return response
#     else:
#         response.raise_for_status()
#
#
# def get_photos(querystring):
#     response = requests.request("GET", url_get_photos, headers=headers, params=querystring, timeout=20)
#     if response.status_code == requests.codes.ok:
#         return response
#     else:
#         response.raise_for_status()
