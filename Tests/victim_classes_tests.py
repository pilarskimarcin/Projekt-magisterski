# -*- coding: utf-8 -*-
from typing import List, Tuple
import unittest

from Skrypty.victim_classes import (ConvertRowWithoutFirstElementToInt, HealthProblem, LoadDeteriorationTable,
                                    RESPIRATORY_RATE_SCORES, RPM_DETERIORATION_INTERVAL_MINUTES, State, TriageColour,
                                    Victim)


class FunctionsTests(unittest.TestCase):
    def testLoadingDeteriorationTable(self):
        deterioration_table_length: int = 13
        deterioration_table_row_length: int = 12
        fail_message: str = "Tablica pogorszenia RPM nie zaladowana poprawnie"
        deterioration_table = LoadDeteriorationTable()
        self.assertEqual(len(deterioration_table), deterioration_table_length, fail_message)
        self.assertEqual(len(deterioration_table[0]), deterioration_table_row_length, fail_message)

    def testConvertRowWithoutFirstElementToInt(self):
        sample_string_row: List[str] = ['12', '12', '12', '11', '11', '10', '10', '10', '10', '9', '9', '8', '8']
        sample_result_int_row: List[int] = [12, 12, 11, 11, 10, 10, 10, 10, 9, 9, 8, 8]
        self.assertEqual(
            ConvertRowWithoutFirstElementToInt(sample_string_row),
            sample_result_int_row
        )


class VictimClassTests(unittest.TestCase):
    sample_victim: Victim

    def setUp(self):
        sample_state: State = State(
            number=1, is_victim_walking=False, respiratory_rate=12, pulse_rate=120, is_victim_following_orders=True,
            triage_colour=TriageColour.YELLOW, health_problems_ids=(HealthProblem(15, 3)),
            description=u"Kobieta lat 15 zgłasza problem z poruszaniem się, twierdzi że nie jest w stanie przejść, "
                        u"podczas próby pionizacji twierdzi ze nie czuje nóg. Nie zgłasza dolegliwości bólowych, neguje"
                        u" asymetrie czucia, twierdzi że nie ma sił. Nie jest w stanie ustać na nogach."
        )
        self.sample_victim: Victim = Victim(1, tuple([sample_state]))

    def testCalculateRPM(self):
        sample_victim_RPM: int = 11
        self.assertEqual(self.sample_victim.CalculateRPM(), sample_victim_RPM)

    def testGetScoreFromLookUpTables(self):
        test_arguments_pair_1: Tuple[int, int] = (30, 3)
        test_arguments_pair_2: Tuple[int, int] = (40, 2)
        self.CompareScoreFromRespiratoryLookUpTableAndSampleScore(test_arguments_pair_1)
        self.CompareScoreFromRespiratoryLookUpTableAndSampleScore(test_arguments_pair_2)

    def CompareScoreFromRespiratoryLookUpTableAndSampleScore(self, arguments_pair: Tuple[int, int]):
        sample_respiratory_rate, sample_score_for_respiratory = arguments_pair
        self.assertEqual(
            Victim.GetScoreFromLookUpTables(sample_respiratory_rate, RESPIRATORY_RATE_SCORES),
            sample_score_for_respiratory
        )

    def testGetBestMotorResponseScore(self):
        sample_victim_motor_best_response_score: int = 3
        self.assertEqual(self.sample_victim.GetBestMotorResponseScore(), sample_victim_motor_best_response_score)

    def testLowerRPM(self):
        sample_time_from_simulation_start: int = RPM_DETERIORATION_INTERVAL_MINUTES + 1
        self.assertRaises(ValueError, self.sample_victim.LowerRPM, sample_time_from_simulation_start)
        self.sample_victim.initial_RPM_number = 7
        self.sample_victim.current_RPM_number = 7
        sample_time_from_simulation_start = RPM_DETERIORATION_INTERVAL_MINUTES
        self.sample_victim.LowerRPM(sample_time_from_simulation_start)
        self.assertEqual(self.sample_victim.current_RPM_number, 6)
        sample_time_from_simulation_start += RPM_DETERIORATION_INTERVAL_MINUTES * 5
        self.sample_victim.LowerRPM(sample_time_from_simulation_start)
        self.assertEqual(self.sample_victim.current_RPM_number, 1)


class StateClassTests(unittest.TestCase):
    def testCheckInitArguments(self):
        State.CheckInitArguments(1, 0, 0)
        self.assertRaises(ValueError, State.CheckInitArguments, 1, 0, -1)
        self.assertRaises(ValueError, State.CheckInitArguments, 1, -1, 0)
        self.assertRaises(ValueError, State.CheckInitArguments, 0, 0, 0)


if __name__ == '__main__':
    unittest.main()
