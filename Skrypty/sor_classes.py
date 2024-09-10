# -*- coding: utf-8 -*-
from typing import List, Optional

from Skrypty.utilities import PlaceAddress, TargetDestination
from Skrypty.victim_classes import Victim


class IncidentPlace(TargetDestination):
    address: PlaceAddress
    victims: List[Victim]

    def __init__(self, address: PlaceAddress, victims: List[Victim]):
        super().__init__(address)
        self.victims = victims

    def TryTakeVictim(self, victim_id: int) -> Optional[Victim]:
        for victim in self.victims:
            if victim.id_ == victim_id:
                self.victims.remove(victim)
                return victim
        return None


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

    def __eq__(self, other):
        if not isinstance(other, Department):
            return False
        return vars(self) == vars(other)

    def TakeInVictim(self, victim: Victim, current_time: float):
        if self.current_beds_count == 0:
            raise RuntimeError(f"Brak miejsc na oddziale {self.name}")
        self.admitted_victims.append(victim)
        victim.AdmitToHospital(current_time)
        self.current_beds_count -= 1


class Hospital(TargetDestination):
    id_: int
    name: str
    departments: List[Department]

    def __init__(self, id_: int, name: str, address: PlaceAddress, departments: List[Department]):
        super().__init__(address)
        self.id_ = id_
        self.name = name
        self.departments = departments

    def __eq__(self, other):
        if not isinstance(other, Hospital):
            return False
        return vars(self) == vars(other)

    def TakeInVictimToOneOfDepartments(self, victim: Victim, current_time: float):
        for medicine_discipline_id in victim.GetCurrentHealthProblemIds():
            department: Department = self.TryGetDepartment(medicine_discipline_id)
            if self.TryGetDepartment(medicine_discipline_id):
                department.TakeInVictim(victim, current_time)
                return
        raise RuntimeError(f"Brak pasującego oddziału w szpitalu {self.name}")

    def TryGetDepartment(self, medicine_discipline_id: int) -> Optional[Department]:
        for department in self.departments:
            if medicine_discipline_id in department.medical_categories:
                return department
        return None
