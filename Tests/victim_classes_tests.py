from typing import List
import unittest

from Skrypty.victim_classes import ConvertRowWithoutFirstElementToInt, LoadDeteriorationTable, State, Victim


class FunctionsTests(unittest.TestCase):
    def testLoadingDeteriorationTable(self):
        deterioration_table_length: int = 13
        deterioration_table_row_length: int = 12
        fail_message: str = "Tablica pogorszenia RPM nie zaladowana poprawnie"
        deterioration_table = LoadDeteriorationTable()
        self.assertEquals(len(deterioration_table), deterioration_table_length, fail_message)
        self.assertEquals(len(deterioration_table[0]), deterioration_table_row_length, fail_message)

    def testConvertRowWithoutFirstElementToInt(self):
        sample_string_row: List[str] = ['12', '12', '12', '11', '11', '10', '10', '10', '10', '9', '9', '8', '8']
        self.assertEquals(
            ConvertRowWithoutFirstElementToInt(sample_string_row),
            [12, 12, 11, 11, 10, 10, 10, 10, 9, 9, 8, 8]
        )


class VictimClassTests(unittest.TestCase):
    # TODO: testy Victim, init i metody
    pass


class StateClassTests(unittest.TestCase):
    def testCheckInitArguments(self):
        State.CheckInitArguments(1, 0, 0)
        self.assertRaises(ValueError, State.CheckInitArguments, 1, 0, -1)
        self.assertRaises(ValueError, State.CheckInitArguments, 1, -1, 0)
        self.assertRaises(ValueError, State.CheckInitArguments, 0, 0, 0)


if __name__ == '__main__':
    unittest.main()
