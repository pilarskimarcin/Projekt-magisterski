# -*- coding: utf-8 -*-
from typing import List, Optional

from Skrypty.utilities import PlaceAddress
from Skrypty.victim_classes import Victim


class Department:
    id_: int
    name: str
    medical_categories: List[int]
    current_beds_count: int
    admitted_victims: List[Victim]

    def __init__(self, id_: int, name: str, medical_categories: List[int], current_beds_count: int):
        self.id_ = id_
        self.name = name
        self.medical_categories = medical_categories
        self.current_beds_count = current_beds_count
        self.admitted_victims = []

    def TakeInVictim(self, victim: Victim, current_time: float):
        if self.current_beds_count == 0:
            raise RuntimeError(f"Brak miejsc na oddziale {self.name}")
        self.admitted_victims.append(victim)
        victim.AdmitToHospital(current_time)
        self.current_beds_count -= 1


class Hospital:
    id_: int
    name: str
    address: PlaceAddress
    departments: List[Department]

    def __init__(self, id_: int, name: str, address: PlaceAddress, departments: List[Department]):
        self.id_ = id_
        self.name = name
        self.address = address
        self.departments = departments

    def TryGetDepartment(self, medicine_discipline_id: int) -> Optional[Department]:
        for department in self.departments:
            if medicine_discipline_id in department.medical_categories:
                return department
        return None

    def TakeInVictimToOneOfDepartments(self, victim: Victim, current_time: float):
        for medicine_discipline_id in victim.GetCurrentHealthProblemIds():
            department: Department = self.TryGetDepartment(medicine_discipline_id)
            if self.TryGetDepartment(medicine_discipline_id):
                department.TakeInVictim(victim, current_time)
                return
        raise RuntimeError(f"Brak pasującego oddziału w szpitalu {self.name}")
