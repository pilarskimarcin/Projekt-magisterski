from __future__ import annotations
import enum
import sys
from typing import Dict, NamedTuple, Optional, Tuple


StateNumber = int
# W poni�szych LUTach, sys.maxsize oznacza nieosi�galn� g�rn� granic�
RESPIRATORY_RATE_SCORES: Dict[Tuple[int, int], int] = {
    (0, 0): 0,
    (1, 9): 1,
    (36, sys.maxsize): 2,
    (25, 35): 3,
    (10, 24): 4
}
PULSE_RATE_SCORES: Dict[Tuple[int, int], int] = {
    (0, 0): 0,
    (1, 40): 1,
    (41, 60): 2,
    (121, sys.maxsize): 3,
    (61, 120): 4
}
# Pierwsza warto�� oznacza czy pacjent chodzi, druga czy wykonuje polecenia - zgodnie z tre�ci� pracy
BEST_MOTOR_RESPONSE_SCORES: Dict[Tuple[bool, bool], int] = {
    (False, False): 0,
    (True, False): 2,
    (False, True): 3,
    (True, True): 4
}
RPM_DETERIORATION_INTERVAL_MINUTES: int = 30


class TriageColour(enum.Enum):
    """Typ wyliczeniowy symbolizuj�cy kolory tria�u"""
    GREEN = 1,
    YELLOW = 2,
    RED = 3,
    BLACK = 4


class HealthProblem(NamedTuple):
    """Reprezentuje problem zdrowotny - format X.Y jest przekszta�cony na pola discipline i number"""
    discipline: int
    number: int


class Procedure(NamedTuple):
    """Reprezentuje procedur� - format P(X.Y) jest przekszta�cony na problem zdrowotny (HealthProblem) zawarty w polu"""
    health_problem: HealthProblem


class State:
    """Klasa reprezentuj�ca stan pacjenta, zgodnie z ca�ym profilem z pliku"""
    number: StateNumber
    is_victim_walking: bool
    respiratory_rate: int
    pulse_rate: int
    is_victim_following_orders: bool
    triage_colour: TriageColour
    health_problems_ids: Tuple[HealthProblem, ...]
    description: str
    timed_next_state_transition: Optional[Tuple[int, StateNumber]]
    intervention_next_state_transition: Optional[Tuple[Procedure, StateNumber]]

    def __init__(
            self, number: int, is_victim_walking: bool, respiratory_rate: int, pulse_rate: int,
            is_victim_following_orders: bool, triage_colour: TriageColour,
            health_problems_ids: Tuple[HealthProblem, ...], description: str,
            timed_next_state_transition: Optional[Tuple[int, StateNumber]] = None,
            intervention_next_state_transition: Optional[Tuple[Procedure, StateNumber]] = None
    ):
        self.AssertInitArgumentsAreLegal(number, respiratory_rate, pulse_rate)
        self.number = number
        self.is_victim_walking = is_victim_walking
        self.respiratory_rate = respiratory_rate
        self.pulse_rate = pulse_rate
        self.is_victim_following_orders = is_victim_following_orders
        self.triage_colour = triage_colour
        self.health_problems_ids = health_problems_ids
        self.description = description
        self.timed_next_state_transition = timed_next_state_transition
        self.intervention_next_state_transition = intervention_next_state_transition

    @staticmethod
    def AssertInitArgumentsAreLegal(number: int, respiratory_rate: int, pulse_rate: int):
        assert number >= 1, "Numer stanu nie mo�e by� mniejszy ni� 1"
        assert respiratory_rate >= 0, "Cz�stotliwo�� oddechu nie mo�e by� mniejsza ni� 0"
        assert pulse_rate >= 0, "T�tno nie mo�e by� mniejsze ni� 0"


class Victim:
    id_: int
    current_state: State
    states: Tuple[State]
    hospital_admittance_time: Optional[float]
    initial_RPM_number: int
    current_RPM_number: int

    def __init__(self, id_: int, states: Tuple[State]):
        self.id_ = id_
        self.states = states
        for state in self.states:
            if state.number == 1:
                self.current_state = state
        self.current_RPM_number = self.initial_RPM_number = self.CalculateRPM()

    def CalculateRPM(self) -> int:
        """Calculates RPM from the victim's current state"""
        respiratory_rate_score: int = self.GetScoreFromLookUpTables(
            self.current_state.respiratory_rate, RESPIRATORY_RATE_SCORES
        )
        pulse_rate_score: int = self.GetScoreFromLookUpTables(
            self.current_state.pulse_rate, PULSE_RATE_SCORES
        )
        best_motor_response_score: int = self.GetBestMotorResponseScore()
        RPM_score: int = respiratory_rate_score + pulse_rate_score + best_motor_response_score
        return RPM_score

    @staticmethod
    def GetScoreFromLookUpTables(value, look_up_table):
        for (low, high), score in look_up_table.items():
            if low <= value <= high:
                return score

    def GetBestMotorResponseScore(self):
        return BEST_MOTOR_RESPONSE_SCORES[
            self.current_state.is_victim_walking, self.current_state.is_victim_following_orders
        ]

    def LowerRPM(self, time_from_simulation_start: int):
        # TODO: zrobi� LUT na te warto�ci wszystkie z tablicy pogarszania, niech bierze po kluczu self.current_RPM, a
        #  potem z listy i-ty element, i = time / INTERVAL?
        raise NotImplementedError
