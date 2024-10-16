# -*- coding: utf-8 -*-
import random
from typing import List, Optional, Tuple
import unittest

from Skrypty import simulation as sim
from Skrypty import sor_classes as sor
from Skrypty import utilities as util
from Skrypty import victim_classes as victim
from Skrypty import zrm_classes as zrm
from Testy import tests_sor_classes as tests_sor
from Testy import tests_utilities as tests_util
from Testy import tests_victim_classes as tests_victim
from Testy import tests_zrm_classes as tests_zrm


class TestSimulation(unittest.TestCase):
    simulation: sim.Simulation

    def setUp(self):
        self.simulation = sim.Simulation(
            "../Scenariusze/Scenariusz 2.txt"  # , ["../Scenariusze/Scenariusz 1.txt"]
        )

    def testInit(self):
        # self.assertEqual(len(self.simulation.additional_scenarios), 1)
        self.assertEqual(len(self.simulation.incidents), 1)
        self.assertEqual(len(self.simulation.all_hospitals), 10)
        self.assertEqual(len(self.simulation.idle_teams), 23)
        self.assertEqual(len(self.simulation.teams_in_action), 0)
        self.assertEqual(len(self.simulation.all_victims), 90)
        self.assertEqual(len(self.simulation.incidents[0].victims), 90)
        self.assertEqual(
            self.simulation.incidents[0].address.address_for_places_data, "Głowackiego 91 32-540 Trzebinia"
        )
        self.assertEqual(len(self.simulation.available_procedures), 15)
        self.assertEqual(self.simulation.solution, [])

    def testLoadProcedures(self):
        disciplines_numbers_times: List[Tuple[int, int]] = [
            (0, 0, 5), (0, 1, 1), (15, 1, 2), (15, 2, 3), (15, 4, 7), (15, 5, 7), (15, 6, 10), (15, 7, 7), (15, 8, 4),
            (15, 9, 5), (15, 10, 5), (15, 11, 4), (15, 12, 3), (15, 13, 5), (15, 14, 5)
        ]
        sample_procedures: List[victim.Procedure] = [
            victim.Procedure.FromDisciplineAndNumber(discipline, number, time)
            for discipline, number, time in disciplines_numbers_times
        ]

        self.assertEqual(self.simulation.LoadProcedures(), sample_procedures)

    def testPerformSimulation(self):
        # TODO
        raise NotImplementedError

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

    def testTeamsAndTimesToReachTheIncidentAscendingBeginningState(self):
        sample_teams_times_to_reach_incident: List[Tuple[str, float]] = [
            ("K01 47", 3.9166666666666665), ("K01 098", 3.9166666666666665), ("K01 100", 5.616666666666666),
            ("K01 102", 15.2), ("K01 104", 18.666666666666668), ("K01 032", 21.033333333333335),
            ("K01 138", 21.033333333333335), ("S02 242", 21.816666666666666), ("S02 214", 21.816666666666666),
            ("S02 212", 21.816666666666666), ("K01 152", 27.066666666666666), ("S02 350", 27.55), ("S02 352", 27.55),
            ("K01 116", 28.65), ("K01 43", 29.55), ("S02 308", 31.25), ("K01 154", 31.35),
            ("K01 07", 31.683333333333334), ("S02 313", 31.983333333333334), ("S02 348", 31.983333333333334),
            ("K01 022", 32.85), ("K01 142", 33.18333333333333), ("K01 112", 33.18333333333333)
        ]

        self.assertEqual(
            self.simulation.GetTeamsWithoutQueueAndTimesToReachTheAddressAscending(
                self.simulation.idle_teams, self.simulation.incidents[0].address
            ),
            sample_teams_times_to_reach_incident
        )

    def testTeamsAndTimesToReachTheIncidentAscendingRandomState(self):
        """
        Wyczerpuje wszystkie przypadki liczenia czasu dojazdu
        - K01 47 nie brany pod uwagę, bo ma kolejkę zadań,
        - K01 112 jest bliżej niż zwykle, więc inna kolejność,
        - K01 100 jedzie już do szpitala, więc będzie inaczej policzony czas dojazdu,
        - K01 142 nie brany pod uwagę, bo ma specjalistów poza pojazdem
        """
        self.simulation.GetTeamById("K01 47").QueueNewTargetLocation(self.simulation.incidents[0])
        self.MakeIdleTeamClosestToTargetLocation(
            self.simulation.incidents[0], team_id="K01 112"
        )
        self.simulation.GetTeamById("K01 100").StartDriving(self.simulation.all_hospitals[0])
        self.simulation.GetTeamById("K01 142").SpecialistsLeaveTheVehicle()

        sample_teams_times_to_reach_incident: List[Tuple[str, float]] = [
            ("K01 112", 1.0), ("K01 098", 3.9166666666666665), ("K01 100", 9.9166666666666666),
            ("K01 102", 15.2), ("K01 104", 18.666666666666668), ("K01 032", 21.033333333333335),
            ("K01 138", 21.033333333333335), ("S02 242", 21.816666666666666), ("S02 214", 21.816666666666666),
            ("S02 212", 21.816666666666666), ("K01 152", 27.066666666666666), ("S02 350", 27.55), ("S02 352", 27.55),
            ("K01 116", 28.65), ("K01 43", 29.55), ("S02 308", 31.25), ("K01 154", 31.35),
            ("K01 07", 31.683333333333334), ("S02 313", 31.983333333333334), ("S02 348", 31.983333333333334),
            ("K01 022", 32.85)
        ]

        self.assertEqual(
            self.simulation.GetTeamsWithoutQueueAndTimesToReachTheAddressAscending(
                self.simulation.idle_teams, self.simulation.incidents[0].address
            ),
            sample_teams_times_to_reach_incident
        )

    def MakeIdleTeamClosestToTargetLocation(self, target_location: zrm.TargetDestination, team_id: str = None) \
            -> zrm.ZRM:
        if not team_id:
            team_id = random.choice([team.id_ for team in self.simulation.idle_teams])
        closest_team: zrm.ZRM = self.simulation.GetTeamById(team_id)
        closest_team.StartDriving(target_location)
        closest_team.time_until_destination_in_minutes = 1
        return closest_team

    def testGetTeamByIdIdle(self):
        sample_team: zrm.ZRM = self.simulation.idle_teams[0]

        self.assertEqual(sample_team, self.simulation.GetTeamById(sample_team.id_))

    def testGetTeamByIdInAction(self):
        sample_team: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(sample_team)

        self.assertEqual(sample_team, self.simulation.GetTeamById(sample_team.id_))

    def testGetTeamByIdWrongId(self):
        self.assertIsNone(self.simulation.GetTeamById(tests_zrm.BAD_TEAM_ID))

    def testTeamIntoAction(self):
        sample_team: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(sample_team)

        self.assertFalse(sample_team in self.simulation.idle_teams)
        self.assertTrue(sample_team in self.simulation.teams_in_action)

    def testTeamIntoActionAlreadyInAction(self):
        sample_team: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(sample_team)
        prev_idle_teams_count: int = len(self.simulation.idle_teams)
        prev_teams_in_action_count: int = len(self.simulation.teams_in_action)
        self.simulation.TeamIntoAction(sample_team)

        self.assertFalse(sample_team in self.simulation.idle_teams)
        self.assertTrue(sample_team in self.simulation.teams_in_action)
        self.assertEqual(len(self.simulation.idle_teams), prev_idle_teams_count)
        self.assertEqual(len(self.simulation.teams_in_action), prev_teams_in_action_count)

    def testCheckIfSimulationEndReachedTrue(self):
        self.SimulationEndSetup()

        self.assertEqual(self.simulation.CheckIfSimulationEndReached(), True)

    def SimulationEndSetup(self):
        for victim_ in self.simulation.all_victims:
            self.simulation.MoveVictimFromUnknownStatusToAssessed(victim_)
            if not victim_.IsDead():
                self.simulation.MoveVictimFromAssessedToTransportReady(victim_)
        self.simulation.transport_ready_victims.clear()

    def testCheckIfSimulationEndReachedNotAssessed(self):
        self.SimulationEndSetup()
        self.simulation.unknown_status_victims.append(self.RandomAliveVictimFromList(self.simulation.all_victims))

        self.assertEqual(self.simulation.CheckIfSimulationEndReached(), False)

    @staticmethod
    def RandomAliveVictimFromList(victims_list: List[victim.Victim]) -> victim.Victim:
        random_victim: Optional[victim.Victim] = None
        while not random_victim or random_victim.IsDead():
            random_victim = random.choice(victims_list)
        return random_victim

    def testCheckIfSimulationEndReachedNotAdmittedToHospital(self):
        self.SimulationEndSetup()
        self.simulation.transport_ready_victims.append(self.RandomAliveVictimFromList(self.simulation.all_victims))

        self.assertEqual(self.simulation.CheckIfSimulationEndReached(), False)

    def testCheckIfSimulationEndReachedNotDeadLeftInAssessed(self):
        self.SimulationEndSetup()
        self.simulation.assessed_victims.append(self.RandomAliveVictimFromList(self.simulation.all_victims))

        self.assertEqual(self.simulation.CheckIfSimulationEndReached(), False)

    def testAnyRemainingAliveAssessedVictimsNoAssessed(self):
        self.assertEqual(self.simulation.AnyRemainingAliveAssessedVictims(), False)

    def testAnyRemainingAliveAssessedVictimsOnlyDeadAssessed(self):
        self.simulation.assessed_victims = [victim_ for victim_ in self.simulation.assessed_victims if victim_.IsDead()]

        self.assertEqual(self.simulation.AnyRemainingAliveAssessedVictims(), False)

    def testAnyRemainingAliveAssessedVictimsOneAliveAssessed(self):
        self.simulation.assessed_victims = [victim_ for victim_ in self.simulation.assessed_victims if victim_.IsDead()]
        self.simulation.assessed_victims.append(self.RandomAliveVictimFromList(self.simulation.all_victims))

        self.assertEqual(self.simulation.AnyRemainingAliveAssessedVictims(), True)

    def testSimulationTimeProgresses(self):
        setup_values: Tuple[int, int, int, int] = self.SimulationTimeProgressTestSetup()
        self.simulation.SimulationTimeProgresses()

        self.AssertSimulationRegularStepEndedSuccessfully(setup_values)

    def SimulationTimeProgressTestSetup(self) -> Tuple[int, int, int, int]:
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
        sample_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        if hospital_target:
            sample_destination: sor.Hospital = self.simulation.all_hospitals[0]
            sample_victim = self.EnsureThatVictimCanBeAdmittedToHospital(
                sample_victim, sample_destination
            )
        else:
            sample_destination: util.TargetDestination = util.TargetDestination(
                tests_util.CreateSampleAddressIncident()
            )
        sample_team: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(sample_team)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(sample_victim)
        self.simulation.MoveVictimFromAssessedToTransportReady(sample_victim)
        sample_team.StartTransportingAVictim(sample_victim, sample_destination)
        return sample_team, sample_victim

    def EnsureThatVictimCanBeAdmittedToHospital(self, sample_victim: victim.Victim, hospital: sor.Hospital) -> \
            victim.Victim:
        victim_can_be_admitted_to_hospital: bool = False
        while not victim_can_be_admitted_to_hospital:
            sample_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
            for medicine_discipline_id in sample_victim.GetCurrentHealthProblemDisciplines():
                if hospital.TryGetDepartment(medicine_discipline_id):
                    victim_can_be_admitted_to_hospital = True
        return sample_victim

    def testMoveTeamFinishedInHospital(self):
        sample_team, sample_victim = self.TeamStartDrivingWithVictim(hospital_target=True)
        sample_team.time_until_destination_in_minutes = 2
        sample_hospital: sor.Hospital = self.simulation.FindAppropriateAvailableHospital(sample_victim)
        prev_hospital_beds: int = self.GetHospitalCurrentBedsCount(sample_hospital)
        self.simulation.MoveTeam(sample_team)
        self.simulation.MoveTeam(sample_team)

        self.assertIsNone(sample_team.time_until_destination_in_minutes)
        self.assertIsNotNone(sample_victim.hospital_admittance_time)
        self.assertTrue(sample_victim not in self.simulation.transport_ready_victims)
        self.assertEqual(
            self.simulation.solution,
            [(
                1, sample_victim.id_, sample_team.id_, "1-1", self.simulation.elapsed_simulation_time
            )]
        )
        self.assertEqual(self.GetHospitalCurrentBedsCount(sample_hospital), prev_hospital_beds - 1)

    @staticmethod
    def GetHospitalCurrentBedsCount(hospital: sor.Hospital) -> int:
        return sum([department.current_beds_count for department in hospital.departments])

    def testMoveTeamFinishedInHospitalDead(self):
        sample_team, sample_victim = self.TeamStartDrivingWithVictim(hospital_target=True)
        sample_team.time_until_destination_in_minutes = 2
        prev_hospital_beds: int = self.GetHospitalCurrentBedsCount(
            self.simulation.FindAppropriateAvailableHospital(sample_victim)
        )
        sample_victim.current_RPM_number = 0
        sample_victim.current_state.triage_colour = victim.TriageColour.BLACK
        self.simulation.MoveTeam(sample_team)
        self.simulation.MoveTeam(sample_team)

        self.assertIsNone(sample_team.time_until_destination_in_minutes)
        self.assertIsNone(sample_victim.hospital_admittance_time)
        self.assertTrue(sample_victim not in self.simulation.transport_ready_victims)
        self.assertTrue(sample_victim in self.simulation.assessed_victims)
        self.assertEqual(
            self.GetHospitalCurrentBedsCount(self.simulation.FindAppropriateAvailableHospital(sample_victim)),
            prev_hospital_beds
        )

    def testMoveTeamFinishedNotInHospitalError(self):
        sample_team, sample_victim = self.TeamStartDrivingWithVictim(hospital_target=False)
        self.simulation.MoveTeam(sample_team)

        self.assertRaises(
            RuntimeError,
            self.simulation.MoveTeam, sample_team
        )

    def testHospitalAndDepartmentId(self):
        sample_hospital: sor.Hospital = self.simulation.all_hospitals[0]
        sample_department: sor.Department = sample_hospital.departments[0]

        self.assertEqual(
            self.simulation.HospitalAndDepartmentId(sample_hospital, sample_department),
            "1-1"
        )

    def testTryHandleReconnaissanceFalse(self):
        self.simulation.incidents[0].reported_victims_count = len(self.simulation.incidents[0].victims)
        first_ZRM: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_ZRM)
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])

        self.assertEqual(first_ZRM.are_specialists_outside, False)
        self.assertIsNone(first_ZRM.specialists[0].stored_procedure)

    def testTryHandleReconnaissanceTrueIsDriving(self):
        first_ZRM: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_ZRM)
        first_ZRM.StartDriving(self.simulation.incidents[0])
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])

        self.assertEqual(first_ZRM.are_specialists_outside, False)
        self.assertIsNone(first_ZRM.specialists[0].stored_procedure)
        self.assertEqual(self.simulation.incidents[0].NeedsReconnaissance(), True)

    def testTryHandleReconnaissanceTrueNotDrivingStartReconnaissance(self):
        first_ZRM: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_ZRM)
        first_ZRM.StartDriving(self.simulation.incidents[0])
        first_ZRM.FinishDrivingAndReturnVictim()
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])

        self.assertEqual(first_ZRM.are_specialists_outside, True)
        self.assertEqual(
            first_ZRM.specialists[0].stored_procedure, self.simulation.GetReconnaissanceProcedure()
        )
        self.assertEqual(self.simulation.incidents[0].NeedsReconnaissance(), True)

    def testTryHandleReconnaissanceTrueFinishedReconnaissance(self):
        first_ZRM: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_ZRM)
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])
        for specialist in first_ZRM.specialists:
            specialist.is_idle = True
        self.simulation.TryHandleReconnaissance(first_ZRM, self.simulation.incidents[0])

        self.assertEqual(self.simulation.incidents[0].NeedsReconnaissance(), False)

    def testPerformReconnaissance(self):
        first_team: zrm.ZRM = self.simulation.idle_teams[0]
        self.simulation.TeamIntoAction(first_team)
        self.simulation.PerformReconnaissance(first_team)

        self.assertEqual(
            first_team.specialists[0].stored_procedure, self.simulation.GetReconnaissanceProcedure()
        )
        self.assertEqual(first_team.specialists[0].is_idle, False)
        self.assertEqual(first_team.are_specialists_outside, True)

    def testGetReconnaissanceProcedure(self):
        self.assertEqual(
            self.simulation.GetReconnaissanceProcedure(),
            victim.Procedure.FromDisciplineAndNumber(0, 0, 5)
        )

    def testGetProcedureByDisciplineAndNumber(self):
        self.assertEqual(
            self.simulation.GetProcedureByDisciplineAndNumber(15, 6),
            victim.Procedure(victim.HealthProblem(15, 6), 10)
        )

    def testGetProcedureByDisciplineAndNumberNoneFound(self):
        self.assertIsNone(self.simulation.GetProcedureByDisciplineAndNumber(-1, -1))

    def testOrderIdleTeamInActionWithQueue(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        self.simulation.TeamIntoAction(sample_team)
        sample_team.origin_location_address = self.simulation.incidents[0].address
        queued_incident_place: sor.IncidentPlace = tests_sor.CreateSampleIncidentPlace()
        sample_team.QueueNewTargetLocation(queued_incident_place)
        self.AssessAllVictims()
        self.PrepareForTransportAllVictims()
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.OrderIdleTeamInAction(sample_team)

        self.assertEqual(sample_team.are_specialists_outside, False)
        self.assertEqual(sample_team.queue_of_next_targets, [])
        self.assertEqual(sample_team.target_location, queued_incident_place)
        self.assertEqual(sample_team.time_until_destination_in_minutes, 2)
        self.assertEqual(sample_team.transported_victim, None)
        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count)
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count)

    def testOrderIdleTeamInActionTransportReadyVictims(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        self.simulation.TeamIntoAction(sample_team)
        sample_team.origin_location_address = self.simulation.incidents[0].address
        self.AssessAllVictims()
        target_victim: victim.Victim = self.simulation.GetTargetVictimForProcedure()
        hospital_target: sor.Hospital = self.simulation.FindAppropriateAvailableHospital(target_victim)
        for victim_ in self.simulation.all_victims:
            if victim_.current_RPM_number == target_victim.current_RPM_number:
                self.simulation.assessed_victims.remove(victim_)
        self.PrepareForTransportAllVictims()
        self.simulation.transport_ready_victims.append(target_victim)
        n_dead_victims: int = len([victim_ for victim_ in self.simulation.transport_ready_victims if victim_.IsDead()])
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.OrderIdleTeamInAction(sample_team)

        self.assertEqual(sample_team.are_specialists_outside, False)
        self.assertEqual(sample_team.queue_of_next_targets, [])
        self.assertEqual(sample_team.target_location, hospital_target)
        self.assertIsNotNone(sample_team.time_until_destination_in_minutes)
        self.assertEqual(sample_team.transported_victim, target_victim)
        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count + n_dead_victims)
        self.assertEqual(
            len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count - n_dead_victims
        )

    def testOrderIdleTeamInActionAtIncidentPlaceWithNoOrders(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        self.simulation.TeamIntoAction(sample_team)
        sample_team.origin_location_address = self.simulation.incidents[0].address
        self.AssessAllVictims()
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.OrderIdleTeamInAction(sample_team)

        self.assertEqual(sample_team.are_specialists_outside, True)
        self.assertEqual(sample_team.queue_of_next_targets, [])
        self.assertEqual(sample_team.target_location, None)
        self.assertEqual(sample_team.time_until_destination_in_minutes, None)
        self.assertEqual(sample_team.transported_victim, None)
        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count)
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count)

    def testOrderIdleTeamInActionNothingToDoGoToIncident(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        self.simulation.TeamIntoAction(sample_team)
        self.AssessAllVictims()
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.OrderIdleTeamInAction(sample_team)

        self.assertEqual(sample_team.are_specialists_outside, False)
        self.assertEqual(sample_team.queue_of_next_targets, [])
        self.assertEqual(sample_team.target_location, self.simulation.incidents[0])
        self.assertEqual(sample_team.time_until_destination_in_minutes, 3)
        self.assertEqual(sample_team.transported_victim, None)
        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count)
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count)

    def testHandleTransportReadyVictimsNoDeadAndVictimsToTransport(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        self.simulation.TeamIntoAction(sample_team)
        self.AssessAllVictims()
        n_chosen_victims: int = 3
        chosen_victims: List[victim.Victim] = self.GetNAssessedVictimsWithDifferentRPM(n_chosen_victims)
        self.PrepareForTransportAllVictims()
        self.simulation.transport_ready_victims = chosen_victims
        sample_hospital: sor.Hospital = self.simulation.FindAppropriateAvailableHospital(chosen_victims[0])
        sample_hospital.incoming_victims.clear()
        self.simulation.HandleTransportReadyVictims(sample_team)

        self.assertEqual(sample_team.are_specialists_outside, False)
        self.assertEqual(sample_team.transported_victim, chosen_victims[0])
        self.assertEqual(sample_team.target_location, sample_hospital)
        self.assertTrue([chosen_victims[0]] in sample_hospital.incoming_victims.values())

    def GetNAssessedVictimsWithDifferentRPM(self, n_victims: int, target_highest_RPM: bool = False) \
            -> List[victim.Victim]:
        chosen_victims: List[victim.Victim] = []
        while len(chosen_victims) < (n_victims + 1):
            random_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.assessed_victims)
            if random_victim.current_RPM_number not in [
                chosen_victim.current_RPM_number for chosen_victim in chosen_victims
            ] and random_victim.GetCurrentCriticalHealthProblems():
                chosen_victims.append(random_victim)
        self.simulation.SortVictimsListByRPM(chosen_victims, descending=target_highest_RPM)
        return chosen_victims

    def testHandleTransportReadyVictimsFewDeadAndVictimsToTransport(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        n_chosen_victims: int = 3
        n_dead_victims: int = 3
        self.simulation.TeamIntoAction(sample_team)
        self.AssessAllVictims()
        chosen_victims: List[victim.Victim] = self.GetNAssessedVictimsWithDifferentRPM(n_chosen_victims)
        self.PrepareForTransportAllVictims()
        dead_victims: List[victim.Victim] = self.GetNDeadVictims(n_dead_victims)
        self.simulation.transport_ready_victims = chosen_victims + dead_victims
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        sample_hospital: sor.Hospital = self.simulation.FindAppropriateAvailableHospital(chosen_victims[0])
        sample_hospital.incoming_victims.clear()
        self.simulation.HandleTransportReadyVictims(sample_team)

        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(
            len(self.simulation.assessed_victims), prev_assessed_victims_count + n_dead_victims
        )
        self.assertEqual(
            len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count - n_dead_victims
        )
        self.assertEqual(sample_team.are_specialists_outside, False)
        self.assertEqual(sample_team.transported_victim, chosen_victims[0])
        self.assertEqual(sample_team.target_location, sample_hospital)
        self.assertTrue([chosen_victims[0]] in sample_hospital.incoming_victims.values())

    def GetNDeadVictims(self, n_victims: int) -> List[victim.Victim]:
        chosen_victims: List[victim.Victim] = []
        while len(chosen_victims) < n_victims:
            random_victim: victim.Victim = random.choice(self.simulation.all_victims)
            if random_victim.IsDead():
                chosen_victims.append(random_victim)
        return chosen_victims

    def testHandleTransportReadyVictimsNoAppropriateHospitalError(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        self.simulation.all_hospitals.remove(self.FindHospitalById(10))
        self.simulation.all_hospitals.remove(self.FindHospitalById(9))
        target_victim: victim.Victim = self.GetVictimById(25)
        target_victim.current_state.health_problems.remove(victim.HealthProblem(15, 1))
        self.AssessAllVictims()
        self.PrepareForTransportAllVictims()
        self.simulation.transport_ready_victims = [target_victim]

        self.assertRaises(RuntimeError, self.simulation.HandleTransportReadyVictims, sample_team)

    def testFindAppropriateAvailableHospitalFound(self):
        self.simulation.all_hospitals.remove(self.FindHospitalById(10))
        fitting_hospital: sor.Hospital = self.FindHospitalById(9)
        target_victim: victim.Victim = self.GetVictimById(25)
        target_victim.current_state.health_problems.remove(victim.HealthProblem(15, 1))

        self.assertEqual(self.simulation.FindAppropriateAvailableHospital(target_victim), fitting_hospital)
        self.assertTrue([target_victim] in fitting_hospital.incoming_victims.values())

    def FindHospitalById(self, hospital_id: int) -> Optional[sor.Hospital]:
        for hospital in self.simulation.all_hospitals:
            if hospital.id_ == hospital_id:
                return hospital
        return None

    def testFindAppropriateAvailableHospitalNotFound(self):
        self.simulation.all_hospitals.remove(self.FindHospitalById(10))
        self.simulation.all_hospitals.remove(self.FindHospitalById(9))
        target_victim: victim.Victim = self.GetVictimById(25)
        target_victim.current_state.health_problems.remove(victim.HealthProblem(15, 1))

        self.assertEqual(self.simulation.FindAppropriateAvailableHospital(target_victim), None)

    def testSortVictimsListByRPMAscending(self):
        self.simulation.SortVictimsListByRPM(self.simulation.all_victims)

        self.assertEqual(self.IsListOfVictimsSorted(self.simulation.all_victims), True)

    @staticmethod
    def IsListOfVictimsSorted(victims_list: List[victim.Victim], descending: bool = False) -> bool:
        if descending:
            key = lambda x, y: x >= y
        else:
            key = lambda x, y: x <= y
        return all(
            key(victims_list[i].current_RPM_number, victims_list[i + 1].current_RPM_number)
            for i in range(len(victims_list) - 1)
        )

    def testSortVictimsListByRPMDescending(self):
        self.simulation.SortVictimsListByRPM(self.simulation.all_victims, descending=True)

        self.assertEqual(self.IsListOfVictimsSorted(self.simulation.all_victims, descending=True), True)

    def testMoveVictimFromTransportReadyToAssessed(self):
        random_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(random_victim)
        self.simulation.MoveVictimFromAssessedToTransportReady(random_victim)
        self.simulation.MoveVictimFromTransportReadyToAssessed(random_victim)

        self.assertTrue(random_victim not in self.simulation.unknown_status_victims)
        self.assertTrue(random_victim in self.simulation.assessed_victims)
        self.assertTrue(random_victim not in self.simulation.transport_ready_victims)

    def testMoveVictimFromTransportReadyToAssessedAlreadyMoved(self):
        random_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(random_victim)
        self.simulation.MoveVictimFromAssessedToTransportReady(random_victim)
        self.simulation.MoveVictimFromTransportReadyToAssessed(random_victim)
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.MoveVictimFromTransportReadyToAssessed(random_victim)

        self.assertTrue(random_victim not in self.simulation.unknown_status_victims)
        self.assertTrue(random_victim in self.simulation.assessed_victims)
        self.assertTrue(random_victim not in self.simulation.transport_ready_victims)
        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count)
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count)

    def testOrderIdleSpecialistsEverySpecialistTriage(self):
        """Trzech ocenionych poszkodowanych, ale jest dużo nieocenionych, więc priorytetem jest ocena tych drugich"""
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        sample_team.SpecialistsLeaveTheVehicle()
        n_victims_to_triage: int = 3
        for _ in range(n_victims_to_triage):
            self.simulation.MoveVictimFromUnknownStatusToAssessed(
                self.RandomAliveVictimFromList(self.simulation.unknown_status_victims)
            )
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.OrderIdleSpecialists(sample_team)

        self.assertEqual(
            len(self.simulation.unknown_status_victims),
            prev_unknown_status_victims_count - n_victims_to_triage
        )
        self.assertEqual(
            len(self.simulation.assessed_victims),
            prev_assessed_victims_count + n_victims_to_triage
        )
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count)
        for specialist in sample_team.specialists:
            self.assertIsNone(specialist.target_victim)
            self.assertEqual(specialist.stored_procedure, self.simulation.GetTriageProcedure())
            self.assertEqual(specialist.is_idle, False)
        self.assertEqual(sample_team.are_specialists_outside, True)

    def testOrderIdleSpecialistsEverySpecialistHelp(self):
        """
        Wszyscy poszkodowani ocenieni, brak nieocenionych, więc tylko leczenie/przygotowanie do transportu
        Jeden poszkodowany jest już uleczony, jest w najgorszym stanie, więc będzie rozpatrywany pierwszy
        """
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        sample_team.SpecialistsLeaveTheVehicle()
        self.AssessAllVictims()
        helped_victim: victim.Victim = self.simulation.GetTargetVictimForProcedure()
        self.HelpVictimCompletely(helped_victim)
        for victim_ in self.simulation.assessed_victims[:]:
            if victim_.current_RPM_number == helped_victim.current_RPM_number:
                self.simulation.assessed_victims.remove(victim_)
        # Poniższe przypadki to poszkodowani, którzy nie mają problemów do uleczenia - muszą być jak najszybciej
        # przetransportowani, mając niskie RPM - zależnie od losowego ułożenia mogą zaburzać deterministyczność testu
        self.simulation.assessed_victims.remove(self.GetVictimById(20))
        self.simulation.assessed_victims.remove(self.GetVictimById(21))
        self.simulation.assessed_victims.append(helped_victim)
        self.AllTeamsIntoAction()
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.OrderIdleSpecialists(sample_team)

        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count - 1)
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count + 1)
        self.assertTrue(helped_victim in self.simulation.transport_ready_victims)
        for specialist in sample_team.specialists:
            self.assertIsNotNone(specialist.target_victim)
            self.assertIsNotNone(specialist.stored_procedure)
            self.assertEqual(specialist.is_idle, False)
        self.assertNotEqual(sample_team.specialists[0].target_victim, sample_team.specialists[1].target_victim)
        self.assertNotEqual(sample_team.specialists[0].target_victim, sample_team.specialists[2].target_victim)
        self.assertNotEqual(sample_team.specialists[1].target_victim, sample_team.specialists[2].target_victim)
        self.assertEqual(sample_team.are_specialists_outside, True)

    def AssessAllVictims(self):
        for victim_ in self.simulation.all_victims:
            self.simulation.MoveVictimFromUnknownStatusToAssessed(victim_)

    def HelpVictimCompletely(self, target_victim: victim.Victim):
        found_procedure: victim.Procedure = self.simulation.GetAnyPossibleProcedureToPerform(target_victim)
        while found_procedure:
            target_victim.procedures_performed_so_far.append(found_procedure)
            found_procedure = self.simulation.GetAnyPossibleProcedureToPerform(target_victim)

    def testOrderIdleSpecialistsEverySpecialistGoBackToVehicle(self):
        """Wszyscy poszkodowani transport_ready - więc specjaliści mogą wrócić do karetki"""
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        sample_team.SpecialistsLeaveTheVehicle()
        self.AssessAllVictims()
        self.PrepareForTransportAllVictims()
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.OrderIdleSpecialists(sample_team)

        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count)
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count)
        for specialist in sample_team.specialists:
            self.assertIsNone(specialist.target_victim)
            self.assertIsNone(specialist.stored_procedure)
            self.assertEqual(specialist.is_idle, False)
        self.assertEqual(sample_team.are_specialists_outside, False)

    def PrepareForTransportAllVictims(self):
        for victim_ in self.simulation.all_victims:
            self.simulation.MoveVictimFromAssessedToTransportReady(victim_)

    def testOrderIdleSpecialistsEverySpecialistDifferentThings(self):
        """
        Wszyscy poszkodowani transport_ready, poza jednym unassessed i jednym uleczonym assessed - są to wszystkie
        przypadki funkcji - jednak nie zostanie wykonana instrukcja powrotu do karetki, ponieważ niektórzy specjaliści
        są zajęci
        """
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        sample_team.SpecialistsLeaveTheVehicle()
        self.AssessAllVictims()
        helped_victim: victim.Victim = self.simulation.GetTargetVictimForProcedure()
        self.HelpVictimCompletely(helped_victim)
        self.simulation.assessed_victims.remove(helped_victim)
        not_helped_victim: victim.Victim = self.simulation.GetTargetVictimForProcedure()
        self.simulation.assessed_victims.remove(not_helped_victim)
        self.AllTeamsIntoAction()
        self.PrepareForTransportAllVictims()
        self.simulation.assessed_victims.append(helped_victim)
        self.simulation.unknown_status_victims.append(not_helped_victim)
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.OrderIdleSpecialists(sample_team)

        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count - 1)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count)
        self.assertEqual(
            len(self.simulation.transport_ready_victims),
            prev_transport_ready_victims_count + 1
        )
        self.assertIsNone(sample_team.specialists[0].target_victim)
        self.assertEqual(sample_team.specialists[0].stored_procedure, self.simulation.GetTriageProcedure())
        self.assertEqual(sample_team.specialists[0].is_idle, False)
        self.assertIsNotNone(sample_team.specialists[1].target_victim)
        self.assertIsNotNone(sample_team.specialists[1].stored_procedure)
        self.assertEqual(sample_team.specialists[1].is_idle, False)
        self.assertIsNone(sample_team.specialists[2].target_victim)
        self.assertIsNone(sample_team.specialists[2].stored_procedure)
        self.assertEqual(sample_team.specialists[2].is_idle, True)
        self.assertEqual(sample_team.are_specialists_outside, True)

    def testAnyRemainingAssessedVictimsNeedingProceduresNoAssessed(self):
        self.assertEqual(self.simulation.AnyRemainingAssessedVictimsNeedingProcedures(), False)

    def testAnyRemainingAssessedVictimsNeedingProceduresOnlyDeadAssessed(self):
        self.simulation.assessed_victims = [
            victim_ for victim_ in self.simulation.assessed_victims if victim_.IsDead()
        ]

        self.assertEqual(self.simulation.AnyRemainingAssessedVictimsNeedingProcedures(), False)

    def testAnyRemainingAssessedVictimsNeedingProceduresOneAliveAssessed(self):
        self.simulation.assessed_victims = [
            victim_ for victim_ in self.simulation.assessed_victims if victim_.IsDead()
        ]
        self.simulation.assessed_victims.append(self.RandomAliveVictimFromList(self.simulation.all_victims))

        self.assertEqual(self.simulation.AnyRemainingAssessedVictimsNeedingProcedures(), True)

    def testAnyRemainingAssessedVictimsNeedingProceduresOnlyUnderProcedureAssessed(self):
        self.AssessAllVictims()
        for victim_ in self.simulation.assessed_victims:
            victim_.under_procedure = True

        self.assertEqual(self.simulation.AnyRemainingAssessedVictimsNeedingProcedures(), False)

    def testAnyRemainingAssessedVictimsNeedingProceduresOneAliveUnderProcedure(self):
        self.simulation.assessed_victims = [
            victim_ for victim_ in self.simulation.assessed_victims if victim_.IsDead()
        ]
        random_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        random_victim.under_procedure = True
        self.simulation.assessed_victims.append(random_victim)

        self.assertEqual(self.simulation.AnyRemainingAssessedVictimsNeedingProcedures(), False)

    def testPerformTriage(self):
        sample_team: zrm.ZRM = tests_zrm.CreateSampleZRM()
        sample_team.SpecialistsLeaveTheVehicle()
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        self.simulation.PerformTriage(sample_team.specialists[0])

        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count - 1)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count + 1)
        self.assertEqual(sample_team.specialists[0].stored_procedure, self.simulation.GetTriageProcedure())
        self.assertEqual(sample_team.specialists[0].is_idle, False)

    def testMoveVictimFromUnknownStatusToAssessed(self):
        random_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(random_victim)

        self.assertTrue(random_victim not in self.simulation.unknown_status_victims)
        self.assertTrue(random_victim in self.simulation.assessed_victims)
        self.assertTrue(random_victim not in self.simulation.transport_ready_victims)

    def testMoveVictimFromUnknownStatusToAssessedAlreadyMoved(self):
        random_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(random_victim)
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(random_victim)

        self.assertTrue(random_victim not in self.simulation.unknown_status_victims)
        self.assertTrue(random_victim in self.simulation.assessed_victims)
        self.assertTrue(random_victim not in self.simulation.transport_ready_victims)
        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count)
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count)

    def testGetTriageProcedure(self):
        self.assertEqual(
            self.simulation.GetTriageProcedure(),
            victim.Procedure.FromDisciplineAndNumber(0, 1, 1)
        )

    def testHelpAssessedVictimOrPrepareForTransportOneToHelpCriticalFewToTransport(self):
        """Pierwszym znalezionym poszkodowanym będzie ten, któremu trzeba pomóc, więc pozostali zostaną ominięci"""
        n_helped_victims: int = 3
        sample_team, helped_victims, next_target_victim = self.PrepareSampleTeamAndAssessedVictims(n_helped_victims)
        self.simulation.HelpAssessedVictimOrPrepareForTransport(sample_team.specialists[0], sample_team)

        for helped_victim in helped_victims:
            self.assertTrue(helped_victim in self.simulation.assessed_victims)
            self.assertFalse(helped_victim in self.simulation.transport_ready_victims)
        for team in self.simulation.teams_in_action[:n_helped_victims]:
            self.assertEqual(team.queue_of_next_targets, [])
        self.assertEqual(sample_team.specialists[0].target_victim, next_target_victim)
        self.assertEqual(sample_team.are_specialists_outside, True)

    def PrepareSampleTeamAndAssessedVictims(self, n_helped_victims: int, target_highest_RPM: bool = False) -> \
            Tuple[zrm.ZRM, List[victim.Victim], victim.Victim]:
        for team in self.simulation.idle_teams[:(n_helped_victims + 1)]:
            self.simulation.TeamIntoAction(team)
        sample_team: zrm.ZRM = self.simulation.teams_in_action[n_helped_victims]
        self.MoveTeamToIncidentPlaceAndSpecialistsOut(sample_team)
        self.AssessAllVictims()
        chosen_victims: List[victim.Victim] = self.GetNAssessedVictimsWithDifferentRPM(
            n_helped_victims, target_highest_RPM
        )
        self.simulation.assessed_victims = chosen_victims
        next_target_victim, *helped_victims = chosen_victims
        for helped_victim in helped_victims:
            self.HelpVictimCompletely(helped_victim)
        return sample_team, helped_victims, next_target_victim

    def MoveTeamToIncidentPlaceAndSpecialistsOut(
            self, team: zrm.ZRM, incident_place: Optional[sor.IncidentPlace] = None
    ):
        if incident_place is None:
            incident_place = self.simulation.incidents[0]
        team.origin_location_address = incident_place.address
        team.SpecialistsLeaveTheVehicle()

    def testHelpAssessedVictimOrPrepareForTransportOneToHelpNonCriticalFewToTransport(self):
        """
        Wersja z nie-krytycznymi problemami poszkodowanego - ma dużo RPM, więc zostanie znaleziony później i pozostali
        zostaną najpierw przeniesieni do transport_ready
        """
        n_helped_victims: int = 3
        non_critical_victim: victim.Victim = self.GetNonCriticalVictim()
        sample_team, helped_victims, next_target_victim = self.PrepareSampleTeamAndAssessedVictims(n_helped_victims)
        self.simulation.assessed_victims.remove(next_target_victim)
        self.simulation.assessed_victims.append(non_critical_victim)
        self.simulation.HelpAssessedVictimOrPrepareForTransport(sample_team.specialists[0], sample_team)

        for helped_victim in helped_victims:
            self.assertFalse(helped_victim in self.simulation.assessed_victims)
            self.assertTrue(helped_victim in self.simulation.transport_ready_victims)
        for team in self.simulation.teams_in_action[:n_helped_victims]:
            self.assertEqual(team.queue_of_next_targets, [self.simulation.incidents[0]])
        self.assertEqual(sample_team.specialists[0].target_victim, non_critical_victim)
        self.assertEqual(sample_team.specialists[0].is_idle, False)
        self.assertEqual(sample_team.are_specialists_outside, True)

    def GetNonCriticalVictim(self) -> Optional[victim.Victim]:
        for victim_ in self.simulation.all_victims:
            if (victim_.current_state.triage_colour == victim.TriageColour.YELLOW and
                    self.simulation.GetAnyPossibleProcedureToPerform(victim_)):
                return victim_
        return None

    def testHelpAssessedVictimOrPrepareForTransportFewToTransportOneToHelp(self):
        """Poszkodowany, któremu trzeba pomóc, będzie ostatni w kolejności, więc najpierw przygotowanie do transportu"""
        n_helped_victims: int = 3
        sample_team, helped_victims, next_target_victim = self.PrepareSampleTeamAndAssessedVictims(
            n_helped_victims, target_highest_RPM=True
        )
        self.simulation.HelpAssessedVictimOrPrepareForTransport(sample_team.specialists[0], sample_team)

        for helped_victim in helped_victims:
            self.assertFalse(helped_victim in self.simulation.assessed_victims)
            self.assertTrue(helped_victim in self.simulation.transport_ready_victims)
        for team in self.simulation.teams_in_action[:n_helped_victims]:
            self.assertEqual(team.queue_of_next_targets, [self.simulation.incidents[0]])
        self.assertEqual(sample_team.specialists[0].target_victim, next_target_victim)
        self.assertEqual(sample_team.are_specialists_outside, True)

    def testHelpAssessedVictimOrPrepareForTransportNoTeamToTransport(self):
        """Poszkodowany z największym RPM potrzebuje pomocy, więc funkcja skończy przed dotarciem do niego"""
        n_helped_victims: int = 3
        sample_team, helped_victims, _ = self.PrepareSampleTeamAndAssessedVictims(
            n_helped_victims, target_highest_RPM=True
        )
        self.simulation.assessed_victims = helped_victims
        queued_location: zrm.TargetDestination = self.simulation.all_hospitals[0]
        for team in self.simulation.teams_in_action[:n_helped_victims]:
            team.QueueNewTargetLocation(queued_location)
        self.simulation.HelpAssessedVictimOrPrepareForTransport(sample_team.specialists[0], sample_team)

        for helped_victim in helped_victims:
            self.assertTrue(helped_victim in self.simulation.assessed_victims)
            self.assertFalse(helped_victim in self.simulation.transport_ready_victims)
        for team in self.simulation.teams_in_action[:n_helped_victims]:
            self.assertEqual(team.queue_of_next_targets, [queued_location])
        self.assertEqual(sample_team.specialists[0].target_victim, None)
        self.assertEqual(sample_team.are_specialists_outside, True)

    def testHelpAssessedVictimOrPrepareForTransportNoVictimToHelpCannotGoBackToVehicle(self):
        n_helped_victims: int = 3
        sample_team, helped_victims, _ = self.PrepareSampleTeamAndAssessedVictims(n_helped_victims)
        self.simulation.assessed_victims = helped_victims
        self.simulation.HelpAssessedVictimOrPrepareForTransport(sample_team.specialists[0], sample_team)

        self.assertIsNone(sample_team.specialists[0].target_victim)
        self.assertEqual(sample_team.are_specialists_outside, True)

    def testHelpAssessedVictimOrPrepareForTransportNoVictimToHelpReturningToVehicle(self):
        n_helped_victims: int = 3
        sample_team, helped_victims, _ = self.PrepareSampleTeamAndAssessedVictims(n_helped_victims)
        self.simulation.assessed_victims = helped_victims
        self.simulation.HelpAssessedVictimOrPrepareForTransport(sample_team.specialists[-1], sample_team)

        self.assertIsNone(sample_team.specialists[-1].target_victim)
        self.assertEqual(sample_team.are_specialists_outside, False)

    def testGetTargetVictimForProcedureRed(self):
        worst_condition_red_victim_RPM_number: int = 2
        self.AssessAllVictims()

        self.assertEqual(
            self.simulation.GetTargetVictimForProcedure().current_RPM_number,
            worst_condition_red_victim_RPM_number
        )

    def testGetTargetVictimForProcedureSecondWorstRed(self):
        """Wszyscy poszkodowani o RPM=2 są już w trakcie przeprowadzania na nich procedur - więc zostaną pominięci"""
        worst_condition_red_victim_RPM_number: int = 2
        second_worst_condition_red_victim_RPM_number: int = 3
        self.AssessAllVictims()
        for victim_ in self.simulation.assessed_victims:
            if victim_.current_RPM_number == worst_condition_red_victim_RPM_number:
                victim_.under_procedure = True

        self.assertEqual(
            self.simulation.GetTargetVictimForProcedure().current_RPM_number,
            second_worst_condition_red_victim_RPM_number
        )

    def testGetTargetVictimForProcedureNoRedYellow(self):
        worst_condition_yellow_victim_RPM_number: int = 10
        self.AssessAllVictims()
        self.RemoveVictimsWithTriageColour(victim.TriageColour.RED)

        self.assertEqual(
            self.simulation.GetTargetVictimForProcedure().current_RPM_number,
            worst_condition_yellow_victim_RPM_number
        )

    def RemoveVictimsWithTriageColour(self, triage_colour_to_remove: victim.TriageColour):
        for victim_ in self.simulation.all_victims:
            if victim_.current_state.triage_colour == triage_colour_to_remove:
                self.simulation.assessed_victims.remove(victim_)

    def testGetTargetVictimForProcedureNoRedNoYellow(self):
        self.AssessAllVictims()
        self.RemoveVictimsWithTriageColour(victim.TriageColour.RED)
        self.RemoveVictimsWithTriageColour(victim.TriageColour.YELLOW)

        self.assertIsNone(self.simulation.GetTargetVictimForProcedure())

    def testGetAnyPossibleProcedureToPerformFound(self):
        target_victim: victim.Victim = self.GetVictimById(75)
        found_procedure: victim.Procedure = victim.Procedure.FromDisciplineAndNumber(15, 2, 3)

        self.assertEqual(self.simulation.GetAnyPossibleProcedureToPerform(target_victim), found_procedure)

    def GetVictimById(self, victim_id: int) -> Optional[victim.Victim]:
        for victim_ in self.simulation.all_victims:
            if victim_.id_ == victim_id:
                return victim_
        return None

    def testGetAnyPossibleProcedureToPerformNotFound(self):
        target_victim: victim.Victim = self.GetVictimById(89)

        self.assertEqual(self.simulation.GetAnyPossibleProcedureToPerform(target_victim), None)

    def testPrepareVictimForTransportAndSendToClosestTeamQueue(self):
        target_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(target_victim)
        team_of_specialists: zrm.ZRM = self.simulation.idle_teams[-1]
        self.MoveTeamToIncidentPlaceAndSpecialistsOut(team_of_specialists)
        closest_team: zrm.ZRM = self.MakeIdleTeamClosestToTargetLocation(self.simulation.incidents[0])
        self.AllTeamsIntoAction()
        self.simulation.PrepareVictimForTransportAndSendToClosestTeamQueue(
            target_victim, team_of_specialists
        )

        self.assertTrue(target_victim in self.simulation.transport_ready_victims)
        self.assertFalse(target_victim in self.simulation.assessed_victims)
        self.assertEqual(closest_team.queue_of_next_targets[0].address, team_of_specialists.origin_location_address)

    def AllTeamsIntoAction(self):
        idle_teams_copy: List[zrm.ZRM] = self.simulation.idle_teams[:]
        for i in range(len(idle_teams_copy)):
            self.simulation.TeamIntoAction(idle_teams_copy[i])

    def testPrepareVictimForTransportAndSendToClosestTeamQueueNoAvailableTeam(self):
        target_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(target_victim)
        team_of_specialists: zrm.ZRM = self.simulation.idle_teams[-1]
        self.MoveTeamToIncidentPlaceAndSpecialistsOut(team_of_specialists)
        self.AllTeamsIntoAction()
        self.AllTeamsHaveQueues()

        self.assertRaises(
            RuntimeError,
            self.simulation.PrepareVictimForTransportAndSendToClosestTeamQueue, target_victim, team_of_specialists
        )
        self.assertTrue(target_victim in self.simulation.transport_ready_victims)
        self.assertFalse(target_victim in self.simulation.assessed_victims)

    def AllTeamsHaveQueues(self):
        for team in self.simulation.teams_in_action:
            team.QueueNewTargetLocation(self.simulation.all_hospitals[0])

    def testMoveVictimFromAssessedToTransportReady(self):
        random_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(random_victim)
        self.simulation.MoveVictimFromAssessedToTransportReady(random_victim)

        self.assertTrue(random_victim not in self.simulation.unknown_status_victims)
        self.assertTrue(random_victim not in self.simulation.assessed_victims)
        self.assertTrue(random_victim in self.simulation.transport_ready_victims)

    def testMoveVictimFromAssessedToTransportReadyAlreadyMoved(self):
        random_victim: victim.Victim = self.RandomAliveVictimFromList(self.simulation.all_victims)
        self.simulation.MoveVictimFromUnknownStatusToAssessed(random_victim)
        self.simulation.MoveVictimFromAssessedToTransportReady(random_victim)
        prev_unknown_status_victims_count: int = len(self.simulation.unknown_status_victims)
        prev_assessed_victims_count: int = len(self.simulation.assessed_victims)
        prev_transport_ready_victims_count: int = len(self.simulation.transport_ready_victims)
        self.simulation.MoveVictimFromAssessedToTransportReady(random_victim)

        self.assertTrue(random_victim not in self.simulation.unknown_status_victims)
        self.assertTrue(random_victim not in self.simulation.assessed_victims)
        self.assertTrue(random_victim in self.simulation.transport_ready_victims)
        self.assertEqual(len(self.simulation.unknown_status_victims), prev_unknown_status_victims_count)
        self.assertEqual(len(self.simulation.assessed_victims), prev_assessed_victims_count)
        self.assertEqual(len(self.simulation.transport_ready_victims), prev_transport_ready_victims_count)

    def testGetClosestTeamWithoutQueueBeginning(self):
        self.AllTeamsIntoAction()

        self.assertTrue(
            self.simulation.GetClosestTeamWithoutQueue(self.simulation.incidents[0].address).id_ in
            ["K01 47", "K01 098"]
        )

    def testGetClosestTeamWithoutQueueClosestHaveQueuesNextClosestChosen(self):
        self.AllTeamsIntoAction()
        different_incident_place: sor.IncidentPlace = tests_sor.CreateSampleIncidentPlace()
        self.simulation.GetTeamById("K01 47").QueueNewTargetLocation(different_incident_place)
        self.simulation.GetTeamById("K01 098").QueueNewTargetLocation(different_incident_place)

        self.assertEqual(
            self.simulation.GetClosestTeamWithoutQueue(self.simulation.incidents[0].address).id_, "K01 100"
        )

    def testGetClosestTeamWithoutQueueClosestIsDriving(self):
        self.AllTeamsIntoAction()
        closest_team_id: str = "S02 348"
        self.MakeIdleTeamClosestToTargetLocation(
            self.simulation.incidents[0], closest_team_id
        )

        self.assertEqual(
            self.simulation.GetClosestTeamWithoutQueue(self.simulation.incidents[0].address).id_,
            closest_team_id
        )

    def testGetClosestTeamWithoutQueueNone(self):
        self.AllTeamsIntoAction()
        self.AllTeamsHaveQueues()

        self.assertIsNone(self.simulation.GetClosestTeamWithoutQueue(self.simulation.incidents[0].address))

    def testGetIncidentPlaceFromAddressFromTeamAddress(self):
        driving_team: zrm.ZRM = self.simulation.idle_teams[0]
        driving_team.StartDriving(self.simulation.incidents[0])
        driving_team.FinishDrivingAndReturnVictim()

        self.assertEqual(
            self.simulation.GetIncidentPlaceFromAddress(driving_team.origin_location_address),
            self.simulation.incidents[0]
        )

    def testGetIncidentPlaceFromAddressBadAddress(self):
        driving_team: zrm.ZRM = self.simulation.idle_teams[0]

        self.assertIsNone(self.simulation.GetIncidentPlaceFromAddress(driving_team.origin_location_address))

    def testSimulationResultsAliveAssessedRemainingError(self):
        # TODO
        raise NotImplementedError

    def testSimulationResultsCorrect(self):
        # TODO
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
