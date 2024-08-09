import unittest
from Skrypty.victim_classes import LoadDeteriorationTable


class FunctionsTests(unittest.TestCase):
    def TestLoadingDeteriorationTable(self):
        DETERIORATION_TABLE_LENGTH: int = 13
        DETERIORATION_TABLE_ROW_LENGTH: int = 12
        fail_message: str = "Tablica pogorszenia RPM nie zaladowana poprawnie"
        deterioration_table = LoadDeteriorationTable()
        self.assertEquals(len(deterioration_table), DETERIORATION_TABLE_LENGTH, fail_message)
        self.assertEquals(len(deterioration_table[0]), DETERIORATION_TABLE_ROW_LENGTH, fail_message)

    def TestConvertRowWithoutFirstElementToInt(self):
        # TODO
        raise NotImplementedError


class VictimClassTests(unittest.TestCase):
    # TODO: testy Victim, init i metody
    pass


class StateClassTests(unittest.TestCase):
    # TODO: testy State, init i metody
    pass


if __name__ == '__main__':
    unittest.main()
