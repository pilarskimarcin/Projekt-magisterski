from __future__ import annotations
from dotenv import load_dotenv
import json
from os import getenv
import requests
from typing import List, Optional, Tuple

load_dotenv()


class PlaceAddress:
    address: str
    latitude: Optional[float]
    longitude: Optional[float]

    def __init__(self, street: str, number: int, postal_code: str, city: str,
                 latitude: Optional[float] = None, longitude: Optional[float] = None):
        address_parts: List[str] = [street, " ", str(number), ", ", postal_code, " ", city]
        self.address = "".join(address_parts)
        self.latitude = latitude
        self.longitude = longitude

    def Geocoding(self):
        """Funkcja kodująca adres na współrzędne geograficzne"""
        url = "https://trueway-geocoding.p.rapidapi.com/Geocode"
        querystring = {"address": self.address, "language": "pl", "country": "pl"}
        headers = {"x-rapidapi-key": getenv("XRAPID_API_KEY"), "x-rapidapi-host": "trueway-geocoding.p.rapidapi.com"}
        response = requests.get(url, headers=headers, params=querystring).json()
        coordinates = response["results"][0]["location"]
        self.latitude = coordinates["lat"]
        self.longitude = coordinates["lng"]

    def DistanceFromOtherPlace(self, other: PlaceAddress) -> Tuple[float, float]:
        """Funkcja obliczająca dystans w kilometrach i czas w minutach między dwoma miejscami"""
        url = "https://trueway-matrix.p.rapidapi.com/CalculateDrivingMatrix"
        querystring = {"origins": f"{str(self.latitude)},{str(self.longitude)}",
                       "destinations": f"{str(other.latitude)},{str(other.longitude)}"}
        headers = {"X-RapidAPI-key": getenv("XRAPID_API_KEY"), "X-RapidAPI-Host": "trueway-matrix.p.rapidapi.com"}
        response = requests.get(url, headers=headers, params=querystring).json()
        origin_index: int = 0
        destination_index: int = 0
        distance: float = response["distances"][origin_index][destination_index] / 1000
        duration: float = response["durations"][origin_index][destination_index] / 60
        self.SaveDistanceToFile(distance, duration)
        return distance, duration

    def SavePlaceToFile(self):
        """Funkcja zapisująca dane o miejscu do pliku"""
        # TODO: Do .csv - kolumny id, adres, współrzędne
        #  jeśli nie współrzędne, geocoding
        #  odczytać plik i sprawdzić czy jest już taki adres (adres razem)
        raise NotImplementedError

    def SaveDistanceToFile(self, distance: float, duration: float):
        """Funkcja zapisująca dane o dystansie między miejscami w pliku"""
        # TODO: JSON - od origin do destination - trzeba załadować najpierw jako słownik i zobaczyć czy już takie jest
        raise NotImplementedError


# TODO: testy
if __name__ == '__main__':
    coord1 = geocoding("Topolowa 16, 32-500 Chrzanów")
    coord2 = geocoding("Chrzanowska 6, 32-541 Trzebinia")
    distance_calculation(coord1, coord2)  # km, min
