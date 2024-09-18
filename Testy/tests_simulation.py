# -*- coding: utf-8 -*-
import random
from typing import List, Tuple
import unittest

from Skrypty import simulation as sim
from Skrypty import victim_classes as victim
from Skrypty import zrm_classes as zrm
from Testy import tests_zrm_classes as tests_zrm


class TestSimulation(unittest.TestCase):
    simulation: sim.Simulation

    def setUp(self):
        self.simulation = sim.Simulation(
            "../Scenariusze/Scenariusz 2.txt", ["../Scenariusze/Scenariusz 1.txt"]
        )

    def testInit(self):
        self.assertEqual(len(self.simulation.additional_scenarios), 1)
        self.assertEqual(self.simulation.additional_incidents, [])
        self.assertEqual(len(self.simulation.all_hospitals), 10)
        self.assertEqual(len(self.simulation.all_teams), 23)
        self.assertEqual(len(self.simulation.all_victims), 90)
        self.assertEqual(len(self.simulation.main_incident.victims), 90)
        self.assertEqual(
            self.simulation.main_incident.address.address_for_places_data, "Głowackiego 91 32-540 Trzebinia"
        )
        self.assertEqual(len(self.simulation.available_procedures), 14)

    def testLoadProcedures(self):
        disciplines_numbers_times: List[Tuple[int, int]] = [
            (0, 0, 5), (15, 1, 2), (15, 2, 3), (15, 4, 7), (15, 5, 7), (15, 6, 10), (15, 7, 7), (15, 8, 4), (15, 9, 5),
            (15, 10, 5), (15, 11, 4), (15, 12, 3), (15, 13, 5), (15, 14, 5)
        ]
        sample_procedures: List[victim.Procedure] = [
            victim.Procedure.FromDisciplineAndNumber(discipline, number, time)
            for discipline, number, time in disciplines_numbers_times
        ]

        self.assertEqual(self.simulation.LoadProcedures(), sample_procedures)

    def testPerformSimulation(self):
        # TODO
        pass

    def testGetStartingAmountOfVictims(self):
        self.assertTrue(27 <= self.simulation.GetStartingAmountOfVictims() <= 67)

    def testGetTeamById(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()

        self.assertEqual(sample_team, self.simulation.GetTeamById(sample_team.id_))

    def testSendOutFirstTeamsToTheIncidentLessThanMaxTeams(self):
        sample_reported_victims_count: int = 15
        self.simulation.SendOutFirstTeamsToTheIncident(sample_reported_victims_count)

        self.assertEqual(self.GetCountOfDrivingTeams(), sample_reported_victims_count)

    def GetCountOfDrivingTeams(self) -> int:
        count: int = 0
        for team in self.simulation.all_teams:
            if team.IsDriving():
                count += 1
        return count

    def testSendOutFirstTeamsToTheIncidentMaxTeams(self):
        sample_reported_victims_count: int = 28
        self.simulation.SendOutFirstTeamsToTheIncident(sample_reported_victims_count)

        self.assertEqual(self.GetCountOfDrivingTeams(), len(self.simulation.all_teams))

    def testCheckIfSimulationEndReachedTrue(self):
        self.SimulationEndSetup()

        self.assertTrue(self.simulation.CheckIfSimulationEndReached())

    def testCheckIfSimulationEndReachedNotAssessed(self):
        self.SimulationEndSetup()
        self.RandomVictim().has_been_assessed = False

        self.assertFalse(self.simulation.CheckIfSimulationEndReached())

    def RandomVictim(self) -> victim.Victim:
        random_index: int = random.randint(0, len(self.simulation.all_victims) - 1)
        return self.simulation.all_victims[random_index]

    def testCheckIfSimulationEndReachedNotAdmittedToHospital(self):
        self.SimulationEndSetup()
        self.RandomVictim().hospital_admittance_time = None

        self.assertFalse(self.simulation.CheckIfSimulationEndReached())

    def SimulationEndSetup(self):
        sample_time: int = 1
        for victim_ in self.simulation.all_victims:
            victim_.Assess()
            if not victim_.IsDead():
                victim_.AdmitToHospital(sample_time)

    def testSimulationRegularStep(self):
        raise NotImplementedError

    def testMoveTeam(self):
        raise NotImplementedError


if __name__ == '__main__':
    unittest.main()
