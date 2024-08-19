from __future__ import annotations

import csv

from dotenv import load_dotenv
import json
from os import getenv
import requests
from typing import List, Optional, Tuple

load_dotenv()


# Stałe
PLACES_CSV_FILE: str = "../Dane/Miejsca.csv"
PLACES_CSV_FILE_FIRST_ROW_NUMBER: int = 2


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
        self.SavePlaceToFile()

    def SavePlaceToFile(self, target_csv_file: Optional[str] = None):
        """Funkcja zapisująca dane o miejscu do pliku, jeśli nie są jeszcze zapisane"""
        if not target_csv_file:
            target_csv_file = PLACES_CSV_FILE
        self.CheckIfCoordinatesPresent()
        with open(target_csv_file, "r+") as csv_file:
            places_csv_file = csv.reader(csv_file)
            last_place_id: int = 0
            for row in places_csv_file:
                if places_csv_file.line_num < PLACES_CSV_FILE_FIRST_ROW_NUMBER:
                    continue
                if row == "":
                    break
                last_place_id = int(row[0])
                if row[1] == self.address:
                    return
            csv_file.write("\n")
            csv.writer(csv_file).writerow(
                [last_place_id + 1, self.address, ";".join([str(self.latitude), str(self.longitude)])]
            )

    def CheckIfCoordinatesPresent(self):
        if not self.latitude or not self.longitude:
            self.Geocoding()

    def DistanceFromOtherPlace(self, other: PlaceAddress) -> Tuple[float, float]:
        """Funkcja obliczająca dystans w kilometrach i czas w minutach między dwoma miejscami"""
        self.CheckIfCoordinatesPresent()
        other.CheckIfCoordinatesPresent()
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

    def SaveDistanceToFile(self, distance: float, duration: float):
        """Funkcja zapisująca dane o dystansie między miejscami w pliku"""
        # TODO: JSON - od origin do destination - trzeba załadować najpierw jako słownik i zobaczyć czy już takie jest
        pass
