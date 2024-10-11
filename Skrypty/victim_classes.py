# -*- coding: utf-8 -*-
from __future__ import annotations
import csv
import enum
import sys
from typing import Dict, List, Literal, NamedTuple, Optional, Set, Tuple

from Skrypty.profiles_editor import DESCRIPTION_START, N_FIRST_LINES_TO_OMIT, STATE_TITLE, TIME_UNIT

# Własne typy
StateNumber = int

# Stałe
RPM_DETERIORATION_TABLE_FIRST_ROW_NUMBER: int = 2
RPM_DETERIORATION_INTERVAL_MINUTES: int = 30
# sys.maxsize w poniższych tablicach oznacza nieosiągalną górną granicę
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
# Pierwsza wartosc oznacza czy pacjent chodzi, druga czy wykonuje polecenia - zgodnie z trescia pracy
BEST_MOTOR_RESPONSE_SCORES: Dict[Tuple[bool, bool], int] = {
    (False, False): 0,
    (True, False): 2,
    (False, True): 3,
    (True, True): 4
}
EMERGENCY_DISCIPLINE_NUMBER: int = 15
N_VICTIM_STATS_IN_FILE: int = 6
INDEX_OF_STAT_IN_LINE: int = 3


def ConvertRowWithoutFirstElementToInt(row: List[str]) -> List[int]:
    return [int(element) for element in row[1:]]


def LoadDeteriorationTable() -> List[List[int]]:
    with open("../Dane/RPM_pogorszenie.csv", encoding="utf-8") as csv_file:
        temp_table: List[List[int]] = []
        csv_reader = csv.reader(csv_file, delimiter=";")
        for row in csv_reader:
            if csv_reader.line_num < RPM_DETERIORATION_TABLE_FIRST_ROW_NUMBER:
                continue
            temp_table.append(ConvertRowWithoutFirstElementToInt(row))
        return temp_table


RPM_DETERIORATION_TABLE: List[List[int]] = LoadDeteriorationTable()


class Victim:
    id_: int
    current_state: State
    states: List[State]
    hospital_admittance_time: Optional[int]
    initial_RPM_number: int
    current_RPM_number: int
    procedures_performed_so_far: List[Procedure]
    under_procedure: bool

    def __init__(self, id_: int, states: List[State]):
        self.id_ = id_
        self.states = states
        for state in self.states:
            if state.number == 1:
                self.current_state = state
        self.current_RPM_number = self.initial_RPM_number = self.CalculateRPM()
        self.hospital_admittance_time = None
        self.procedures_performed_so_far = []
        self.under_procedure = False

    def __eq__(self, other):
        if not isinstance(other, Victim):
            return False
        return vars(self) == vars(other)

    def __repr__(self):
        return str(self.__dict__)

    def CalculateRPM(self) -> int:
        """Oblicza RPM na podstawie obecnego stanu pacjenta"""
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
    def GetScoreFromLookUpTables(value, look_up_table: Dict[Tuple[int, int], int]) -> int:
        """Zwraca wynik przypisany parze liczb, między którymi znajduje się argument"""
        for (low, high), score in look_up_table.items():
            if low <= value <= high:
                return score

    def GetBestMotorResponseScore(self) -> int:
        """Zwraca wynik składowej odpowiedzi ruchowej oceny RPM"""
        return BEST_MOTOR_RESPONSE_SCORES[
            self.current_state.is_victim_walking, self.current_state.is_victim_following_orders
        ]

    @classmethod
    def FromString(cls, victim_string: str, victim_id: int) -> Victim:
        states_strings: List[str] = victim_string.split("\n\n")
        if "" in states_strings:
            states_strings.remove("")
        parsed_states: List[State] = []
        transition_datas: List[TransitionData] = []
        for state in states_strings:
            lines: List[str] = state.split("\n")
            parsed_state: State = State.FromString(lines)
            parsed_states.append(parsed_state)
            transition_data: TransitionData = cls.TryGetTransitionDataFromString(lines, parsed_state.number)
            if transition_data:
                transition_datas.append(transition_data)
        for transition_data in transition_datas:
            parsed_states = cls.SaveTransitionDataInProperState(transition_data, parsed_states)
        return Victim(victim_id, parsed_states)

    @staticmethod
    def TryGetTransitionDataFromString(state_lines: List[str], current_state_number: StateNumber) \
            -> Optional[TransitionData]:
        state_lines_number: int = N_FIRST_LINES_TO_OMIT + N_VICTIM_STATS_IN_FILE + 1
        if len(state_lines) > state_lines_number:
            parent_state, transition = state_lines[state_lines_number].split(", ", 1)
            _, _, parent_state_number_string = parent_state.split()
            _, transition_type, _, transition_condition_string = transition.split(maxsplit=3)
            return TransitionData(
                int(parent_state_number_string), current_state_number, transition_type, transition_condition_string
            )
        return None

    @staticmethod
    def SaveTransitionDataInProperState(transition_data: TransitionData, parsed_states: List[State]) -> List[State]:
        for parsed_state in parsed_states:
            if parsed_state.number == transition_data.parent_state_number:
                if transition_data.transition_type == "czas":
                    transition_time: int = int(transition_data.transition_condition[:-len(TIME_UNIT)])
                    parsed_state.timed_next_state_transition = (
                        transition_time, transition_data.child_state_number
                    )
                else:  # interwencja
                    critical_health_problems_strings: List[str] = transition_data.transition_condition.split(", ")
                    critical_health_problems: List[HealthProblem] = []
                    for critical_health_problem_string in critical_health_problems_strings:
                        critical_health_problems.append(
                            HealthProblem.FromProcedureString(critical_health_problem_string)
                        )
                    parsed_state.intervention_next_state_transition = (
                        critical_health_problems, transition_data.child_state_number
                    )
        return parsed_states

    def LowerRPM(self, time_from_simulation_start: int):
        """Zmniejsza RPM zależnie od czasu, który upłynął od początku symulacji"""
        if self.HasBeenAdmittedToHospital():
            return
        if time_from_simulation_start % RPM_DETERIORATION_INTERVAL_MINUTES == 0:
            index_of_time_interval: int = time_from_simulation_start // RPM_DETERIORATION_INTERVAL_MINUTES - 1
            self.current_RPM_number = RPM_DETERIORATION_TABLE[self.initial_RPM_number][index_of_time_interval]
        if self.current_state.timed_next_state_transition:
            if time_from_simulation_start >= self.current_state.GetTimeOfDeterioration():
                self.ChangeState(self.current_state.GetDeterioratedStateNumber())

    def ChangeState(self, new_state_number: StateNumber):
        for state in self.states:
            if state.number == new_state_number:
                self.current_state = state
                self.procedures_performed_so_far = []
                self.current_RPM_number = self.initial_RPM_number = self.CalculateRPM()
                return
        else:
            raise ValueError("Brak stanu o takim numerze")

    def PerformProcedureOnMe(self, procedure: Procedure):
        self.under_procedure = False
        if procedure.health_problem in self.GetCurrentCriticalHealthProblems():
            self.procedures_performed_so_far.append(procedure)
            if len(self.GetCurrentCriticalHealthProblems()) == 0:
                self.ChangeState(self.current_state.GetImprovedStateNumber())
        else:
            raise RuntimeError(f"Zła procedura {procedure.health_problem} użyta na poszkodowanym {self.id_}")

    def AdmitToHospital(self, time: int):
        self.hospital_admittance_time = time

    def GetCurrentHealthProblemDisciplines(self) -> List[int]:
        return self.current_state.GetAllHealthProblemDisciplines()

    def IsDead(self) -> bool:
        return self.current_state.triage_colour == TriageColour.BLACK

    def HasBeenAdmittedToHospital(self) -> bool:
        return self.hospital_admittance_time is not None

    def GetCurrentCriticalHealthProblems(self) -> Set[HealthProblem]:
        base_problems: Set[HealthProblem] = set(
            self.current_state.GetCriticalHealthProblemNeededToBeFixedForImprovement()
        )
        healed_problems: Set[HealthProblem] = {
            procedure.health_problem for procedure in self.procedures_performed_so_far
        }
        return base_problems.difference(healed_problems)


class TransitionData(NamedTuple):
    """Reprezentuje przejście między stanami poszkodowanego"""
    parent_state_number: StateNumber
    child_state_number: StateNumber
    transition_type: Literal["czas", "interwencja"]
    transition_condition: str


class State:
    """Klasa reprezentujaca stan pacjenta, zgodnie z calym profilem z pliku"""
    number: StateNumber
    is_victim_walking: bool
    respiratory_rate: int
    pulse_rate: int
    is_victim_following_orders: bool
    triage_colour: TriageColour
    health_problems_ids: List[HealthProblem]
    description: str
    timed_next_state_transition: Optional[Tuple[int, StateNumber]]
    intervention_next_state_transition: Optional[Tuple[List[HealthProblem], StateNumber]]

    def __init__(
            self, number: StateNumber, is_victim_walking: bool, respiratory_rate: int, pulse_rate: int,
            is_victim_following_orders: bool, triage_colour: TriageColour,
            health_problems_ids: List[HealthProblem], description: str,
            timed_next_state_transition: Optional[Tuple[int, StateNumber]] = None,
            intervention_next_state_transition: Optional[Tuple[List[HealthProblem], StateNumber]] = None
    ):
        self.CheckInitArguments(number, respiratory_rate, pulse_rate)
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
    def CheckInitArguments(number: StateNumber, respiratory_rate: int, pulse_rate: int):
        if number < 1:
            raise ValueError("Numer stanu nie może być mniejszy niż 1")
        if respiratory_rate < 0:
            raise ValueError("Częstotliwość oddechu nie może być mniejsza niż 0")
        if pulse_rate < 0:
            raise ValueError("Tętno nie może być mniejsze niż 0")

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return vars(self) == vars(other)

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def FromString(cls, lines: List[str]) -> State:
        state_title_line: str = lines[0]
        state_number_string: str = state_title_line[len(STATE_TITLE):]
        data_lines: List[str] = lines[N_FIRST_LINES_TO_OMIT:]
        is_victim_walking: bool = cls.GetIsVictimWalkingFromString(data_lines)
        respiratory_rate: int = cls.GetRespiratoryRateFromString(data_lines)
        pulse_rate: int = cls.GetPulseRateFromString(data_lines)
        is_victim_following_orders: bool = cls.GetIsVictimFollowingOrdersFromString(data_lines)
        triage_colour: TriageColour = cls.GetTriageColourFromString(data_lines)
        health_problem_ids: List[HealthProblem] = cls.GetHealthProblemIdsFromString(data_lines)
        description: str = cls.GetDescriptionFromString(data_lines)
        return State(
            int(state_number_string), is_victim_walking, respiratory_rate, pulse_rate,
            is_victim_following_orders, triage_colour, health_problem_ids,
            description
        )

    @classmethod
    def GetIsVictimWalkingFromString(cls, data_lines: List[str]) -> bool:
        stat: str = data_lines[0].split("; ")[INDEX_OF_STAT_IN_LINE]
        if stat == "nie":
            return False
        elif stat == "tak":
            return True
        else:
            raise ValueError("Błąd w trakcie wczytywania profilu: nieprawidłowa wartość \"Czy pacjent chodzi?\"")

    @classmethod
    def GetRespiratoryRateFromString(cls, data_lines: List[str]) -> int:
        stat: str = data_lines[1].split("; ")[INDEX_OF_STAT_IN_LINE]
        if stat == "nieobecna":
            return 0
        else:
            return int(stat)

    @classmethod
    def GetPulseRateFromString(cls, data_lines: List[str]) -> int:
        stat: str = data_lines[2].split("; ")[INDEX_OF_STAT_IN_LINE]
        if stat == "nieobecne":
            return 0
        else:
            return int(stat)

    @classmethod
    def GetIsVictimFollowingOrdersFromString(cls, data_lines: List[str]) -> bool:
        stat: str = data_lines[3].split("; ")[INDEX_OF_STAT_IN_LINE]
        if stat == "nie":
            return False
        elif stat == "tak":
            return True
        else:
            raise ValueError("Błąd w trakcie wczytywania profilu: nieprawidłowa wartość "
                             "\"Czy pacjent wykonuje polecenia?\"")

    @classmethod
    def GetTriageColourFromString(cls, data_lines: List[str]) -> TriageColour:
        stat: str = data_lines[4].split("; ")[INDEX_OF_STAT_IN_LINE]
        match stat:
            case "czarny":
                return TriageColour.BLACK
            case "czerwony":
                return TriageColour.RED
            case "żółty":
                return TriageColour.YELLOW
            case _:
                raise ValueError("Błąd w trakcie wczytywania profilu: nieprawidłowa wartość \"Kolor segregacji\"")

    @classmethod
    def GetHealthProblemIdsFromString(cls, data_lines: List[str]) -> List[HealthProblem]:
        stat: str = data_lines[5].split("; ")[INDEX_OF_STAT_IN_LINE]
        if "-" in stat:
            return []
        health_problems_strings: List[str] = stat.split(", ")
        health_problem_ids: List[HealthProblem] = []
        for health_problems_string in health_problems_strings:
            discipline_string, number_string = health_problems_string.split(".")
            health_problem_ids.append(
                HealthProblem(int(discipline_string), int(number_string))
            )
        return health_problem_ids

    @classmethod
    def GetDescriptionFromString(cls, data_lines: List[str]) -> str:
        return data_lines[6][len(DESCRIPTION_START):]

    def GetAllHealthProblemDisciplines(self) -> List[int]:
        health_problem_ids: List[int] = sorted(
            {health_problem.discipline for health_problem in self.health_problems_ids}
        )
        if EMERGENCY_DISCIPLINE_NUMBER in health_problem_ids:
            health_problem_ids.remove(EMERGENCY_DISCIPLINE_NUMBER)
            health_problem_ids.insert(0, EMERGENCY_DISCIPLINE_NUMBER)
        return health_problem_ids

    def GetTimeOfDeterioration(self) -> Optional[int]:
        return self.timed_next_state_transition[0] if self.timed_next_state_transition else None

    def GetDeterioratedStateNumber(self) -> Optional[StateNumber]:
        return self.timed_next_state_transition[1] if self.timed_next_state_transition else None

    def GetCriticalHealthProblemNeededToBeFixedForImprovement(self) -> List[HealthProblem]:
        return self.intervention_next_state_transition[0] if self.intervention_next_state_transition else []

    def GetImprovedStateNumber(self) -> Optional[StateNumber]:
        return self.intervention_next_state_transition[1] if self.intervention_next_state_transition else None


class TriageColour(enum.Enum):
    """Typ wyliczeniowy symbolizujacy kolory triazu"""
    GREEN = 1,
    YELLOW = 2,
    RED = 3,
    BLACK = 4


class HealthProblem(NamedTuple):
    """Reprezentuje problem zdrowotny - format X.Y jest przeksztalcony na pola discipline i number"""
    discipline: int
    number: int

    @classmethod
    def FromProcedureString(cls, procedure_string) -> HealthProblem:
        health_problem_numbers: str = procedure_string[2:-1]
        discipline_string, number_string = health_problem_numbers.split(".")
        return cls(int(discipline_string), int(number_string))


class Procedure(NamedTuple):
    """Reprezentuje procedury - format P(X.Y) jest przeksztalcony na problem zdrowotny (HealthProblem) zawarty w polu"""
    health_problem: HealthProblem
    time_needed_to_perform: int

    @classmethod
    def FromString(cls, procedure_string: str, time_needed_to_perform: str) -> Procedure:
        transition_health_problem_numbers: str = procedure_string[2:-1]  # odrzucenie P(...)
        discipline_string, number_string = transition_health_problem_numbers.split(".")
        return cls.FromDisciplineAndNumber(
            int(discipline_string), int(number_string), int(time_needed_to_perform)
        )

    @classmethod
    def FromDisciplineAndNumber(cls, discipline: int, number: int, time_needed_to_perform: int) -> Procedure:
        return cls(
            HealthProblem(discipline, number), time_needed_to_perform
        )
