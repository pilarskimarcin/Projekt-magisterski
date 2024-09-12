# -*- coding: utf-8 -*-
from typing import List, Tuple
import unittest

from Skrypty import victim_classes as victim

SAMPLE_DESCRIPTION: str = (u"Nieprzytomny pacjent z masywnym urazem potylicy ( krwiaki okularowe) oraz treścią krwistą "
                           u"wypływającą z jamy ustnej -  leży na boku, charczy, krztusi się.  Czynności krytyczne do "
                           u"wykonania:  udrożnienie dróg oddechowych przyrządowo ( intubacja lub alternatywa) oraz "
                           u"transport do oddziału neurochirurgii. W przypadku braku zabezpieczenia dróg przyrządowo "
                           u"30 min od pierwszego kontaktu z ratownikiem – zachłyśnięcie krwią i NZK (cały czas "
                           u"asystolia)  W przypadku transportu do SOR bez zaplecza neurochirurgii – NZK przy "
                           u"przekazaniu. USG: Bez patologii")


def CreateSampleVictim() -> victim.Victim:
    """Profil poszkodowanego - Profil4.txt"""
    return victim.Victim(1, CreateStatesForSampleVictim())


def CreateStatesForSampleVictim() -> List[victim.State]:
    sample_states: List[victim.State] = [
        CreateSampleState(),
        victim.State(
            number=2, is_victim_walking=False, respiratory_rate=0, pulse_rate=0, is_victim_following_orders=False,
            triage_colour=victim.TriageColour.BLACK,
            health_problems_ids=[],
            description=""
        ),
        victim.State(
            number=3, is_victim_walking=False, respiratory_rate=16, pulse_rate=100, is_victim_following_orders=False,
            triage_colour=victim.TriageColour.RED,
            health_problems_ids=[victim.HealthProblem(21, 1)],
            description=""
        )
    ]
    return sample_states


def CreateSampleState(no_transitions: bool = False) -> victim.State:
    sample_state: victim.State = victim.State(
        number=1, is_victim_walking=False, respiratory_rate=26, pulse_rate=120, is_victim_following_orders=False,
        triage_colour=victim.TriageColour.RED,
        health_problems_ids=[
            victim.HealthProblem(15, 1), victim.HealthProblem(21, 1)
        ],
        description=SAMPLE_DESCRIPTION,
        timed_next_state_transition=(40, 2),
        intervention_next_state_transition=(victim.Procedure(victim.HealthProblem(15, 1)), 3)
    )
    if no_transitions:
        sample_state.timed_next_state_transition = sample_state.intervention_next_state_transition = None
    return sample_state


class FunctionsTests(unittest.TestCase):
    def testLoadingDeteriorationTable(self):
        deterioration_table_length: int = 13
        deterioration_table_last_row: List[int] = [12, 12, 11, 11, 10, 10, 10, 10, 9, 9, 8, 8]
        deterioration_table = victim.LoadDeteriorationTable()

        self.assertEqual(len(deterioration_table), deterioration_table_length)
        self.assertEqual(deterioration_table[-1], deterioration_table_last_row)

    def testConvertRowWithoutFirstElementToInt(self):
        sample_string_row: List[str] = ['12', '12', '12', '11', '11', '10', '10', '10', '10', '9', '9', '8', '8']
        sample_result_int_row: List[int] = [12, 12, 11, 11, 10, 10, 10, 10, 9, 9, 8, 8]

        self.assertEqual(
            victim.ConvertRowWithoutFirstElementToInt(sample_string_row),
            sample_result_int_row
        )


class VictimClassTests(unittest.TestCase):
    sample_victim: victim.Victim
    sample_profile_text: str

    def setUp(self):
        self.sample_victim = CreateSampleVictim()
        sample_profile_file: str = "../Profile pacjentów/Czerwony/Profil4.txt"
        with open(sample_profile_file, encoding="utf-8") as f:
            self.sample_profile_text = f.read()

    def testEquality(self):
        sample_victim: victim.Victim = CreateSampleVictim()

        self.assertEqual(sample_victim, self.sample_victim)

    def testInequality(self):
        sample_victim: victim.Victim = CreateSampleVictim()
        sample_victim.initial_RPM_number += 1

        self.assertNotEqual(sample_victim, self.sample_victim)

    def testCalculateRPM(self):
        sample_victim_RPM: int = 7

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
        sample_victim_motor_best_response_score: int = 0

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
        sample_transition_data: victim.TransitionData = victim.TransitionData(
            parent_state_number=1, child_state_number=2, transition_type="czas", transition_condition="40min"
        )

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
        sample_transition_data: victim.TransitionData = victim.TransitionData(
            parent_state_number=1, child_state_number=2, transition_type="czas", transition_condition="40min"
        )
        sample_states: List[victim.State] = CreateStatesForSampleVictim()
        sample_states[0].timed_next_state_transition = sample_states[0].intervention_next_state_transition = None

        states_with_changes: List[victim.State] = victim.Victim.SaveTransitionDataInProperState(
            sample_transition_data, sample_states
        )

        self.assertEqual(
            states_with_changes[0].timed_next_state_transition,
            (40, 2)
        )

    def testLowerRPMWrongInterval(self):
        RPM_before: int = self.sample_victim.current_RPM_number
        sample_time_from_simulation_start: int = victim.RPM_DETERIORATION_INTERVAL_MINUTES + 1
        self.sample_victim.LowerRPM(sample_time_from_simulation_start)

        self.assertEqual(self.sample_victim.current_RPM_number, RPM_before)

    def testLowerRPMCorrectInterval(self):
        RPM_number_after_one_interval: int = 6
        sample_time_from_simulation_start = victim.RPM_DETERIORATION_INTERVAL_MINUTES
        self.sample_victim.LowerRPM(sample_time_from_simulation_start)

        self.assertEqual(self.sample_victim.current_RPM_number, RPM_number_after_one_interval)

    def testLowerRPMStateDeterioration(self):
        time_needed_for_deterioration: int = 40
        self.sample_victim.LowerRPM(time_needed_for_deterioration)

        self.assertEqual(self.sample_victim.current_state.number, 2)

    def testChangeStateWrongNumber(self):
        wrong_state_number: int = 4

        self.assertRaises(ValueError, self.sample_victim.ChangeState, wrong_state_number)

    def testChangeStateCorrectNumber(self):
        new_state_number: int = 3
        self.sample_victim.ChangeState(new_state_number)

        self.assertEqual(self.sample_victim.current_state.number, new_state_number)

    def testAdmitToHospital(self):
        self.assertIsNone(self.sample_victim.hospital_admittance_time)
        sample_time: float = 7.5
        self.sample_victim.AdmitToHospital(sample_time)

        self.assertEqual(self.sample_victim.hospital_admittance_time, sample_time)

    def testGetCurrentHealthProblemIds(self):
        self.assertEqual(self.sample_victim.GetCurrentHealthProblemIds(), tuple([15, 21]))


def CreateSampleStateLines() -> List[str]:
    sample_profile_file: str = "../Profile pacjentów/Czerwony/Profil4.txt"
    with open(sample_profile_file, encoding="utf-8") as f:
        sample_profile_text: str = f.read()
    sample_state_text: str = sample_profile_text.split("\n\n")[0]
    return sample_state_text.split("\n")


class StateClassTests(unittest.TestCase):
    def testCheckInitArguments(self):
        victim.State.CheckInitArguments(1, 0, 0)

        self.assertRaises(ValueError, victim.State.CheckInitArguments, 1, 0, -1)
        self.assertRaises(ValueError, victim.State.CheckInitArguments, 1, -1, 0)
        self.assertRaises(ValueError, victim.State.CheckInitArguments, 0, 0, 0)

    def testEquality(self):
        self.assertEqual(CreateSampleState(), CreateSampleState())

    def testInequality(self):
        self.assertNotEqual(CreateSampleState(), CreateSampleState(no_transitions=True))

    def testGetters(self):
        sample_state: victim.State = CreateSampleState()

        self.assertTupleEqual(
            tuple1=(
                sample_state.GetAllHealthProblemIds(), sample_state.GetTimeOfDeterioration(),
                sample_state.GetDeterioratedStateNumber(), sample_state.GetInterventionNeededForImprovement(),
                sample_state.GetImprovedStateNumber()
            ),
            tuple2=(
                (15, 21), 40,
                2, victim.Procedure(victim.HealthProblem(15, 1)),
                3
            )
        )

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

        self.assertEqual(State.GetIsVictimWalkingFromString(sample_state_data_lines), False)
        self.assertEqual(State.GetRespiratoryRateFromString(sample_state_data_lines), 26)
        self.assertEqual(State.GetPulseRateFromString(sample_state_data_lines), 120)
        self.assertEqual(State.GetIsVictimFollowingOrdersFromString(sample_state_data_lines), False)
        self.assertEqual(State.GetTriageColourFromString(sample_state_data_lines), victim.TriageColour.RED)
        self.assertEqual(State.GetHealthProblemIdsFromString(sample_state_data_lines),
                         [victim.HealthProblem(15, 1), victim.HealthProblem(21, 1)])
        self.assertEqual(State.GetDescriptionFromString(sample_state_data_lines), SAMPLE_DESCRIPTION)


class ProcedureClassTests(unittest.TestCase):
    def testFromString(self):
        sample_procedure: victim.Procedure = victim.Procedure(
            victim.HealthProblem(15, 1)
        )
        self.assertEqual(
            victim.Procedure.FromString("P(15.1)"),
            sample_procedure
        )


if __name__ == '__main__':
    unittest.main()
