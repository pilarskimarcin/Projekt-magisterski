# -*- coding: utf-8 -*-
from __future__ import annotations
import enum
import math
from typing import List, Optional

from Skrypty.sor_classes import IncidentPlace
from Skrypty.victim_classes import Procedure, Victim
from Skrypty.utilities import PlaceAddress, TargetDestination


class Specialist:
    """Klasa reprezentująca specjalistów z ZRMu"""
    id_: int
    origin_zrm_id: str
    time_until_procedure_is_finished: Optional[int]
    stored_procedure: Optional[Procedure]
    target_victim: Optional[Victim]
    is_idle: bool

    def __init__(self, origin_zrm_id: str, id_: int):
        self.id_ = id_
        self.origin_zrm_id = origin_zrm_id
        self.time_until_procedure_is_finished = self.stored_procedure = self.target_victim = None
        self.is_idle = True

    def __eq__(self, other):
        if not isinstance(other, Specialist):
            return False
        return vars(self) == vars(other)

    def __repr__(self):
        return str(self.__dict__)

    def StartPerformingProcedure(self, procedure: Procedure, target_victim: Victim = None):
        self.target_victim = target_victim
        if self.target_victim:
            self.target_victim.under_procedure = True
        self.stored_procedure = procedure
        self.time_until_procedure_is_finished = procedure.time_needed_to_perform
        self.is_idle = False

    def ContinuePerformingProcedure(self):
        if self.time_until_procedure_is_finished is not None:
            self.time_until_procedure_is_finished -= 1
            if self.time_until_procedure_is_finished == 0:
                self.FinishProcedure()

    def FinishProcedure(self):
        if self.target_victim:
            self.target_victim.PerformProcedureOnMe(self.stored_procedure)
        self.time_until_procedure_is_finished = self.target_victim = self.stored_procedure = None
        self.is_idle = True


class ZRM:
    """Klasa reprezentująca zespół ratownictwa medycznego"""
    id_: str
    dispatch: str
    type: ZRMType
    specialists: List[Specialist]
    origin_location_address: PlaceAddress
    target_location: Optional[TargetDestination]
    transported_victim: Optional[Victim]
    time_until_destination_in_minutes: Optional[int]
    queue_of_next_targets: List[TargetDestination]
    are_specialists_outside: bool

    def __init__(self, id_: str, dispatch: str, zrm_type: ZRMType, base_location: PlaceAddress):
        self.id_ = id_
        self.dispatch = dispatch
        self.type = zrm_type
        self.specialists = [Specialist(self.id_, i + 1) for i in range(self.GetPersonnelCount())]
        self.origin_location_address = base_location
        self.target_location, self.transported_victim, self.time_until_destination_in_minutes = None, None, None
        self.queue_of_next_targets = []
        self.are_specialists_outside = False

    def GetPersonnelCount(self) -> int:
        return self.type.value

    def __eq__(self, other):
        if not isinstance(other, ZRM):
            return False
        return vars(self) == vars(other)

    def __repr__(self):
        return str(self.__dict__)

    def IsTransportingAVictim(self) -> bool:
        return self.transported_victim is not None

    def StartTransportingAVictim(self, victim: Victim, target_location: TargetDestination):
        """Zaczyna transport poszkodowanego do docelowej lokalizacji"""
        if self.IsDriving():
            raise RuntimeError(f"ZRM {self.id_} jest obecnie w drodze")
        self.transported_victim = victim
        self.StartDriving(target_location)

    def IsDriving(self) -> bool:
        return self.time_until_destination_in_minutes is not None

    def StartDriving(self, target_location: Optional[TargetDestination] = None):
        """Zaczyna jechać do docelowej lokalizacji"""
        if self.IsDriving():
            raise RuntimeError(f"ZRM {self.id_} jest obecnie w drodze")
        if self.are_specialists_outside:
            raise RuntimeError("Specjaliści są poza pojazdem, nie można zacząć jechać")
        if target_location:
            self.target_location = target_location
        self.CalculateTimeForTheNextDestination()

    def CalculateTimeForTheNextDestination(self):
        distance, duration = self.origin_location_address.GetDistanceAndDurationToOtherPlace(
            self.target_location.address)
        self.time_until_destination_in_minutes = math.ceil(0.64 * duration)

    def DriveOrFinishDrivingAndReturnVictim(self) -> Optional[Victim]:
        """Zmniejsza czas do dojazdu na miejsce o 1 minutę/kończy dojazd"""
        if not self.IsDriving():
            return None
        self.time_until_destination_in_minutes -= 1
        if self.time_until_destination_in_minutes == 0:
            return self.FinishDrivingAndReturnVictim()
        return

    def FinishDrivingAndReturnVictim(self) -> Optional[Victim]:
        victim_to_return: Optional[Victim] = self.transported_victim
        self.transported_victim = None
        self.origin_location_address = self.target_location.address
        self.time_until_destination_in_minutes = None
        if not self.queue_of_next_targets:
            self.target_location = None
        else:
            self.target_location = self.queue_of_next_targets.pop(0)
            if isinstance(self.target_location, IncidentPlace):
                self.StartDriving()
        return victim_to_return

    def QueueNewTargetLocation(self, new_target: TargetDestination):
        self.queue_of_next_targets.append(new_target)

    def SpecialistsLeaveTheVehicle(self):
        if self.IsDriving():
            raise RuntimeError("Karetka w ruchu, specjaliści nie mogą jej opuścić")
        for specialist in self.specialists:
            specialist.is_idle = True
        self.are_specialists_outside = True

    def TrySpecialistsComeBackToTheVehicle(self) -> bool:
        if self.AreSpecialistsIdle():
            self.are_specialists_outside = False
            for specialist in self.specialists:
                specialist.is_idle = False
            return True
        return False

    def AreSpecialistsIdle(self) -> bool:
        return all([specialist.is_idle for specialist in self.specialists])

    def SpecialistsContinuePerformingProcedures(self):
        if self.are_specialists_outside:
            for specialist in self.specialists:
                specialist.ContinuePerformingProcedure()


class ZRMType(enum.Enum):
    """Typ wyliczeniowy dzielący ZRM-y na podstawowe i specjalistyczne i przydzielający im liczbę ratowników"""
    P = 2
    S = 3
