# -*- coding: utf-8 -*-
import pandas as pd
from typing import Dict, List, Tuple

from Skrypty.sor_classes import Hospital, Department
from Skrypty.utilities import PlaceAddress
from Skrypty.victim_classes import Victim
from Skrypty.zrm_classes import ZRM, ZRMType

DATA_TITLE_OFFSET: int = 1
ZRM_DATA_TITLE: str = "ZRM: "
ADDRESS_DATA_TITLE: str = "Adres: "


class Scenario:
    """Klasa przedstawiająca treść scenariusza"""
    hospitals: List[Hospital]
    teams: List[ZRM]
    victims: List[Victim]
    address: PlaceAddress

    def __init__(self, scenario_filename: str):
        with open(scenario_filename, encoding="utf-8") as file:
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
        hospitals_and_departments: Dict[Tuple[str, str], List[Department]] = self.AddDepartmentsToHospitals(
            departments_data, SOR_table)
        hospital_id: int = 1
        for key, departments in hospitals_and_departments.items():
            hospital_name, address_str = key
            address: PlaceAddress = PlaceAddress.FromString(address_str)
            self.hospitals.append(
                Hospital(id_=hospital_id, name=hospital_name, address=address, departments=departments)
            )
            hospital_id += 1

    @staticmethod
    def AddDepartmentsToHospitals(departments_data: List[str], hospital_data_table: pd.DataFrame) -> (
            Dict)[Tuple[str, str], List[Department]]:
        departments: Dict[Tuple[str, str], List[Department]] = dict()
        for department_data in departments_data:
            department_number, beds_number = [int(number) for number in department_data.split()]
            department_row: pd.Series = hospital_data_table.loc[department_number]
            _, hospital_name, address, department_name, medical_disciplines_string, _ = department_row.tolist()
            if (hospital_name, address) not in departments.keys():
                departments[hospital_name, address] = []
            medical_disciplines: List[int] = Scenario.GetMedicalDisciplinesFromString(medical_disciplines_string)
            departments[hospital_name, address].append(
                Department(id_=department_number, name=department_name, medical_categories=medical_disciplines,
                           current_beds_count=beds_number)
            )
        return departments

    @staticmethod
    def GetMedicalDisciplinesFromString(medical_disciplines_string: str) -> List[int]:
        disciplines_string_list: List[str] = medical_disciplines_string.split(", ")
        return [int(discipline_string) for discipline_string in disciplines_string_list]

    def ParseTeams(self, teams_part: str):
        teams_part_without_title: str = teams_part[len(ZRM_DATA_TITLE):]
        teams_ids: List[int] = [int(number) for number in teams_part_without_title.split(", ")]
        self.GetTeamsDataFromIds(teams_ids)

    def GetTeamsDataFromIds(self, teams_ids: List[int]):
        full_teams_data: pd.DataFrame = pd.read_csv("../Dane/ZRM.csv", encoding="utf-8", sep=";", index_col=0)
        self.teams = []
        for team_id in teams_ids:
            team_row: pd.Series = full_teams_data.loc[team_id]
            team_number, address, dispatch, team_type = team_row.tolist()
            zrm_parsed_type: ZRMType = eval(f"ZRMType.{team_type}", globals(), locals())
            self.teams.append(ZRM(team_number, dispatch, zrm_parsed_type, PlaceAddress.FromString(address)))

    def ParseVictims(self, victims_part: str, total_victims_part: str):
        profiles_and_counts: List[Tuple[str, int]] = []
        sum_victims_counts: int = 0
        for line in victims_part.split("\n")[DATA_TITLE_OFFSET:]:
            profile, amount_string = line.split()
            profiles_and_counts.append((profile, int(amount_string)))
            sum_victims_counts += int(amount_string)
        total_victims_count: int = int(total_victims_part.split()[-1])
        if total_victims_count != sum_victims_counts:
            raise RuntimeError(f"Całkowita liczba poszkodowanych {total_victims_count} nie jest równa sumie liczb "
                               f"pposzkodowanych {sum_victims_counts}")
        self.CreateVictimsFromProfilesAndCounts(profiles_and_counts)

    def CreateVictimsFromProfilesAndCounts(self, profiles_and_counts: List[Tuple[str, int]]):
        self.victims = []
        victim_id: int = 1
        for profile, count in profiles_and_counts:
            path: str = "../Profile pacjentów/" + profile + ".txt"
            with open(path, encoding="utf-8") as f:
                profile_text: str = f.read()
                for _ in range(count):
                    self.victims.append(
                        Victim.FromString(profile_text, victim_id)
                    )
                    victim_id += 1

    def ParseAddress(self, address_part: str):
        address_part_without_title: str = address_part[len(ADDRESS_DATA_TITLE):]
        self.address = PlaceAddress.FromString(address_part_without_title.replace(",", ""))
