# -*- coding: utf-8 -*-
import os
import unittest
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

    def testDistanceFromOtherPlace(self):
        sample_address_2: utilities.PlaceAddress = utilities.PlaceAddress(
            "Chrzanowska",  6, "32-541", "Trzebinia"
        )
        self.assertEqual(self.sample_address.DistanceFromOtherPlace(sample_address_2), (9.891, 13.266666666666667))

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
        open(sample_file, "w")
        self.sample_address.SavePlaceToFile(sample_file)
        self.assertIsNotNone(open(sample_file))
        os.remove(sample_file)

    def testSaveDistanceToFile(self):
        self.fail()


if __name__ == '__main__':
    unittest.main()
