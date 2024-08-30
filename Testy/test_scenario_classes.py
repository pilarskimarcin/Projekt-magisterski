# -*- coding: utf-8 -*-
from typing import List, Tuple
import unittest

from Skrypty import scenario_classes as scenario
from Skrypty import sor_classes as sor
from Skrypty import utilities as util
from Skrypty import victim_classes as victim
from Skrypty import zrm_classes as zrm


def CreateSampleScenarioData() -> Tuple[sor.Hospital, list[zrm.ZRM], list[victim.Victim], util.PlaceAddress]:
    sample_departments: List[sor.Department] = [
        sor.Department(id_=1, name="Oddział chirurgii urazowo-ortopedycznej", medical_categories=[25],
                       current_beds_count=22),
        sor.Department(id_=2, name="Oddział kardiologiczny", medical_categories=[53],
                       current_beds_count=31),
        sor.Department(id_=3, name="Oddział anestezjologii i intensywnej terapii", medical_categories=[1],
                       current_beds_count=9),
        sor.Department(id_=4, name="Oddział chirurgii naczyniowej", medical_categories=[39, 37],
                       current_beds_count=15),
        sor.Department(id_=5, name="Oddział neurologiczny z pododziałem udarowym", medical_categories=[22],
                       current_beds_count=15),
        sor.Department(id_=6, name="Szpitalny Oddział Ratunkowy", medical_categories=[15],
                       current_beds_count=12),
        sor.Department(id_=7, name="Pododdział udarowy", medical_categories=[22],
                       current_beds_count=16)
    ]
    sample_address: util.PlaceAddress = util.PlaceAddress("Topolowa", 16, "32-500", "Chrzanów")
    sample_hospital: sor.Hospital = sor.Hospital(
        id_=1, name="Szpital Powiatowy w Chrzanowie",
        address=sample_address,
        departments=sample_departments
    )
    sample_teams: List[zrm.ZRM] = [
        zrm.ZRM(id_="K01 47", dispatch="DM06-01", zrm_type=zrm.ZRMType.S, base_location=sample_address),
        zrm.ZRM(id_="K01 098", dispatch="DM06-01", zrm_type=zrm.ZRMType.P, base_location=sample_address)
    ]
    sample_state1: victim.State = victim.State(
        number=1, is_victim_walking=False, respiratory_rate=12, pulse_rate=120, is_victim_following_orders=True,
        triage_colour=victim.TriageColour.YELLOW,
        health_problems_ids=(
            victim.HealthProblem(25, 1), victim.HealthProblem(25, 4)
        ),
        description=u"Kobieta lat 17 zgłasza problem z poruszaniem się, na prośbę o opuszczenie strefy "
                    u"niebezpiecznej, zgłasza ból w obrębie stawu kolanowego, dolegliwości uniemożliwiają "
                    u"samodzielne poruszanie się, dolegliwości bólowe w obrębie stawu barkowego (widoczna "
                    u"asymetria barku lewego w stosunku do prawego, bolesność palpacyjna)."
    )
    sample_state2: victim.State = victim.State(
        number=1, is_victim_walking=False, respiratory_rate=12, pulse_rate=130, is_victim_following_orders=True,
        triage_colour=victim.TriageColour.YELLOW,
        health_problems_ids=(
            victim.HealthProblem(25, 2)
        ),
        description=u"Mężczyzna lat 13 zgłasza problem z poruszaniem się, na prośbę o opuszczenie strefy "
                    u"niebezpiecznej, zgłasza ból w obrębie piszczeli prawej, widoczna deformacja, widoczny uraz "
                    u"głowy nie wymagający interwencji chirurgicznej."
    )
    sample_victims: List[victim.Victim] = [
        victim.Victim(1, tuple([sample_state1])), victim.Victim(2, tuple([sample_state1])),
        victim.Victim(3, tuple([sample_state2])), victim.Victim(4, tuple([sample_state2])),
    ]
    sample_address2: util.PlaceAddress = util.PlaceAddress("Magnoliowa", 10, "32-500", "Chrzanów")
    return sample_hospital, sample_teams, sample_victims, sample_address2


class TestScenario(unittest.TestCase):

    def setUp(self):
        self.sample_scenario = scenario.Scenario("../Scenariusze/Scenariusz 1.txt")

    def testInit(self):
        sample_hospital, sample_teams, sample_victims, sample_address = CreateSampleScenarioData()
        self.assertEqual(self.sample_scenario.hospitals, [sample_hospital])
        self.assertEqual(self.sample_scenario.teams, sample_teams)
        self.assertEqual(self.sample_scenario.victims, sample_victims)
        self.assertEqual(self.sample_scenario.address, sample_address)

    def testParseDepartments(self):
        raise NotImplementedError

    def testParseTeams(self):
        raise NotImplementedError

    def testParseVictims(self):
        raise NotImplementedError

    def testParseAddress(self):
        raise NotImplementedError


if __name__ == '__main__':
    unittest.main()
