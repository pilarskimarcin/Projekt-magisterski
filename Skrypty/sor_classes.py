# -*- coding: utf-8 -*-
import math
import random
from typing import Dict, List, Optional

from Skrypty.utilities import PlaceAddress, TargetDestination
from Skrypty.victim_classes import Victim


class IncidentPlace(TargetDestination):
    address: PlaceAddress
    victims: List[Victim]
    reported_victims_count: int

    def __init__(self, address: PlaceAddress, victims: List[Victim]):
        super().__init__(address)
        self.victims = victims
        self.reported_victims_count = self.GetStartingAmountOfVictims()

    def __repr__(self):
        return str(self.__dict__)

    def GetStartingAmountOfVictims(self) -> int:
        victims_total_count: int = len(self.victims)
        return math.floor(random.uniform(0.3, 0.75) * victims_total_count)

    def TryTakeVictim(self, victim_id: int) -> Optional[Victim]:
        for victim in self.victims:
            if victim.id_ == victim_id:
                self.victims.remove(victim)
                return victim
        return None

    def NeedsReconnaissance(self):
        return len(self.victims) != self.reported_victims_count


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

    def __repr__(self):
        return str(self.__dict__)

    def TakeInVictim(self, victim: Victim, current_time: int):
        if self.current_beds_count == 0:
            raise RuntimeError(f"Brak miejsc na oddziale {self.name}")
        self.admitted_victims.append(victim)
        victim.AdmitToHospital(current_time)
        self.current_beds_count -= 1


class Hospital(TargetDestination):
    id_: int
    name: str
    departments: List[Department]
    incoming_victims: Dict[int, List[Victim]]

    def __init__(self, id_: int, name: str, address: PlaceAddress, departments: List[Department]):
        super().__init__(address)
        self.id_ = id_
        self.name = name
        self.departments = departments
        self.incoming_victims = {}

    def __eq__(self, other):
        if not isinstance(other, Hospital):
            return False
        return vars(self) == vars(other)

    def __repr__(self):
        return str(self.__dict__)

    def TakeInVictimToOneOfDepartments(self, victim: Victim, current_time: int):
        for medicine_discipline_id in victim.GetCurrentHealthProblemDisciplines():
            department: Department = self.TryGetDepartment(medicine_discipline_id)
            if department:
                department.TakeInVictim(victim, current_time)
                return
        raise RuntimeError(f"Brak pasującego oddziału w szpitalu {self.name}")

    def TryGetDepartment(self, medicine_discipline_id: int) -> Optional[Department]:
        for department in self.departments:
            if (medicine_discipline_id in department.medical_categories and
                    self.AvailableBedsInDepartment(department) > 0):
                return department
        return None

    def AvailableBedsInDepartment(self, department: Department) -> int:
        return department.current_beds_count - len(self.incoming_victims.get(department.id_, []))

    def CanVictimBeTakenIn(self, target_victim: Victim) -> bool:
        for medicine_discipline_id in target_victim.GetCurrentHealthProblemDisciplines():
            department: Department = self.TryGetDepartment(medicine_discipline_id)
            if department:
                self.incoming_victims.setdefault(department.id_, []).append(target_victim)
                return True
        return False

    def RemoveVictimFromIncoming(self, transported_victim: Victim):
        for department_id, victim_list in self.incoming_victims.items():
            if transported_victim in victim_list:
                self.incoming_victims[department_id].remove(transported_victim)
                if not self.incoming_victims[department_id]:
                    self.incoming_victims.pop(department_id)
                return
