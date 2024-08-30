# -*- coding: utf-8 -*-
import pandas as pd
from typing import Dict, List, Tuple

from Skrypty.sor_classes import Hospital, Department
from Skrypty.utilities import PlaceAddress
from Skrypty.victim_classes import Victim
from Skrypty.zrm_classes import ZRM

DATA_TITLE_OFFSET: int = 1


class Scenario:
    """Klasa przedstawiająca treść scenariusza"""
    hospitals: List[Hospital]
    teams: List[ZRM]
    victims: List[Victim]
    address: PlaceAddress

    def __init__(self, scenario_filename: str):
        with open(scenario_filename) as file:
            content: str = file.read()
            departments_part: str
            teams_part: str
            victims_part: str
            total_victims_part: str
            address_part: str
            departments_part, teams_part, victims_part, total_victims_part, address_part = content.split("\n\n")
        self.ParseDepartments(departments_part)
        self.ParseTeams(teams_part)
        self.ParseVictims(victims_part, total_victims_part)
        self.ParseAddress(address_part)

    def ParseDepartments(self, departments_string: str):
        departments_data: List[str] = departments_string.split("\n")[DATA_TITLE_OFFSET:]
        SOR_table: pd.DataFrame = pd.read_csv("../Dane/SOR.csv", encoding="utf-8", sep=";", index_col=0)
        self.hospitals = []
        hospitals_and_departments: Dict[Tuple[str, str], List[Department]] = self.JoinDepartmentDataWithHospitals(
            departments_data, SOR_table
        )
        hospital_id: int = 1
        for key, departments in hospitals_and_departments.items():
            hospital_name, address_str = key
            address_parts: List[str] = address_str.split()
            address: PlaceAddress = PlaceAddress(street=address_parts[0], number=int(address_parts[1]),
                                                 postal_code=address_parts[2], city=address_parts[3])
            self.hospitals.append(
                Hospital(id_=hospital_id, name=hospital_name, address=address, departments=departments)
            )
            hospital_id += 1

    @staticmethod
    def JoinDepartmentDataWithHospitals(
            departments_data: List[str], hospital_data_table: pd.DataFrame
    ) -> Dict[Tuple[str, str], List[Department]]:
        departments: Dict[Tuple[str, str], List[Department]] = dict()
        for department_data in departments_data:
            department_number, beds_number = [int(number) for number in department_data.split()]
            department_row: pd.Series = hospital_data_table.loc[department_number]
            _, hospital_name, address, department_name, medical_disciplines, _ = department_row.tolist()
            if (hospital_name, address) not in departments.keys():
                departments[hospital_name, address] = []
            departments[hospital_name, address].append(
                Department(id_=department_number, name=department_name, medical_categories=medical_disciplines,
                           current_beds_count=beds_number)
            )
        return departments

    def ParseTeams(self, teams_part):
        pass

    def ParseVictims(self, victims_part, total_victims_part):
        pass

    def ParseAddress(self, address_part):
        pass
