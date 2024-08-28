# -*- coding: utf-8 -*-
from __future__ import annotations
import enum
import math
from typing import List, Optional

from Skrypty.victim_classes import Victim
from Skrypty.utilities import PlaceAddress


class Specialist:
    """Klasa reprezentująca specjalistów z ZRMu"""
    origin_zrm_id: str

    def __init__(self, origin_zrm_id: str):
        self.origin_zrm_id = origin_zrm_id


class ZRM:
    """Klasa reprezentująca zespół ratownictwa medycznego"""
    id_: str
    dispatch: str
    type: ZRMType
    specialists: List[Specialist]
    origin_location: PlaceAddress
    target_location: Optional[PlaceAddress]
    transported_victim: Optional[Victim]
    time_until_destination_in_minutes: Optional[int]
    queue_of_next_targets: List[PlaceAddress]

    def __init__(self, id_: str, dispatch: str, zrm_type: ZRMType, base_location: PlaceAddress):
        self.id_ = id_
        self.dispatch = dispatch
        self.type = zrm_type
        self.specialists = [Specialist(self.id_) for _ in range(self.GetPersonnelCount())]
        self.origin_location = base_location
        self.target_location, self.transported_victim, self.time_until_destination_in_minutes = None, None, None
        self.queue_of_next_targets = []

    def GetPersonnelCount(self) -> int:
        return self.type.value

    def IsTransportingAVictim(self) -> bool:
        return self.transported_victim is not None

    def IsDriving(self) -> bool:
        return self.time_until_destination_in_minutes is not None

    def StartTransportingAVictim(self, victim: Victim, target_location: PlaceAddress):
        """Zaczyna transport poszkodowanego do docelowej lokalizacji"""
        if self.IsDriving():
            raise RuntimeError(f"ZRM {self.id_} jest obecnie w drodze")
        self.transported_victim = victim
        self.StartDriving(target_location)

    def StartDriving(self, target_location: PlaceAddress):
        """Zaczyna jechać do docelowej lokalizacji"""
        self.target_location = target_location
        self.CalculateTimeForTheNextDestination()

    def CalculateTimeForTheNextDestination(self):
        distance: float
        duration: float
        distance, duration = self.origin_location.DistanceFromOtherPlace(self.target_location)
        self.time_until_destination_in_minutes = math.ceil(0.64 * duration)

    def DriveOrFinishDrivingAndReturnVictim(self) -> Optional[Victim]:
        """Zmniejsza czas do dojazdu na miejsce o 1 minutę/kończy dojazd"""
        if self.time_until_destination_in_minutes == 0:
            return self.FinishDrivingAndReturnVictim()
        self.time_until_destination_in_minutes -= 1
        return

    def FinishDrivingAndReturnVictim(self) -> Optional[Victim]:
        victim_to_return: Optional[Victim] = self.transported_victim
        self.transported_victim = None
        self.origin_location = self.target_location
        if not self.queue_of_next_targets:
            self.target_location = None
        else:
            self.target_location = self.queue_of_next_targets.pop(0)
        self.time_until_destination_in_minutes = None
        return victim_to_return

    def QueueNewTargetLocation(self, new_target: PlaceAddress):
        self.queue_of_next_targets.append(new_target)


class ZRMType(enum.Enum):
    """Typ wyliczeniowy dzielący ZRM-y na podstawowe i specjalistyczne i przydzielający im liczbę ratowników"""
    P = 2
    S = 3
