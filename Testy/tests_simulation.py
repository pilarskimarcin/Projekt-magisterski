# -*- coding: utf-8 -*-
import random
from typing import List, Optional, Tuple
import unittest

from Skrypty import simulation as sim
from Skrypty import sor_classes as sor
from Skrypty import utilities as util
from Skrypty import victim_classes as victim
from Skrypty import zrm_classes as zrm
from Testy import tests_scenario_classes as tests_scenario
from Testy import tests_utilities as tests_util
from Testy import tests_victim_classes as tests_victim
from Testy import tests_zrm_classes as tests_zrm


def ReconnaissanceProcedure():
    return victim.Procedure.FromDisciplineAndNumber(
        0, 0, 5
    )


class TestSimulation(unittest.TestCase):
    simulation: sim.Simulation

    def setUp(self):
        self.simulation = sim.Simulation(
            "../Scenariusze/Scenariusz 2.txt", ["../Scenariusze/Scenariusz 1.txt"]
        )

    def testInit(self):
        self.assertEqual(len(self.simulation.additional_scenarios), 1)
        self.assertEqual(len(self.simulation.incidents), 1)
        self.assertEqual(len(self.simulation.all_hospitals), 10)
        self.assertEqual(len(self.simulation.idle_teams), 23)
        self.assertEqual(len(self.simulation.teams_in_action), 0)
        self.assertEqual(len(self.simulation.all_victims), 90)
        self.assertEqual(len(self.simulation.incidents[0].victims), 90)
        self.assertEqual(
            self.simulation.incidents[0].address.address_for_places_data, "Głowackiego 91 32-540 Trzebinia"
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

    def testSendOutNTeamsToTheIncidentReturnFirstLessThanMaxTeams(self):
        sample_reported_victims_count: int = 15
        self.simulation.incidents[0].reported_victims_count = sample_reported_victims_count
        self.simulation.SendOutNTeamsToTheIncidentReturnFirst(
            self.simulation.incidents[0],
            sample_reported_victims_count
        )

        self.assertEqual(self.GetCountOfDrivingTeams(), sample_reported_victims_count)

    def GetCountOfDrivingTeams(self) -> int:
        count: int = 0
        for team in self.simulation.teams_in_action:
            if team.IsDriving():
                count += 1
        return count

    def testSendOutNTeamsToTheIncidentReturnFirstMaxTeams(self):
        sample_reported_victims_count: int = 28
        self.simulation.incidents[0].reported_victims_count = sample_reported_victims_count
        self.simulation.SendOutNTeamsToTheIncidentReturnFirst(
            self.simulation.incidents[0],
            sample_reported_victims_count
        )

        self.assertEqual(self.GetCountOfDrivingTeams(), len(self.simulation.teams_in_action))

    def testTeamIntoAction(self):
        sample_team: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(sample_team)

        self.assertFalse(sample_team in self.simulation.idle_teams)
        self.assertTrue(sample_team in self.simulation.teams_in_action)

    def testTeamsAndTimesToReachTheIncidentAsc(self):
        sample_teams_times_to_reach_incident: List[Tuple[str, float]] = [
            ('K01 47', 3.9166666666666665), ('K01 098', 3.9166666666666665), ('K01 100', 5.616666666666666),
            ('K01 102', 15.2), ('K01 104', 18.666666666666668), ('K01 032', 21.033333333333335),
            ('K01 138', 21.033333333333335), ('S02 242', 21.816666666666666), ('S02 214', 21.816666666666666),
            ('S02 212', 21.816666666666666), ('K01 152', 27.066666666666666), ('S02 350', 27.55), ('S02 352', 27.55),
            ('K01 116', 28.65), ('K01 43', 29.55), ('S02 308', 31.25), ('K01 154', 31.35),
            ('K01 07', 31.683333333333334), ('S02 313', 31.983333333333334), ('S02 348', 31.983333333333334),
            ('K01 022', 32.85), ('K01 142', 33.18333333333333), ('K01 112', 33.18333333333333)
        ]

        self.assertEqual(
            self.simulation.TeamsAndTimesToReachTheIncidentAsc(self.simulation.incidents[0]),
            sample_teams_times_to_reach_incident
        )

    def testGetTeamById(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()

        self.assertEqual(sample_team, self.simulation.GetTeamById(sample_team.id_))

    def testSimulationRegularStep(self):
        setup_values: Tuple[int, int, int, int] = self.SimulationRegularStepTestSetup()
        self.simulation.SimulationRegularStep()

        self.AssertSimulationRegularStepEndedSuccessfully(setup_values)

    def SimulationRegularStepTestSetup(self):
        elapsed_time_before: int = self.simulation.elapsed_simulation_time
        sample_destination: util.TargetDestination = util.TargetDestination(tests_util.CreateSampleAddressIncident())
        first_zrm: zrm.ZRM = self.simulation.idle_teams[0]
        sample_zrm_with_specialists_outside: zrm.ZRM = self.simulation.idle_teams[1]

        first_zrm.StartDriving(sample_destination)
        sample_time_to_destination: int = first_zrm.time_until_destination_in_minutes
        self.simulation.TeamIntoAction(first_zrm)

        sample_zrm_with_specialists_outside.SpecialistsLeaveTheVehicle()
        self.simulation.TeamIntoAction(sample_zrm_with_specialists_outside)
        sample_zrm_with_specialists_outside.specialists[0].StartPerformingProcedure(
            tests_victim.CreateSampleProcedure()
        )
        sample_time_to_finish_procedure: int = (sample_zrm_with_specialists_outside.specialists[0].
                                                time_until_procedure_is_finished)
        sample_victim_previous_RPM: int = self.simulation.all_victims[0].current_RPM_number
        return (elapsed_time_before, sample_time_to_destination, sample_time_to_finish_procedure,
                sample_victim_previous_RPM)

    def AssertSimulationRegularStepEndedSuccessfully(self, setup_values: Tuple[int, int, int, int]):
        (elapsed_time_before, sample_time_to_destination, sample_time_to_finish_procedure,
         sample_victim_previous_RPM) = setup_values

        self.assertEqual(self.simulation.elapsed_simulation_time, elapsed_time_before + 1)
        self.assertEqual(
            self.simulation.teams_in_action[0].time_until_destination_in_minutes,
            sample_time_to_destination - 1
        )
        self.assertEqual(
            self.simulation.teams_in_action[1].specialists[0].time_until_procedure_is_finished,
            sample_time_to_finish_procedure - 1
        )
        self.assertEqual(self.simulation.all_victims[0].current_RPM_number, sample_victim_previous_RPM)

    def testMoveTeamNotFinished(self):
        sample_team, _ = self.TeamStartDrivingWithVictim()
        sample_time_to_destination_before: int = sample_team.time_until_destination_in_minutes
        self.simulation.MoveTeam(sample_team)

        self.assertEqual(
            sample_team.time_until_destination_in_minutes,
            sample_time_to_destination_before - 1
        )

    def TeamStartDrivingWithVictim(self, hospital_target: bool = False) -> Tuple[zrm.ZRM, victim.Victim]:
        if hospital_target:
            sample_destination: sor.Hospital = tests_scenario.CreateSampleHospital()
        else:
            sample_destination: util.TargetDestination = util.TargetDestination(
                tests_util.CreateSampleAddressIncident()
            )
        sample_team: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(sample_team)
        sample_victim: victim.Victim = tests_victim.CreateSampleVictim()
        sample_team.StartTransportingAVictim(sample_victim, sample_destination)
        return sample_team, sample_victim

    def testMoveTeamFinishedInHospital(self):
        sample_team, sample_victim = self.TeamStartDrivingWithVictim(hospital_target=True)
        sample_team.time_until_destination_in_minutes = 2
        self.simulation.MoveTeam(sample_team)
        self.simulation.MoveTeam(sample_team)

        self.assertEqual(sample_team.time_until_destination_in_minutes, None)
        self.assertIsNotNone(sample_victim.hospital_admittance_time)

    def testMoveTeamFinishedNotInHospitalError(self):
        sample_team, sample_victim = self.TeamStartDrivingWithVictim(hospital_target=False)
        self.simulation.MoveTeam(sample_team)
        self.assertRaises(RuntimeError, self.simulation.MoveTeam, sample_team)

    def testTryHandleReconnaissanceFalse(self):
        self.simulation.incidents[0].reported_victims_count = len(self.simulation.incidents[0].victims)
        first_ZRM: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_ZRM)
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])

        self.assertFalse(first_ZRM.are_specialists_outside)
        self.assertIsNone(first_ZRM.specialists[0].stored_procedure)

    def testTryHandleReconnaissanceTrueIsDriving(self):
        first_ZRM: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_ZRM)
        first_ZRM.StartDriving(self.simulation.incidents[0])
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])

        self.assertFalse(first_ZRM.are_specialists_outside)
        self.assertIsNone(first_ZRM.specialists[0].stored_procedure)
        self.assertTrue(self.simulation.incidents[0].NeedsReconnaissance())

    def testTryHandleReconnaissanceTrueNotDrivingStartReconnaissance(self):
        first_ZRM: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_ZRM)
        first_ZRM.StartDriving(self.simulation.incidents[0])
        first_ZRM.FinishDrivingAndReturnVictim()
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])

        self.assertTrue(first_ZRM.are_specialists_outside)
        self.assertEqual(first_ZRM.specialists[0].stored_procedure, ReconnaissanceProcedure())
        self.assertTrue(self.simulation.incidents[0].NeedsReconnaissance())

    def testTryHandleReconnaissanceTrueFinishedReconnaissance(self):
        first_ZRM: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_ZRM)
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])
        for specialist in first_ZRM.specialists:
            specialist.is_idle = True
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])

        self.assertFalse(self.simulation.incidents[0].NeedsReconnaissance())

    def testPerformReconnaissance(self):
        first_team: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_team)
        self.simulation.PerformReconnaissance(first_team)

        self.assertEqual(first_team.specialists[0].stored_procedure, ReconnaissanceProcedure())
        self.assertEqual(first_team.specialists[0].is_idle, False)
        self.assertEqual(first_team.are_specialists_outside, True)

    def testGetProcedureByDisciplineAndNumber(self):
        reconnaissance_procedure: victim.Procedure = ReconnaissanceProcedure()

        self.assertEqual(
            self.simulation.GetProcedureByDisciplineAndNumber(0, 0),
            reconnaissance_procedure
        )

    def testCheckIfSimulationEndReachedTrue(self):
        self.SimulationEndSetup()

        self.assertTrue(self.simulation.CheckIfSimulationEndReached())

    def SimulationEndSetup(self):
        sample_time: int = 1
        for victim_ in self.simulation.all_victims:
            victim_.Assess()
            if not victim_.IsDead():
                victim_.AdmitToHospital(sample_time)

    def testCheckIfSimulationEndReachedNotAssessed(self):
        self.SimulationEndSetup()
        self.RandomVictim().has_been_assessed = False

        self.assertFalse(self.simulation.CheckIfSimulationEndReached())

    def RandomVictim(self) -> victim.Victim:
        random_victim: Optional[victim.Victim] = None
        while not random_victim or random_victim.IsDead():
            random_index: int = random.randint(0, len(self.simulation.all_victims) - 1)
            random_victim = self.simulation.all_victims[random_index]
        return random_victim

    def testCheckIfSimulationEndReachedNotAdmittedToHospital(self):
        self.SimulationEndSetup()
        self.RandomVictim().hospital_admittance_time = None

        self.assertFalse(self.simulation.CheckIfSimulationEndReached())


if __name__ == '__main__':
    unittest.main()
