from __future__ import annotations
from dotenv import load_dotenv
import json
from os import getenv
import pandas as pd
import re
import requests
from typing import Dict, List, Optional, Tuple

load_dotenv()

# Stałe
PLACES_CSV_FILE: str = "../Dane/Miejsca.csv"
PLACES_CSV_FILE_FIRST_ROW_NUMBER: int = 2
PLACES_CSV_FILE_ADDRESS_COLUMN_NAME: str = "adres"
PLACES_CSV_COORDINATES_COLUMN_NAME: str = "współrzędne"
DISTANCES_JSON_FILE: str = "../Dane/Odległości.json"
DISTANCE_KEY: str = "odległość [km]"
DURATION_KEY: str = "czas podróży [min]"


class PlaceAddress:
    address_for_api_requests: str
    address_for_places_data: str
    latitude: Optional[float]
    longitude: Optional[float]

    def __init__(self, street: str, number: str, postal_code: str, city: str,
                 latitude: Optional[float] = None, longitude: Optional[float] = None):
        address_first_part: str = " ".join([street, str(number)])
        address_second_part: str = " ".join([postal_code, city])
        self.address_for_api_requests = ", ".join([address_first_part, address_second_part])
        self.address_for_places_data = " ".join([address_first_part, address_second_part])
        self.latitude = latitude
        self.longitude = longitude
        if latitude is None or longitude is None:
            self.Geocoding()

    def __eq__(self, other):
        if not isinstance(other, PlaceAddress):
            return False
        return vars(self) == vars(other)

    @classmethod
    def FromString(cls, address_string: str) -> PlaceAddress:
        address_parts: Tuple[str, str, str, str] = cls.DivideAddressIntoParts(address_string)
        return PlaceAddress(
            street=address_parts[0], number=address_parts[1], postal_code=address_parts[2], city=address_parts[3]
        )

    @staticmethod
    def DivideAddressIntoParts(address_string: str) -> Tuple[str, str, str, str]:
        address_parts: List[str] = address_string.split()
        for i, address_part in enumerate(address_parts):
            if i < 1:
                continue
            if re.match(r"[0-9]{2}-[0-9]{3}", address_part) is not None:
                street: str = " ".join(address_parts[:(i - 1)])
                number: str = address_parts[i - 1]
                postal_code: str = address_part
                city: str = " ".join(address_parts[(i + 1):])
                return street, number, postal_code, city
        raise ValueError("Argument nie jest adresem")

    def Geocoding(self):
        """Funkcja kodująca adres na współrzędne geograficzne"""
        if self.longitude and self.latitude:
            return
        if self.AreCoordinatesSavedInDataFrame():
            self.ReadCoordinatesFromDataFrame()
            return
        url = "https://trueway-geocoding.p.rapidapi.com/Geocode"
        querystring = {"address": self.address_for_api_requests, "language": "pl", "country": "pl"}
        headers = {"x-rapidapi-key": getenv("XRAPID_API_KEY"), "x-rapidapi-host": "trueway-geocoding.p.rapidapi.com"}
        response = requests.get(url, headers=headers, params=querystring).json()
        coordinates = response["results"][0]["location"]
        self.latitude = coordinates["lat"]
        self.longitude = coordinates["lng"]
        self.SavePlaceCoordinatesToFile()

    def AreCoordinatesSavedInDataFrame(self, places_coordinates_df: Optional[pd.DataFrame] = None) -> bool:
        if places_coordinates_df is None:
            places_coordinates_df = pd.read_csv(
                PLACES_CSV_FILE, header=0, index_col=0, encoding="utf-8"
            )
        return self.address_for_api_requests in places_coordinates_df[PLACES_CSV_FILE_ADDRESS_COLUMN_NAME].values

    def ReadCoordinatesFromDataFrame(self, places_coordinates_df: Optional[pd.DataFrame] = None):
        if places_coordinates_df is None:
            places_coordinates_df = pd.read_csv(
                PLACES_CSV_FILE, header=0, index_col=0, encoding="utf-8"
            )
        if not self.AreCoordinatesSavedInDataFrame(places_coordinates_df):
            raise RuntimeError("Współrzędne nie są zapisane w tym DataFrame")
        this_address_row: pd.Series = places_coordinates_df.loc[
            places_coordinates_df[PLACES_CSV_FILE_ADDRESS_COLUMN_NAME] == self.address_for_api_requests
            ]
        coordinates: str = this_address_row.loc[:, PLACES_CSV_COORDINATES_COLUMN_NAME].values[0]
        self.latitude, self.longitude = [float(coordinate) for coordinate in coordinates.split(",")]

    def SavePlaceCoordinatesToFile(self, target_csv_file: str = PLACES_CSV_FILE):
        if not self.AreCoordinatesPresent():
            return
        places_coordinates_df: pd.DataFrame = pd.read_csv(
            target_csv_file, header=0, index_col=0, encoding="utf-8"
        )
        if not self.AreCoordinatesSavedInDataFrame(places_coordinates_df):
            places_coordinates_df.loc[len(places_coordinates_df.index) + 1] = [
                self.address_for_api_requests, ",".join([str(self.latitude), str(self.longitude)])
            ]
            places_coordinates_df.to_csv(target_csv_file, header=True, index_label="Lp.", encoding="utf-8")

    def AreCoordinatesPresent(self) -> bool:
        if not self.latitude or not self.longitude:
            return False
        return True

    def DistanceAndDurationToOtherPlace(self, other: PlaceAddress) -> Tuple[float, float]:
        """Funkcja obliczająca dystans w kilometrach i czas w minutach między dwoma miejscami"""
        if not self.AreCoordinatesPresent() or not other.AreCoordinatesPresent():
            raise RuntimeError("Współrzędne nie zostały jeszcze zakodowane, nie można obliczyć odległości")
        saved_distance_and_duration: Optional[Tuple[float, float]] = self.ReadDistanceAndDurationFromFile(other)
        if saved_distance_and_duration:
            return saved_distance_and_duration
        url = "https://trueway-matrix.p.rapidapi.com/CalculateDrivingMatrix"
        querystring = {"origins": f"{str(self.latitude)},{str(self.longitude)}",
                       "destinations": f"{str(other.latitude)},{str(other.longitude)}"}
        headers = {"X-RapidAPI-key": getenv("XRAPID_API_KEY"), "X-RapidAPI-Host": "trueway-matrix.p.rapidapi.com"}
        response = requests.get(url, headers=headers, params=querystring).json()
        origin_index: int = 0
        destination_index: int = 0
        distance: float = response["distances"][origin_index][destination_index] / 1000
        duration: float = response["durations"][origin_index][destination_index] / 60
        self.SaveDistanceAndDurationToFile(distance, duration, other)
        return distance, duration

    def ReadDistanceAndDurationFromFile(self, other_place: PlaceAddress, filename: str = DISTANCES_JSON_FILE) \
            -> Optional[Tuple[float, float]]:
        with open(filename, "r", encoding="utf-8") as file:
            file_contents: str = file.read()
        if not file_contents:
            return None
        saved_distances: Dict[str, Dict[str, Dict[str, float]]] = json.loads(file_contents)
        for origin, info_for_origin in saved_distances.items():
            if origin == self.address_for_api_requests:
                for destination, info_for_origin_destination in info_for_origin.items():
                    if destination == other_place.address_for_api_requests:
                        return info_for_origin_destination[DISTANCE_KEY], info_for_origin_destination[DURATION_KEY]
        return None

    def SaveDistanceAndDurationToFile(
            self, distance: float, duration: float, other: PlaceAddress, target_json_file: str = DISTANCES_JSON_FILE
    ):
        if self.IsDistanceAndDurationPresentInTheFile(other, target_json_file):
            return
        with (open(target_json_file, "r+", encoding="utf-8") as file):
            file_contents: str = file.read()
            saved_distances: Dict[str, Dict[str, Dict[str, float]]] = {}
            if file_contents:
                saved_distances = json.loads(file_contents)
            saved_distances = self.AddDistanceAndDurationToDictionary(saved_distances, other, distance, duration)
            file.seek(0)
            file.truncate()
            json.dump(saved_distances, file, ensure_ascii=False, indent=2)

    def IsDistanceAndDurationPresentInTheFile(self, other_place: PlaceAddress,
                                              filename: str = DISTANCES_JSON_FILE) -> bool:
        return self.ReadDistanceAndDurationFromFile(other_place, filename) is not None

    def AddDistanceAndDurationToDictionary(
            self, dictionary: Dict[str, Dict[str, Dict[str, float]]], other: PlaceAddress, distance: float,
            duration: float
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        other_distance_duration_dict: Dict[str, Dict[str, float]] = {
            other.address_for_api_requests: {
                DISTANCE_KEY: distance, DURATION_KEY: duration
            }
        }
        if self.address_for_api_requests in dictionary.keys():
            dictionary[self.address_for_api_requests].update(other_distance_duration_dict)
        else:
            dictionary[self.address_for_api_requests] = other_distance_duration_dict
        return dictionary


class TargetDestination:
    address: PlaceAddress

    def __init__(self, address: PlaceAddress):
        self.address = address
