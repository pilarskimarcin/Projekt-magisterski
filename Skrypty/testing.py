import requests
from typing import Dict
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# GOOGLE MAPS
# # importing googlemaps module
# import googlemaps
#
# # Requires API key
# gmaps = googlemaps.Client(key=getenv("GOOGLE_API_KEY"))
#
# # Requires cities name
# my_dist = gmaps.distance_matrix('Rostafińskiego 2 Kraków', 'Kraków Bronowice')['rows'][0]['elements'][0]
#
# # Printing the result
# print(my_dist)

# # GEOCODING - Distancematrix.ai
# def geocoding(address: str) -> Dict[str, float]:
#     url = f"https://api.distancematrix.ai/maps/api/geocode/json?address={address}&" \
#           f"key={getenv('DISTANCE_MATRIX_AI_GEOCODING_KEY')}&language=pl"
#     response = requests.get(url).json()
#     coordinates = response["result"][0]["geometry"]["location"]
#     print(coordinates)
#     return coordinates

# TRUEWAY GEOCODING


def geocoding(address: str) -> Dict[str, float]:
    url = "https://trueway-geocoding.p.rapidapi.com/Geocode"
    querystring = {"address": address, "language": "pl", "country": "pl"}
    headers = {"x-rapidapi-key": getenv("XRAPID_API_KEY"), "x-rapidapi-host": "trueway-geocoding.p.rapidapi.com"}
    response = requests.get(url, headers=headers, params=querystring).json()
    coordinates = response["results"][0]["location"]
    print(coordinates)
    return coordinates


# TRUEWAY MATRIX
def distance_calculation(coordinates1: Dict[str, float], coordinates2: Dict[str, float]):
    url = "https://trueway-matrix.p.rapidapi.com/CalculateDrivingMatrix"
    querystring = {"origins": f"{str(coordinates1['lat'])},{str(coordinates1['lng'])}",
                   "destinations": f"{str(coordinates2['lat'])},{str(coordinates2['lng'])}"}
    headers = {"X-RapidAPI-key": getenv("XRAPID_API_KEY"), "X-RapidAPI-Host": "trueway-matrix.p.rapidapi.com"}
    response = requests.get(url, headers=headers, params=querystring).json()
    distances = [[el / 1000 for el in source] for source in response["distances"]]
    durations = [[el / 60 for el in source] for source in response["durations"]]
    print(distances, durations)


if __name__ == '__main__':
    coord1 = geocoding("Topolowa 16, 32-500 Chrzanów")
    coord2 = geocoding("Chrzanowska 6, 32-541 Trzebinia")
    distance_calculation(coord1, coord2)  # km, min
