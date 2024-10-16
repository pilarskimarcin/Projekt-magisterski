# -*- coding: utf-8 -*-
from typing import List, Set, Tuple
import unittest

from Skrypty import victim_classes as victim

SAMPLE_DESCRIPTION: str = (u"Przygnieciony konstrukcją przytomny, logiczny pacjent z duża krwawiąca rana okolicy "
                           u"czołowej i ciemieniowej i dusznością. Złamanie zamknięte obu kości udowych ( zasinienie, "
                           u"niestabilne, trzeszczy, powiększony obwód ud) oraz odma prawostronnie.  Czynności "
                           u"krytyczne do wykonania: Założenie dwóch opasek uciskowych na złamane kończyny i "
                           u"odbarczenie odmy w przeciągu 50 minut od pierwszego kontaktu z medykiem. Po 50 min bez "
                           u"wykonania czynności krytycznych – NZK z asystolią. USG – brak objawu ślizgania opłucnej "
                           u"prawostronnie.")


def CreateSampleVictim() -> victim.Victim:
    """Profil poszkodowanego - Profil5.txt"""
    return victim.Victim(1, CreateStatesForSampleVictim())


def CreateStatesForSampleVictim() -> List[victim.State]:
    sample_states: List[victim.State] = [
        CreateSampleState(),
        victim.State(number=2, is_victim_walking=False, respiratory_rate=0, pulse_rate=0,
                     is_victim_following_orders=False, triage_colour=victim.TriageColour.BLACK, health_problems=[],
                     description=""),
        victim.State(number=3, is_victim_walking=False, respiratory_rate=14, pulse_rate=0,
                     is_victim_following_orders=True, triage_colour=victim.TriageColour.RED,
                     health_problems=[victim.HealthProblem(5, 4), victim.HealthProblem(25, 2)], description="")
    ]
    return sample_states


def CreateSampleState(no_transitions: bool = False) -> victim.State:
    sample_state: victim.State = victim.State(number=1, is_victim_walking=False, respiratory_rate=34, pulse_rate=0,
                                              is_victim_following_orders=True, triage_colour=victim.TriageColour.RED,
                                              health_problems=CreateSampleHealthProblems(),
                                              description=SAMPLE_DESCRIPTION,
                                              timed_next_state_transition=SampleTimedNextStateTransition(),
                                              intervention_next_state_transition=(SampleCriticalHealthProblems(), 3))
    if no_transitions:
        sample_state.timed_next_state_transition = sample_state.intervention_next_state_transition = None
    return sample_state


def CreateSampleHealthProblems() -> List[victim.HealthProblem]:
    sample_critical_health_problems: List[victim.HealthProblem] = SampleCriticalHealthProblems()
    return [
        victim.HealthProblem(5, 4), sample_critical_health_problems[0], sample_critical_health_problems[1],
        victim.HealthProblem(25, 2)
    ]


def SampleTimedNextStateTransition() -> Tuple[int, int]:
    return 50, 2


def SampleCriticalHealthProblems() -> List[victim.HealthProblem]:
    return [victim.HealthProblem(15, 7), victim.HealthProblem(15, 14)]


def SampleHealthProblemDisciplines() -> Set[int]:
    return {15, 5, 25}


def CreateSampleTransitionData() -> victim.TransitionData:
    transition_time, transition_new_state = SampleTimedNextStateTransition()
    return victim.TransitionData(
        parent_state_number=1, child_state_number=transition_new_state, transition_type="czas",
        transition_condition=f"{transition_time}min"
    )


def CreateDeteriorationTableLastRow() -> List[int]:
    return [12, 12, 11, 11, 10, 10, 10, 10, 9, 9, 8, 8]


def RoundNUpToNearestMultipleOfM(n: int, m: int):
    """źródło: https://gist.github.com/OR13/20bc2044e01d512a51d0"""
    needed_multiplier_of_m: int = (n + m - 1) // m
    return m * needed_multiplier_of_m


class FunctionsTests(unittest.TestCase):
    def testLoadingDeteriorationTable(self):
        deterioration_table_length: int = 13
        deterioration_table_last_row: List[int] = CreateDeteriorationTableLastRow()
        deterioration_table = victim.LoadDeteriorationTable()

        self.assertEqual(len(deterioration_table), deterioration_table_length)
        self.assertEqual(deterioration_table[-1], deterioration_table_last_row)

    def testConvertRowWithoutFirstElementToInt(self):
        sample_string_row: List[str] = ["12", "12", "12", "11", "11", "10", "10", "10", "10", "9", "9", "8", "8"]
        sample_result_int_row: List[int] = CreateDeteriorationTableLastRow()

        self.assertEqual(
            victim.ConvertRowWithoutFirstElementToInt(sample_string_row),
            sample_result_int_row
        )


class VictimClassTests(unittest.TestCase):
    sample_victim: victim.Victim
    sample_profile_text: str

    def setUp(self):
        self.sample_victim = CreateSampleVictim()
        sample_profile_file: str = "../Profile pacjentów/Czerwony/Profil5.txt"
        with open(sample_profile_file, encoding="utf-8") as f:
            self.sample_profile_text = f.read()

    def testInit(self):
        self.assertEqual(self.sample_victim.id_, 1)
        self.assertEqual(self.sample_victim.current_state, CreateSampleState())
        self.assertEqual(self.sample_victim.current_RPM_number, 6)
        self.assertEqual(self.sample_victim.initial_RPM_number, 6)
        self.assertEqual(self.sample_victim.hospital_admittance_time, None)

    def testEquality(self):
        sample_victim: victim.Victim = CreateSampleVictim()

        self.assertEqual(sample_victim, self.sample_victim)

    def testInequality(self):
        sample_victim: victim.Victim = CreateSampleVictim()
        sample_victim.initial_RPM_number += 1

        self.assertNotEqual(sample_victim, self.sample_victim)

    def testCalculateRPM(self):
        sample_victim_RPM: int = 6

        self.assertEqual(self.sample_victim.CalculateRPM(), sample_victim_RPM)

    def testGetScoreFromLookUpTables(self):
        test_arguments_pair_1: Tuple[int, int] = (30, 3)
        test_arguments_pair_2: Tuple[int, int] = (40, 2)

        self.CompareScoreFromRespiratoryLookUpTableAndSampleScore(test_arguments_pair_1)
        self.CompareScoreFromRespiratoryLookUpTableAndSampleScore(test_arguments_pair_2)

    def CompareScoreFromRespiratoryLookUpTableAndSampleScore(self, arguments_pair: Tuple[int, int]):
        sample_respiratory_rate, sample_score_for_respiratory = arguments_pair

        self.assertEqual(
            victim.Victim.GetScoreFromLookUpTables(sample_respiratory_rate, victim.RESPIRATORY_RATE_SCORES),
            sample_score_for_respiratory
        )

    def testGetBestMotorResponseScore(self):
        sample_victim_motor_best_response_score: int = 3

        self.assertEqual(self.sample_victim.GetBestMotorResponseScore(), sample_victim_motor_best_response_score)

    def testFromString(self):
        victim_from_string: victim.Victim = victim.Victim.FromString(self.sample_profile_text, 1)

        self.assertEqual(
            victim_from_string,
            self.sample_victim
        )

    def testTryGetTransitionDataFromStringSucceeded(self):
        sample_state_with_transition: str = self.sample_profile_text.split("\n\n")[1]
        sample_state_lines: List[str] = sample_state_with_transition.split("\n")
        sample_transition_data: victim.TransitionData = CreateSampleTransitionData()

        self.assertEqual(
            victim.Victim.TryGetTransitionDataFromString(
                sample_state_lines, victim.State.FromString(sample_state_lines).number
            ),
            sample_transition_data
        )

    def testTryGetTransitionDataFromStringFailed(self):
        sample_state_without_transition: str = self.sample_profile_text.split("\n\n")[0]
        sample_state_lines: List[str] = sample_state_without_transition.split("\n")

        self.assertIsNone(
            victim.Victim.TryGetTransitionDataFromString(
                sample_state_lines, victim.State.FromString(sample_state_lines).number
            )
        )

    def testSaveTransitionDataInProperState(self):
        sample_transition_data: victim.TransitionData = CreateSampleTransitionData()
        sample_states: List[victim.State] = CreateStatesForSampleVictim()
        sample_states[0].timed_next_state_transition = sample_states[0].intervention_next_state_transition = None

        states_with_changes: List[victim.State] = victim.Victim.SaveTransitionDataInProperState(
            sample_transition_data, sample_states
        )

        self.assertEqual(
            states_with_changes[0].timed_next_state_transition,
            SampleTimedNextStateTransition()
        )

    def testLowerRPMWrongInterval(self):
        RPM_before: int = self.sample_victim.current_RPM_number
        sample_time_from_simulation_start: int = victim.RPM_DETERIORATION_INTERVAL_MINUTES + 1
        self.sample_victim.LowerRPM(sample_time_from_simulation_start)

        self.assertEqual(self.sample_victim.current_RPM_number, RPM_before)

    def testLowerRPMAdmittedToTheHospital(self):
        RPM_before: int = self.sample_victim.current_RPM_number
        sample_time_from_simulation_start: int = victim.RPM_DETERIORATION_INTERVAL_MINUTES
        self.sample_victim.AdmitToHospital(sample_time_from_simulation_start)
        self.sample_victim.LowerRPM(sample_time_from_simulation_start)

        self.assertEqual(self.sample_victim.current_RPM_number, RPM_before)

    def testLowerRPMCorrectInterval(self):
        RPM_number_after_one_interval: int = 4  # od RPM = 6
        sample_time_from_simulation_start = victim.RPM_DETERIORATION_INTERVAL_MINUTES
        self.sample_victim.LowerRPM(sample_time_from_simulation_start)

        self.assertEqual(self.sample_victim.current_RPM_number, RPM_number_after_one_interval)

    def testLowerRPMStateDeterioration(self):
        time_needed_for_deterioration: int = SampleTimedNextStateTransition()[0]
        self.sample_victim.LowerRPM(
            RoundNUpToNearestMultipleOfM(time_needed_for_deterioration, victim.RPM_DETERIORATION_INTERVAL_MINUTES)
        )

        self.assertEqual(self.sample_victim.current_state.number, 2)

    def testLowerRPMNoStateChangeRPMEquals0(self):
        sample_time_from_simulation_start = victim.RPM_DETERIORATION_INTERVAL_MINUTES
        self.sample_victim.current_RPM_number = self.sample_victim.initial_RPM_number = 1
        self.sample_victim.LowerRPM(sample_time_from_simulation_start)

        self.assertEqual(self.sample_victim.current_RPM_number, 0)
        self.assertEqual(self.sample_victim.current_state.number, 1)
        self.assertEqual(self.sample_victim.IsDead(), True)

    def testChangeStateWrongNumber(self):
        wrong_state_number: int = 4

        self.assertRaises(
            ValueError,
            self.sample_victim.ChangeState, wrong_state_number
        )

    def testChangeStateCorrectNumber(self):
        new_state_number: int = 3
        self.sample_victim.ChangeState(new_state_number)

        self.assertEqual(self.sample_victim.current_state.number, new_state_number)
        self.assertEqual(self.sample_victim.procedures_performed_so_far, [])
        self.assertEqual(self.sample_victim.current_RPM_number, 7)
        self.assertEqual(self.sample_victim.initial_RPM_number, 7)

    def testAdmitToHospital(self):
        self.assertIsNone(self.sample_victim.hospital_admittance_time)
        sample_time: int = 7
        self.sample_victim.AdmitToHospital(sample_time)

        self.assertEqual(self.sample_victim.hospital_admittance_time, sample_time)
        self.assertEqual(self.sample_victim.HasBeenAdmittedToHospital(), True)

    def testGetCurrentHealthProblemDisciplines(self):
        self.assertEqual(self.sample_victim.GetCurrentHealthProblemDisciplines(), SampleHealthProblemDisciplines())

    def testIsDeadFalse(self):
        self.assertEqual(self.sample_victim.IsDead(), False)

    def testIsDeadTrue(self):
        self.sample_victim.current_state.triage_colour = victim.TriageColour.BLACK

        self.assertEqual(self.sample_victim.IsDead(), True)

    def testPerformProcedureOnMeAllNeededOnes(self):
        health_problems = SampleCriticalHealthProblems()
        self.sample_victim.PerformProcedureOnMe(victim.Procedure(health_problems[0], 1))
        self.sample_victim.PerformProcedureOnMe(victim.Procedure(health_problems[1], 1))

        self.assertEqual(self.sample_victim.current_state.number, 3)
        self.assertEqual(self.sample_victim.under_procedure, False)

    def testPerformProcedureOnMeOnlyOneProcedure(self):
        health_problems = SampleCriticalHealthProblems()
        sample_procedure: victim.Procedure = victim.Procedure(health_problems[0], 1)
        self.sample_victim.PerformProcedureOnMe(sample_procedure)

        self.assertEqual(self.sample_victim.procedures_performed_so_far, [sample_procedure])
        self.assertEqual(self.sample_victim.current_state.number, 1)
        self.assertEqual(self.sample_victim.under_procedure, False)

    def testPerformProcedureOnMeWrongProcedure(self):
        health_problems = SampleCriticalHealthProblems()
        sample_procedure: victim.Procedure = victim.Procedure.FromDisciplineAndNumber(
            health_problems[0].discipline, -1, 1)

        self.assertRaises(
            RuntimeError,
            self.sample_victim.PerformProcedureOnMe, sample_procedure
        )
        self.assertEqual(self.sample_victim.under_procedure, False)

    def testGetCurrentCriticalHealthProblems(self):
        sample_critical_health_problems: List[victim.HealthProblem] = SampleCriticalHealthProblems()

        self.assertEqual(
            self.sample_victim.GetCurrentCriticalHealthProblems(),
            set(sample_critical_health_problems)
        )

    def testGetCurrentCriticalHealthProblemsOneFixed(self):
        sample_critical_health_problems: List[victim.HealthProblem] = SampleCriticalHealthProblems()
        self.sample_victim.PerformProcedureOnMe(
            victim.Procedure(sample_critical_health_problems[0], 1)
        )

        self.assertEqual(
            self.sample_victim.GetCurrentCriticalHealthProblems(),
            {sample_critical_health_problems[1]}
        )

    def testGetCurrentCriticalHealthProblemsNoAvailable(self):
        sample_critical_health_problems: List[victim.HealthProblem] = SampleCriticalHealthProblems()
        for health_problem in sample_critical_health_problems:
            self.sample_victim.PerformProcedureOnMe(
                victim.Procedure(health_problem, 1)
            )

        self.assertEqual(self.sample_victim.GetCurrentCriticalHealthProblems(), set())


def CreateSampleStateLines() -> List[str]:
    sample_profile_file: str = "../Profile pacjentów/Czerwony/Profil5.txt"
    with open(sample_profile_file, encoding="utf-8") as f:
        sample_profile_text: str = f.read()
    sample_state_text: str = sample_profile_text.split("\n\n")[0]
    return sample_state_text.split("\n")


class StateClassTests(unittest.TestCase):
    def testCheckInitArguments(self):
        victim.State.CheckInitArguments(1, 0, 0)

        self.assertRaises(
            ValueError,
            victim.State.CheckInitArguments, 1, 0, -1
        )
        self.assertRaises(
            ValueError,
            victim.State.CheckInitArguments, 1, -1, 0
        )
        self.assertRaises(
            ValueError,
            victim.State.CheckInitArguments, 0, 0, 0
        )

    def testEquality(self):
        self.assertEqual(CreateSampleState(), CreateSampleState())

    def testInequality(self):
        self.assertNotEqual(CreateSampleState(), CreateSampleState(no_transitions=True))

    def testGetters(self):
        sample_state: victim.State = CreateSampleState()
        transition_time, transition_new_state = SampleTimedNextStateTransition()

        self.assertEqual(sample_state.GetAllHealthProblemDisciplines(), SampleHealthProblemDisciplines())
        self.assertEqual(sample_state.GetTimeOfDeterioration(), transition_time)
        self.assertEqual(sample_state.GetDeterioratedStateNumber(), transition_new_state)
        self.assertEqual(
            sample_state.GetCriticalHealthProblemNeededToBeFixedForImprovement(),
            SampleCriticalHealthProblems()
        )
        self.assertEqual(sample_state.GetImprovedStateNumber(), 3)

    def testTransitionGettersWhenTransitionsNone(self):
        sample_state: victim.State = CreateSampleState(no_transitions=True)

        self.assertEqual(sample_state.GetTimeOfDeterioration(), None)
        self.assertEqual(sample_state.GetDeterioratedStateNumber(), None)
        self.assertEqual(
            sample_state.GetCriticalHealthProblemNeededToBeFixedForImprovement(),
            []
        )
        self.assertEqual(sample_state.GetImprovedStateNumber(), None)

    def testFromString(self):
        sample_state: victim.State = CreateSampleState(no_transitions=True)

        self.assertEqual(
            victim.State.FromString(CreateSampleStateLines()),
            sample_state
        )

    def testClassGettersFromStrings(self):
        sample_state_lines: List[str] = CreateSampleStateLines()
        sample_state_data_lines: List[str] = sample_state_lines[victim.N_FIRST_LINES_TO_OMIT:]
        State = victim.State
        sample_state: State = CreateSampleState()

        self.assertEqual(
            State.GetIsVictimWalkingFromString(sample_state_data_lines),
            sample_state.is_victim_walking
        )
        self.assertEqual(
            State.GetRespiratoryRateFromString(sample_state_data_lines),
            sample_state.respiratory_rate
        )
        self.assertEqual(
            State.GetPulseRateFromString(sample_state_data_lines),
            sample_state.pulse_rate
        )
        self.assertEqual(
            State.GetIsVictimFollowingOrdersFromString(sample_state_data_lines),
            sample_state.is_victim_following_orders
        )
        self.assertEqual(
            State.GetTriageColourFromString(sample_state_data_lines),
            sample_state.triage_colour
        )
        self.assertEqual(
            State.GetHealthProblemsFromString(sample_state_data_lines),
            sample_state.health_problems
        )
        self.assertEqual(
            State.GetDescriptionFromString(sample_state_data_lines),
            SAMPLE_DESCRIPTION
        )

    def testGettersErrors(self):
        sample_state_lines: List[str] = CreateSampleStateLines()
        sample_state_data_lines: List[str] = sample_state_lines[victim.N_FIRST_LINES_TO_OMIT:]
        sample_state_data_lines[0] = "1; Czy pacjent chodzi?; (tak/nie); 0"  # nie -> 0
        sample_state_data_lines[3] = "4; Czy pacjent spełnia polecenia?; (tak/nie); 1"  # tak -> 1
        sample_state_data_lines[4] = "5; Kolor segregacji; (nazwa koloru); zielony"  # czerwony -> zielony

        self.assertRaises(
            ValueError,
            victim.State.GetIsVictimWalkingFromString, sample_state_data_lines
        )
        self.assertRaises(
            ValueError,
            victim.State.GetIsVictimFollowingOrdersFromString, sample_state_data_lines
        )
        self.assertRaises(
            ValueError,
            victim.State.GetTriageColourFromString, sample_state_data_lines
        )


class HealthProblemClassTests(unittest.TestCase):
    def testFromProcedureString(self):
        sample_health_problem: victim.HealthProblem = victim.HealthProblem(15, 1)

        self.assertEqual(victim.HealthProblem.FromProcedureString("P(15.1)"), sample_health_problem)


def CreateSampleProcedure():
    return victim.Procedure(
        victim.HealthProblem(15, 7), 2
    )


class ProcedureClassTests(unittest.TestCase):
    def testFromString(self):
        sample_procedure: victim.Procedure = CreateSampleProcedure()

        self.assertEqual(
            victim.Procedure.FromString("P(15.7)", "2"),
            sample_procedure
        )

    def testFromDisciplineAndNumber(self):
        sample_procedure: victim.Procedure = CreateSampleProcedure()

        self.assertEqual(
            victim.Procedure.FromDisciplineAndNumber(15, 7, 2),
            sample_procedure
        )


if __name__ == "__main__":
    unittest.main()
