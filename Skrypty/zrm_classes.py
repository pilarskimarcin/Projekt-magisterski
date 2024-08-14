# -*- coding: utf-8 -*-
from __future__ import annotations
import enum
from typing import Optional

from Skrypty.victim_classes import Victim
from Skrypty.utilities import PlaceAddress


class ZRM:
    """Klasa reprezentująca zespół ratownictwa medycznego"""
    id_: str
    base_address: str
    dispatch: str
    type: ZRMType
    transported_victim: Optional[Victim]
    current_location: PlaceAddress
    target_location: PlaceAddress


class ZRMType(enum.Enum):
    """Typ wyliczeniowy dzielący ZRM-y na podstawowe i specjalistyczne i przydzielający im liczbę ratowników"""
    P = 2,
    S = 3
