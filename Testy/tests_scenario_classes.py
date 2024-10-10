# -*- coding: utf-8 -*-
import pandas as pd
from typing import Dict, List, Tuple
import unittest

from Skrypty import scenario_classes as scenario
from Skrypty import sor_classes as sor
from Skrypty import utilities as util
from Skrypty import victim_classes as victim
from Skrypty import zrm_classes as zrm
from Testy import tests_sor_classes as tests_sor
from Testy import tests_utilities as tests_util


def CreateSampleScenarioData() -> Tuple[sor.Hospital, list[zrm.ZRM], list[victim.Victim], util.PlaceAddress]:
    sample_hospital: sor.Hospital = CreateSampleHospital()
    sample_teams: List[zrm.ZRM] = CreateSampleTeams()
    sample_victims: List[victim.Victim] = tests_sor.CreateSampleVictims()
    sample_address2: util.PlaceAddress = tests_util.CreateSampleAddressIncident()
    return sample_hospital, sample_teams, sample_victims, sample_address2


def CreateSampleHospital() -> sor.Hospital:
    sample_departments: List[sor.Department] = [
        sor.Department(id_=1, name="Oddział chirurgii urazowo-ortopedycznej", medical_categories=[25],
                       current_beds_count=10),
        sor.Department(id_=2, name="Oddział kardiologiczny", medical_categories=[53],
                       current_beds_count=14),
        sor.Department(id_=3, name="Oddział anestezjologii i intensywnej terapii", medical_categories=[1],
                       current_beds_count=2),
        sor.Department(id_=4, name="Oddział chirurgii naczyniowej", medical_categories=[39, 37],
                       current_beds_count=5),
        sor.Department(id_=5, name="Oddział neurologiczny z pododziałem udarowym", medical_categories=[22],
                       current_beds_count=5),
        sor.Department(id_=6, name="Szpitalny Oddział Ratunkowy", medical_categories=[15],
                       current_beds_count=6),
        sor.Department(id_=7, name="Pododdział udarowy", medical_categories=[22],
                       current_beds_count=5)
    ]
    sample_address: util.PlaceAddress = tests_util.CreateSampleAddressHospital()
    return sor.Hospital(
        id_=1, name="Szpital Powiatowy w Chrzanowie",
        address=sample_address,
        departments=sample_departments
    )


def CreateSampleTeams() -> List[zrm.ZRM]:
    sample_address: util.PlaceAddress = tests_util.CreateSampleAddressHospital()
    return [
        zrm.ZRM(id_="K01 47", dispatch="DM06-01", zrm_type=zrm.ZRMType.S, base_location=sample_address),
        zrm.ZRM(id_="K01 098", dispatch="DM06-01", zrm_type=zrm.ZRMType.P, base_location=sample_address)
    ]


class TestScenario(unittest.TestCase):
    sample_scenario: scenario.Scenario

    def setUp(self):
        self.sample_scenario = scenario.Scenario("../Scenariusze/Scenariusz 1.txt")

    def testInit(self):
        sample_hospital, sample_teams, sample_victims, sample_address = CreateSampleScenarioData()

        self.assertEqual(self.sample_scenario.hospitals, [sample_hospital])
        self.assertEqual(self.sample_scenario.teams, sample_teams)
        self.assertEqual(self.sample_scenario.victims, sample_victims)
        self.assertEqual(self.sample_scenario.address, sample_address)

    def testParseDepartments(self):
        sample_input: str = "Oddziały - liczba miejsc\n1 10\n2 14\n3 2\n4 5\n5 5\n6 6\n7 5"
        sample_hospital: sor.Hospital = CreateSampleHospital()

        self.sample_scenario.ParseDepartments(sample_input)

        self.assertEqual(self.sample_scenario.hospitals, [sample_hospital])

    def testAddDepartmentsToHospitals(self):
        sample_departments_data: List[str] = ["1 10", "2 14", "3 2", "4 5", "5 5", "6 6", "7 5"]
        SOR_table: pd.DataFrame = pd.read_csv("../Dane/SOR.csv", encoding="utf-8", sep=";", index_col=0)
        hospitals_and_departments_dict: Dict[Tuple[str, str], List[sor.Department]] = (
            scenario.Scenario.AddDepartmentsToHospitals(sample_departments_data, SOR_table)
        )
        sample_hospital: sor.Hospital = CreateSampleHospital()
        sample_hospital_with_joined_departments: Dict[Tuple[str, str], List[sor.Department]] = {
            (sample_hospital.name, sample_hospital.address.address_for_places_data): sample_hospital.departments
        }

        self.assertEqual(hospitals_and_departments_dict, sample_hospital_with_joined_departments)

    def testGetMedicalDisciplinesFromStringMoreDisciplines(self):
        sample_disciplines_string: str = "25, 14"
        parsed_disciplines: List[int] = scenario.Scenario.GetMedicalDisciplinesFromString(sample_disciplines_string)

        self.assertEqual(parsed_disciplines, [25, 14])

    def testGetMedicalDisciplinesFromStringOneDiscipline(self):
        sample_disciplines_string: str = "25"
        parsed_disciplines: List[int] = scenario.Scenario.GetMedicalDisciplinesFromString(sample_disciplines_string)

        self.assertEqual(parsed_disciplines, [25])

    def testParseTeams(self):
        sample_input: str = "ZRM: 1, 2"
        sample_teams: List[zrm.ZRM] = CreateSampleTeams()
        self.sample_scenario.ParseTeams(sample_input)

        self.assertEqual(self.sample_scenario.teams, sample_teams)

    def testGetTeamsDataFromIds(self):
        sample_teams_ids: List[int] = [1, 2]
        sample_teams: List[zrm.ZRM] = CreateSampleTeams()
        self.sample_scenario.GetTeamsDataFromIds(sample_teams_ids)

        self.assertEqual(self.sample_scenario.teams, sample_teams)

    def testParseVictimsCorrect(self):
        sample_input1: str = "Profile - liczba poszkodowanych\nŻółty/Profil70 2\nŻółty/Profil95 2"
        sample_input2: str = "Całkowita liczba poszkodowanych: 4"
        sample_victims: List[victim.Victim] = tests_sor.CreateSampleVictims()
        self.sample_scenario.ParseVictims(sample_input1, sample_input2)

        self.assertEqual(self.sample_scenario.victims, sample_victims)

    def testParseVictimsError(self):
        sample_input1: str = "Profile - liczba poszkodowanych\nŻółty/Profil70 2\nŻółty/Profil95 2"
        sample_input2: str = "Całkowita liczba poszkodowanych: 5"
        self.assertRaises(
            RuntimeError,
            self.sample_scenario.ParseVictims, sample_input1, sample_input2
        )

    def testCreateVictimsFromProfilesAndCounts(self):
        sample_profiles_and_counts: List[Tuple[str, int]] = [
            ("Żółty/Profil70", 2), ("Żółty/Profil95", 2)
        ]
        sample_victims: List[victim.Victim] = tests_sor.CreateSampleVictims()
        self.sample_scenario.CreateVictimsFromProfilesAndCounts(sample_profiles_and_counts)

        self.assertEqual(self.sample_scenario.victims, sample_victims)

    def testParseAddress(self):
        sample_input: str = "Adres: Magnoliowa 10, 32-500 Chrzanów"
        sample_address: util.PlaceAddress = tests_util.CreateSampleAddressIncident()
        self.sample_scenario.ParseAddress(sample_input)

        self.assertEqual(self.sample_scenario.address, sample_address)


if __name__ == "__main__":
    unittest.main()
