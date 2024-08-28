# -*- coding: utf-8 -*-
import os
import unittest
from typing import Callable

from Skrypty import utilities


class TestPlaceAddress(unittest.TestCase):

    def setUp(self):
        self.sample_address: utilities.PlaceAddress = utilities.PlaceAddress(
            "Topolowa", 16, "32-500", "Chrzanów"
        )

    def testInit(self):
        self.assertEqual(self.sample_address.address, "Topolowa 16, 32-500 Chrzanów")
        self.assertIsNone(self.sample_address.latitude)
        self.assertIsNone(self.sample_address.longitude)

    def testDistanceFromOtherPlaceAndSaveToFile(self):
        sample_address_2: utilities.PlaceAddress = utilities.PlaceAddress(
            "Chrzanowska",  6, "32-541", "Trzebinia"
        )
        with open("../Dane/Odległości.json") as f1:
            file1 = f1.read()
        sample_distance: float
        sample_duration: float
        sample_distance, sample_duration = self.sample_address.DistanceFromOtherPlace(sample_address_2)
        self.assertAlmostEqual(sample_distance, 9.891, delta=0.1)
        self.assertAlmostEqual(sample_duration, 13.27, delta=1)
        with open("../Dane/Odległości.json") as f2:
            file2 = f2.read()
        self.assertEqual(file1, file2)

        sample_file_name: str = "test.json"
        self.SavingToSampleFileAndTesting(
            sample_file_name, self.sample_address.SaveDistanceToFile,
            1.0, 1.0, sample_address_2, sample_file_name
        )

    def SavingToSampleFileAndTesting(self, sample_file_name: str, function_to_test: Callable, *args):
        file = open(sample_file_name, "w")
        file.close()
        function_to_test(*args)
        file = open(sample_file_name)
        self.assertIsNotNone(file)
        file.close()
        os.remove(sample_file_name)

    def testGeocodingAndSavePlaceToFile(self):
        with open("../Dane/Miejsca.csv") as f1:
            file1 = f1.read()
        self.sample_address.Geocoding()
        self.assertAlmostEqual(self.sample_address.latitude, 50.137109, delta=0.0015)
        self.assertAlmostEqual(self.sample_address.longitude, 19.428547, delta=0.015)
        with open("../Dane/Miejsca.csv") as f2:
            file2 = f2.read()
        self.assertEqual(file1, file2)

        sample_file: str = "test.csv"
        self.SavingToSampleFileAndTesting(
            sample_file, self.sample_address.SavePlaceToFile,
            sample_file
        )


if __name__ == '__main__':
    unittest.main()
