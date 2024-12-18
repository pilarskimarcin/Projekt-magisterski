# -*- coding: utf-8 -*-
import os
import pandas as pd
import unittest
from typing import Dict, Tuple

import utilities


def CreateSampleDataFrameWithPlacesCoordinates() -> pd.DataFrame:
    return pd.DataFrame([[None, None]], columns=["adres", "współrzędne"], index=[1])


def CreateSampleAddressHospital() -> utilities.PlaceAddress:
    return utilities.PlaceAddress(
        "Topolowa", "16", "32-500", "Chrzanów"
    )


def CreateSampleAddressHospital2() -> utilities.PlaceAddress:
    return utilities.PlaceAddress(
        "Wysokie Brzegi", "4", "32-600", "Oświęcim"
    )


def CreateSampleDistanceAndDurationData() -> Tuple[float, float]:
    return 1.53, 2.7


def CreateSampleCoordinates() -> Tuple[float, float]:
    return 50.136, 19.42863


def CreateSampleAddressIncident() -> utilities.PlaceAddress:
    return utilities.PlaceAddress(
        "Magnoliowa", "10", "32-500", "Chrzanów"
    )


def SampleMultiplePartsAddress() -> str:
    return "30 Maja 1960r. 9B 65-072 Zielona Góra"


class TestPlaceAddress(unittest.TestCase):
    sample_address: utilities.PlaceAddress

    def setUp(self):
        self.sample_address = CreateSampleAddressHospital()

    def testInit(self):
        sample_latitude, sample_longitude = CreateSampleCoordinates()

        self.assertEqual(self.sample_address.address_for_api_requests, "Topolowa 16, 32-500 Chrzanów")
        self.assertAlmostEqual(self.sample_address.latitude, sample_latitude, delta=0.0015)
        self.assertAlmostEqual(self.sample_address.longitude, sample_longitude, delta=0.015)

    def testEquality(self):
        sample_address: utilities.PlaceAddress = CreateSampleAddressHospital()

        self.assertEqual(sample_address == self.sample_address, True)

    def testInequalityPartOfAddress(self):
        sample_address: utilities.PlaceAddress = CreateSampleAddressIncident()

        self.assertNotEqual(self.sample_address, sample_address)

    def testInequalityCoordinates(self):
        sample_address: utilities.PlaceAddress = CreateSampleAddressHospital()
        sample_address.longitude = 7.5

        self.assertNotEqual(self.sample_address, sample_address)

    def testFromString(self):
        sample_address_string: str = "Topolowa 16 32-500 Chrzanów"

        self.assertEqual(utilities.PlaceAddress.FromString(sample_address_string), self.sample_address)

    def testDivideAddressIntoParts(self):
        sample_address_parts: Tuple[str, str, str, str] = ("30 Maja 1960r.", "9B", "65-072", "Zielona Góra")

        self.assertEqual(
            utilities.PlaceAddress.DivideAddressIntoParts(SampleMultiplePartsAddress()),
            sample_address_parts
        )

    def testDivideAddressIntoPartsInvalidAddress(self):
        self.assertRaises(
            ValueError,
            utilities.PlaceAddress.DivideAddressIntoParts, "18 Listopada 1989 16 32 700 Tarnowskie Góry"
        )

    def testGeocodingIsAlreadyInFile(self):
        sample_latitude, sample_longitude = CreateSampleCoordinates()
        self.RemoveLatitudeAndLongitudeFromSampleAddress()
        with open(utilities.PLACES_CSV_FILE, encoding="utf-8") as f1:
            file1 = f1.read()
        self.sample_address.Geocoding()
        with open(utilities.PLACES_CSV_FILE, encoding="utf-8") as f2:
            file2 = f2.read()

        self.assertEqual(file1, file2)
        self.assertAlmostEqual(self.sample_address.latitude, sample_latitude, delta=0.0015)
        self.assertAlmostEqual(self.sample_address.longitude, sample_longitude, delta=0.015)

    # def testGeocodingAddressNotInFile(self):
    #     # TODO0 usunąć ostatni w pliku adres, zapamiętać współrzędne, utworzyć obiekt, geocoding powinien przywrócić
    #     #  taki sam stan pliku i dobre współrzędne z API wyciągnąć

    def testGeocodingAlreadyGeocoded(self):
        sample_latitude, sample_longitude = CreateSampleCoordinates()
        with open(utilities.PLACES_CSV_FILE, encoding="utf-8") as f1:
            file1 = f1.read()
        self.sample_address.Geocoding()
        with open(utilities.PLACES_CSV_FILE, encoding="utf-8") as f2:
            file2 = f2.read()

        self.assertEqual(file1, file2)
        self.assertAlmostEqual(self.sample_address.latitude, sample_latitude, delta=0.0015)
        self.assertAlmostEqual(self.sample_address.longitude, sample_longitude, delta=0.015)

    def RemoveLatitudeAndLongitudeFromSampleAddress(self):
        self.sample_address.longitude = self.sample_address.latitude = None

    def testAreCoordinatesSavedInDataFrameTrue(self):
        places_coordinates_df: pd.DataFrame = pd.read_csv(utilities.PLACES_CSV_FILE, header=0, index_col=0)

        self.assertEqual(self.sample_address.AreCoordinatesSavedInDataFrame(places_coordinates_df), True)

    def testAreCoordinatesSavedInDataFrameFalse(self):
        places_coordinates_df: pd.DataFrame = CreateSampleDataFrameWithPlacesCoordinates()

        self.assertEqual(self.sample_address.AreCoordinatesSavedInDataFrame(places_coordinates_df), False)

    def testReadCoordinatesFromDataFrame(self):
        self.sample_address.ReadCoordinatesFromDataFrame()
        sample_latitude, sample_longitude = CreateSampleCoordinates()

        self.assertAlmostEqual(self.sample_address.latitude, sample_latitude, delta=0.0015)
        self.assertAlmostEqual(self.sample_address.longitude, sample_longitude, delta=0.015)

    def testReadCoordinatesFromDataFrameRaiseError(self):
        sample_dataframe_without_address: pd.DataFrame = CreateSampleDataFrameWithPlacesCoordinates()

        self.assertRaises(
            RuntimeError,
            self.sample_address.ReadCoordinatesFromDataFrame, sample_dataframe_without_address
        )

    def testGeocodeUsingAPI(self):
        self.RemoveLatitudeAndLongitudeFromSampleAddress()
        self.sample_address.GeocodeUsingAPI()
        sample_latitude, sample_longitude = CreateSampleCoordinates()

        self.assertAlmostEqual(self.sample_address.latitude, sample_latitude, delta=0.0015)
        self.assertAlmostEqual(self.sample_address.longitude, sample_longitude, delta=0.015)

    def testSavePlaceCoordinatesToFileNoCoordinates(self):
        with open(utilities.PLACES_CSV_FILE, encoding="utf-8") as f1:
            file1 = f1.read()
        self.RemoveLatitudeAndLongitudeFromSampleAddress()
        self.sample_address.SavePlaceCoordinatesToFile()
        with open(utilities.PLACES_CSV_FILE, encoding="utf-8") as f2:
            file2 = f2.read()

        self.assertEqual(file1, file2)

    def testSavePlaceCoordinatesToFileExistingRecord(self):
        with open(utilities.PLACES_CSV_FILE, encoding="utf-8") as f1:
            file1 = f1.read()
        self.sample_address.SavePlaceCoordinatesToFile()
        with open(utilities.PLACES_CSV_FILE, encoding="utf-8") as f2:
            file2 = f2.read()

        self.assertEqual(file1, file2)

    def testSavePlaceCoordinatesToFileNewRecord(self):
        sample_file: str = "test.csv"
        self.sample_address.longitude = 19.43
        self.sample_address.latitude = 50.14
        CreateSampleDataFrameWithPlacesCoordinates().to_csv(sample_file)
        self.sample_address.SavePlaceCoordinatesToFile(sample_file)
        sample_dataframe: pd.DataFrame = pd.read_csv(sample_file)

        self.assertTrue(self.sample_address.AreCoordinatesSavedInDataFrame(sample_dataframe))
        os.remove(sample_file)

    def testAreCoordinatesPresentNoCoordinates(self):
        self.RemoveLatitudeAndLongitudeFromSampleAddress()

        self.assertEqual(self.sample_address.AreCoordinatesPresent(), False)

    def testAreCoordinatesPresentOnlyOnePresent(self):
        self.sample_address.longitude = None

        self.assertEqual(self.sample_address.AreCoordinatesPresent(), False)

    def testAreCoordinatesPresentBothPresent(self):
        self.sample_address.longitude = 19.43
        self.sample_address.latitude = 50.14

        self.assertEqual(self.sample_address.AreCoordinatesPresent(), True)

    def testGetDistanceAndDurationToOtherPlace(self):
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressIncident()
        sample_distance, sample_duration = CreateSampleDistanceAndDurationData()
        results = self.sample_address.GetDistanceAndDurationToOtherPlace(sample_address_2)

        self.assertAlmostEqual(results[0], sample_distance, delta=0.1)
        self.assertAlmostEqual(results[1], sample_duration, delta=1)

    def testGetDistanceAndDurationToOtherPlaceSamePlace(self):
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressHospital()
        results = self.sample_address.GetDistanceAndDurationToOtherPlace(sample_address_2)

        self.assertAlmostEqual(results[0], 0)
        self.assertAlmostEqual(results[1], 0)

    def testGetDistanceAndDurationToOtherPlaceError(self):
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressHospital()
        self.RemoveLatitudeAndLongitudeFromSampleAddress()

        self.assertRaises(
            RuntimeError,
            self.sample_address.GetDistanceAndDurationToOtherPlace, sample_address_2
        )

    def testReadDistanceAndDurationFromFile(self):
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressIncident()
        sample_distance, sample_duration = CreateSampleDistanceAndDurationData()
        results = self.sample_address.ReadDistanceAndDurationFromFile(sample_address_2)

        self.assertAlmostEqual(results[0], sample_distance, delta=0.1)
        self.assertAlmostEqual(results[1], sample_duration, delta=0.1)

    def testReadDistanceAndDurationFromFileError(self):
        sample_address_2: utilities.PlaceAddress = utilities.PlaceAddress.FromString(SampleMultiplePartsAddress())

        self.assertIsNone(self.sample_address.ReadDistanceAndDurationFromFile(sample_address_2))

    def testCalculateDistanceAndDurationToOtherPlaceUsingAPI(self):
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressIncident()
        sample_distance, sample_duration = CreateSampleDistanceAndDurationData()
        results = self.sample_address.CalculateDistanceAndDurationToOtherPlaceUsingAPI(sample_address_2)

        self.assertAlmostEqual(results[0], sample_distance, delta=0.1)
        self.assertAlmostEqual(results[1], sample_duration, delta=1)

    def testSaveDistanceAndDurationToFileExistingRecord(self):
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressIncident()
        with open("../Dane/Odległości.json") as f1:
            file1 = f1.read()
        sample_distance, sample_duration = CreateSampleDistanceAndDurationData()
        self.sample_address.SaveDistanceAndDurationToFile(
            sample_distance, sample_duration, sample_address_2
        )
        with open("../Dane/Odległości.json") as f2:
            file2 = f2.read()

        self.assertEqual(file1, file2)

    def testSaveDistanceAndDurationToFileNewRecord(self):
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressIncident()
        sample_address_3: utilities.PlaceAddress = CreateSampleAddressHospital2()
        sample_filename: str = "test.json"
        sample_distance, sample_duration = CreateSampleDistanceAndDurationData()
        open(sample_filename, "w", encoding="utf-8").close()
        self.sample_address.SaveDistanceAndDurationToFile(
            sample_distance, sample_duration, sample_address_2, sample_filename
        )
        self.sample_address.SaveDistanceAndDurationToFile(
            sample_distance, sample_duration, sample_address_3, sample_filename
        )

        self.assertTrue(
            self.sample_address.IsDistanceAndDurationPresentInTheFile(
                sample_address_2, sample_filename
            )
        )
        self.assertTrue(
            self.sample_address.IsDistanceAndDurationPresentInTheFile(
                sample_address_3, sample_filename
            )
        )
        os.remove(sample_filename)

    def testIsDistancePresentInTheFile(self):
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressIncident()

        self.assertEqual(self.sample_address.IsDistanceAndDurationPresentInTheFile(sample_address_2), True)

    def testAddDistanceAndDurationToDictionary(self):
        sample_dictionary: Dict[str, Dict[str, Dict[str, float]]] = {
            self.sample_address.address_for_api_requests: {
                "sample address": {
                    "sample value": 1.0
                }
            }
        }
        sample_address_2: utilities.PlaceAddress = CreateSampleAddressIncident()
        sample_distance, sample_duration = CreateSampleDistanceAndDurationData()
        sample_dictionary_after_update: Dict[str, Dict[str, Dict[str, float]]] = {
            self.sample_address.address_for_api_requests: {
                "sample address": {
                    "sample value": 1.0
                },
                sample_address_2.address_for_api_requests: {
                    "odległość [km]": sample_distance,
                    "czas podróży [min]": sample_duration
                }
            }
        }

        self.assertEqual(
            self.sample_address.AddDistanceAndDurationToDictionary(
                sample_dictionary, sample_address_2, sample_distance, sample_duration
            ),
            sample_dictionary_after_update
        )


if __name__ == "__main__":
    unittest.main()
