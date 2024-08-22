from __future__ import annotations
import csv
from dotenv import load_dotenv
import json
from os import getenv
import requests
from typing import Dict, List, Optional, Tuple

load_dotenv()


# Stałe
PLACES_CSV_FILE: str = "../Dane/Miejsca.csv"
PLACES_CSV_FILE_FIRST_ROW_NUMBER: int = 2
DISTANCES_JSON_FILE: str = "../Dane/Odległości.json"
DISTANCE_KEY: str = "odległość [km]"
DURATION_KEY: str = "czas podróży [min]"


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

    def CheckIfCoordinatesPresent(self, raise_error: bool = False):
        if not self.latitude or not self.longitude:
            if raise_error:
                raise RuntimeError("Współrzędne nie zostały jeszcze zakodowane, nie można zapisać")
            else:
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
        self.SaveDistanceToFile(distance, duration, other)
        return distance, duration

    def SaveDistanceToFile(
            self, distance: float, duration: float, other: PlaceAddress, target_json_file: Optional[str] = None
    ):
        """Funkcja zapisująca dane o dystansie między miejscami w pliku"""
        if not target_json_file:
            target_json_file = DISTANCES_JSON_FILE
        with (open(target_json_file, "r+") as file):
            file_contents: str = file.read()
            saved_distances: Dict[str, Dict[str, Dict[str, float]]] = {}
            if file_contents:
                saved_distances = json.loads(file_contents)
            for origin, info_for_origin in saved_distances.items():
                if origin == self.address:
                    for destination, info_for_origin_destination in info_for_origin.items():
                        if destination == other.address:
                            return
            saved_distances = self.AddDistanceAndDurationToDictionary(saved_distances, other, distance, duration)
            saved_distances[self.address][other.address][DISTANCE_KEY] = distance
            saved_distances[self.address][other.address][DURATION_KEY] = duration
            file.seek(0)
            file.truncate()
            json.dump(saved_distances, file, ensure_ascii=False, indent=2)

    def AddDistanceAndDurationToDictionary(
            self, dictionary: Dict[str, Dict[str, Dict[str, float]]], other: PlaceAddress, distance: float,
            duration: float
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        other_distance_duration_dict: Dict[str, Dict[str, float]] = {other.address: {
            DISTANCE_KEY: distance, DURATION_KEY: duration}
        }
        dictionary[self.address] = other_distance_duration_dict
        return dictionary

