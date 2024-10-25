# -*- coding: utf-8 -*-
import math
import unittest

import sor_classes as sor
import utilities as util
import victim_classes as victim
import zrm_classes as zrm
import tests_utilities as tests_util
import tests_victim_classes as tests_victim


class SpecialistTests(unittest.TestCase):
    sample_specialist: zrm.Specialist
    sample_zrm: zrm.ZRM

    def setUp(self):
        self.sample_zrm = CreateSampleZRM()
        self.sample_zrm.SpecialistsLeaveTheVehicle()
        self.sample_specialist = self.sample_zrm.specialists[0]

    def testEquality(self):
        sample_specialist: zrm.Specialist = zrm.Specialist("K01 47", 1)
        sample_specialist.is_idle = True

        self.assertEqual(sample_specialist, self.sample_specialist)

    def testInequality(self):
        sample_specialist: zrm.Specialist = self.sample_zrm.specialists[1]

        self.assertNotEqual(sample_specialist, self.sample_specialist)

    def testStartPerformingProcedureWithVictim(self):
        sample_procedure: victim.Procedure = tests_victim.CreateSampleProcedure()
        sample_victim: victim.Victim = tests_victim.CreateSampleVictim()
        self.sample_specialist.StartPerformingProcedure(sample_procedure, sample_victim)

        self.assertEqual(self.sample_specialist.stored_procedure, sample_procedure)
        self.assertEqual(self.sample_specialist.target_victim, sample_victim)
        self.assertEqual(sample_victim.under_procedure, True)
        self.assertEqual(self.sample_specialist.is_idle, False)

    def testStartPerformingProcedureNoVictim(self):
        sample_procedure: victim.Procedure = tests_victim.CreateSampleProcedure()
        self.sample_specialist.StartPerformingProcedure(sample_procedure)

        self.assertEqual(self.sample_specialist.stored_procedure, sample_procedure)
        self.assertEqual(self.sample_specialist.target_victim, None)
        self.assertEqual(self.sample_specialist.is_idle, False)

    def testContinuePerformingProcedureNoProcedure(self):
        self.sample_specialist.ContinuePerformingProcedure()

        self.assertIsNone(self.sample_specialist.stored_procedure)
        self.assertIsNone(self.sample_specialist.target_victim)
        self.assertIsNone(self.sample_specialist.time_until_procedure_is_finished)
        self.assertEqual(self.sample_specialist.is_idle, True)

    def testContinuePerformingProcedureWithProcedure(self):
        sample_procedure: victim.Procedure = tests_victim.CreateSampleProcedure()
        self.sample_specialist.StartPerformingProcedure(sample_procedure)
        sample_time_before_procedure_finished: int = self.sample_specialist.time_until_procedure_is_finished
        self.sample_specialist.ContinuePerformingProcedure()

        self.assertEqual(self.sample_specialist.stored_procedure, sample_procedure)
        self.assertEqual(
            self.sample_specialist.time_until_procedure_is_finished,
            sample_time_before_procedure_finished - 1
        )
        self.assertEqual(self.sample_specialist.is_idle, False)

    def testContinuePerformingProcedureFinishingProcedure(self):
        sample_procedure: victim.Procedure = tests_victim.CreateSampleProcedure()
        self.sample_specialist.StartPerformingProcedure(sample_procedure)
        self.sample_specialist.time_until_procedure_is_finished = 1
        self.sample_specialist.ContinuePerformingProcedure()

        self.assertEqual(self.sample_specialist.stored_procedure, None)
        self.assertEqual(self.sample_specialist.target_victim, None)
        self.assertEqual(self.sample_specialist.time_until_procedure_is_finished, None)
        self.assertEqual(self.sample_specialist.is_idle, True)

    def testClearAfterProcedure(self):
        sample_procedure: victim.Procedure = tests_victim.CreateSampleProcedure()
        sample_victim: victim.Victim = tests_victim.CreateSampleVictim()
        self.sample_specialist.StartPerformingProcedure(sample_procedure, sample_victim)
        self.sample_specialist.ClearAfterProcedure()

        self.assertEqual(self.sample_specialist.time_until_procedure_is_finished, None)
        self.assertEqual(self.sample_specialist.target_victim, None)
        self.assertEqual(self.sample_specialist.stored_procedure, None)
        self.assertEqual(self.sample_specialist.is_idle, True)

    def testClearAfterProcedureVictimDiedDuringProcedure(self):
        sample_procedure: victim.Procedure = tests_victim.CreateSampleProcedure()
        sample_victim: victim.Victim = tests_victim.CreateSampleVictim()
        self.sample_specialist.StartPerformingProcedure(sample_procedure, sample_victim)
        sample_victim.ChangeState(2)
        self.sample_specialist.ContinuePerformingProcedure()

        self.assertEqual(self.sample_specialist.time_until_procedure_is_finished, None)
        self.assertEqual(self.sample_specialist.target_victim, None)
        self.assertEqual(self.sample_specialist.stored_procedure, None)
        self.assertEqual(self.sample_specialist.is_idle, True)

    def testFinishProcedure(self):
        sample_procedure: victim.Procedure = tests_victim.CreateSampleProcedure()
        target_victim: victim.Victim = tests_victim.CreateSampleVictim()
        self.sample_specialist.StartPerformingProcedure(sample_procedure, target_victim)
        self.sample_specialist.FinishProcedure()

        self.assertEqual(self.sample_specialist.stored_procedure, None)
        self.assertEqual(self.sample_specialist.target_victim, None)
        self.assertEqual(self.sample_specialist.time_until_procedure_is_finished, None)
        self.assertEqual(self.sample_specialist.is_idle, True)
        self.assertEqual(target_victim.under_procedure, False)
        self.assertEqual(target_victim.procedures_performed_so_far, [sample_procedure])


def CreateSampleZRM() -> zrm.ZRM:
    return zrm.ZRM(
            "K01 47", "DM06-01", zrm.ZRMType.S,
            tests_util.CreateSampleAddressHospital()
    )


BAD_TEAM_ID = "K01 98"


class ZRMTests(unittest.TestCase):
    sample_zrm: zrm.ZRM
    sample_target_location: util.TargetDestination
    sample_victim: victim.Victim

    def setUp(self):
        self.sample_zrm = CreateSampleZRM()
        self.sample_target_location = sor.IncidentPlace(tests_util.CreateSampleAddressIncident(), [])
        sample_state: victim.State = tests_victim.CreateSampleState()
        self.sample_victim = victim.Victim(1, [sample_state])

    def testInit(self):
        self.assertEqual(len(self.sample_zrm.specialists), 3)
        self.assertEqual(self.sample_zrm.target_location, None)
        self.assertEqual(self.sample_zrm.transported_victim, None)
        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, None)
        self.assertEqual(self.sample_zrm.queue_of_next_targets, [])

    def testEquality(self):
        sample_zrm: zrm.ZRM = CreateSampleZRM()

        self.assertEqual(sample_zrm, self.sample_zrm)

    def testInequality(self):
        sample_zrm: zrm.ZRM = CreateSampleZRM()
        sample_zrm.id_ = BAD_TEAM_ID

        self.assertNotEqual(sample_zrm, self.sample_zrm)

    def testSimpleGetters(self):
        self.assertEqual(self.sample_zrm.GetPersonnelCount(), 3)
        self.assertEqual(self.sample_zrm.IsDriving(), False)
        self.assertEqual(self.sample_zrm.IsTransportingAVictim(), False)

    def testStartDriving(self):
        self.sample_zrm.StartDriving(self.sample_target_location)

        self.assertEqual(self.sample_zrm.target_location, self.sample_target_location)

    def testStartDrivingNoSpecialists(self):
        self.sample_zrm.SpecialistsLeaveTheVehicle()

        self.assertRaises(
            RuntimeError,
            self.sample_zrm.StartDriving, self.sample_target_location
        )

    def testStartDrivingIsAlreadyDriving(self):
        self.sample_zrm.StartDriving(self.sample_target_location)

        self.assertRaises(
            RuntimeError,
            self.sample_zrm.StartDriving, self.sample_target_location
        )

    def testStartTransportingAVictim(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_target_location)

        self.assertEqual(self.sample_zrm.IsTransportingAVictim(), True)
        self.assertEqual(self.sample_zrm.IsDriving(), True)

    def testStartTransportingAVictimAlreadyDriving(self):
        self.sample_zrm.StartDriving(self.sample_target_location)

        self.assertRaises(
            RuntimeError,
            self.sample_zrm.StartTransportingAVictim, self.sample_victim, self.sample_target_location
        )

    def testCalculateTimeForTheNextDestination(self):
        self.sample_zrm.target_location = self.sample_target_location
        self.sample_zrm.CalculateTimeForTheNextDestination()

        self.assertEqual(
            self.sample_zrm.time_until_destination_in_minutes,
            math.ceil(0.64*tests_util.CreateSampleDistanceAndDurationData()[1])
        )

    def testDriveDecreasingTravelDuration(self):
        self.sample_zrm.StartDriving(self.sample_target_location)
        self.sample_zrm.time_until_destination_in_minutes = 10
        self.sample_zrm.DriveOrFinishDrivingAndReturnVictim()

        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, 9)

    def testDriveNotDrivingCurrently(self):
        self.sample_zrm.time_until_destination_in_minutes = None

        self.assertEqual(self.sample_zrm.DriveOrFinishDrivingAndReturnVictim(), None)
        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, None)

    def testDriveAlreadyFinished(self):
        self.sample_zrm.StartDriving(self.sample_target_location)
        self.sample_zrm.time_until_destination_in_minutes = 0
        self.sample_zrm.DriveOrFinishDrivingAndReturnVictim()

        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, None)

    def testFinishDrivingAndReturnVictimNoQueue(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_target_location)

        self.assertIsNotNone(self.sample_zrm.FinishDrivingAndReturnVictim())
        self.assertEqual(self.sample_zrm.transported_victim, None)
        self.assertEqual(self.sample_zrm.origin_location_address, self.sample_target_location.address)
        self.assertEqual(self.sample_zrm.target_location, None)
        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, None)

    def testFinishDrivingAndReturnVictimWithQueueButAlreadyReached(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_target_location)
        self.sample_zrm.QueueNewTargetLocation(self.sample_target_location)

        self.assertIsNotNone(self.sample_zrm.FinishDrivingAndReturnVictim())
        self.assertEqual(self.sample_zrm.transported_victim, None)
        self.assertEqual(self.sample_zrm.origin_location_address, self.sample_target_location.address)
        self.assertEqual(self.sample_zrm.target_location, None)
        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, None)
        self.assertEqual(self.sample_zrm.queue_of_next_targets, [])

    def testFinishDrivingAndReturnVictimWithQueueNewLocation(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_target_location)
        new_target_location = sor.TargetDestination(tests_util.CreateSampleAddressHospital())
        self.sample_zrm.QueueNewTargetLocation(new_target_location)

        self.assertIsNotNone(self.sample_zrm.FinishDrivingAndReturnVictim())
        self.assertEqual(self.sample_zrm.transported_victim, None)
        self.assertEqual(self.sample_zrm.origin_location_address, self.sample_target_location.address)
        self.assertEqual(self.sample_zrm.target_location, new_target_location)
        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, 3)
        self.assertEqual(self.sample_zrm.queue_of_next_targets, [])

    def testQueueNewTargetLocation(self):
        self.sample_zrm.QueueNewTargetLocation(self.sample_target_location)

        self.assertEqual(self.sample_zrm.queue_of_next_targets, [self.sample_target_location])

    def testSpecialistsLeaveTheVehicleCorrectUsage(self):
        self.sample_zrm.SpecialistsLeaveTheVehicle()

        self.assertEqual(self.sample_zrm.are_specialists_outside, True)
        self.assertEqual(self.sample_zrm.specialists[-1].is_idle, True)

    def testSpecialistsLeaveTheVehicleIsDriving(self):
        self.sample_zrm.StartDriving(self.sample_target_location)

        self.assertRaises(
            RuntimeError,
            self.sample_zrm.SpecialistsLeaveTheVehicle
        )

    def testTrySpecialistsComeBackToTheVehicleTrue(self):
        self.sample_zrm.SpecialistsLeaveTheVehicle()

        self.assertEqual(self.sample_zrm.TrySpecialistsComeBackToTheVehicle(), True)
        self.assertEqual(self.sample_zrm.are_specialists_outside, False)
        self.assertEqual(self.sample_zrm.specialists[-1].is_idle, False)

    def testTrySpecialistsComeBackToTheVehicleFalse(self):
        self.sample_zrm.SpecialistsLeaveTheVehicle()
        self.sample_zrm.specialists[0].StartPerformingProcedure(tests_victim.CreateSampleProcedure())

        self.assertEqual(self.sample_zrm.TrySpecialistsComeBackToTheVehicle(), False)
        self.assertEqual(self.sample_zrm.are_specialists_outside, True)

    def testAreSpecialistsIdleTrue(self):
        self.sample_zrm.SpecialistsLeaveTheVehicle()

        self.assertEqual(self.sample_zrm.AreSpecialistsIdle(), True)

    def testAreSpecialistsIdleFalse(self):
        self.sample_zrm.SpecialistsLeaveTheVehicle()
        self.sample_zrm.specialists[0].StartPerformingProcedure(tests_victim.CreateSampleProcedure())

        self.assertEqual(self.sample_zrm.AreSpecialistsIdle(), False)

    def testSpecialistsContinuePerformingProcedures(self):
        self.sample_zrm.SpecialistsLeaveTheVehicle()
        self.sample_zrm.specialists[0].StartPerformingProcedure(tests_victim.CreateSampleProcedure())
        time_needed_to_perform: int = tests_victim.CreateSampleProcedure().time_needed_to_perform
        self.sample_zrm.SpecialistsContinuePerformingProcedures()

        self.assertEqual(
            self.sample_zrm.specialists[0].time_until_procedure_is_finished,
            time_needed_to_perform - 1
        )


if __name__ == '__main__':
    unittest.main()
