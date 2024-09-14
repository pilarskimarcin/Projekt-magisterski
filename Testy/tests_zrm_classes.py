# -*- coding: utf-8 -*-
import math
import unittest

from Skrypty import utilities as util
from Skrypty import victim_classes as victim
from Skrypty import zrm_classes as zrm
from Testy import tests_utilities as tests_util
from Testy import tests_victim_classes as tests_victim


class SpecialistTests(unittest.TestCase):
    sample_specialist: zrm.Specialist

    def setUp(self):
        self.sample_specialist = zrm.Specialist("K01 47")

    def testEquality(self):
        sample_specialist: zrm.Specialist = zrm.Specialist("K01 47")

        self.assertEqual(sample_specialist, self.sample_specialist)

    def testInequality(self):
        sample_specialist: zrm.Specialist = zrm.Specialist("K01 48")

        self.assertNotEqual(sample_specialist, self.sample_specialist)


def CreateSampleZRM() -> zrm.ZRM:
    return zrm.ZRM(
            "K01 47", "DM06-01", zrm.ZRMType.S,
            tests_util.CreateSampleAddressHospital()
    )


class ZRMTests(unittest.TestCase):
    sample_zrm: zrm.ZRM
    sample_target_location: util.TargetDestination
    sample_victim: victim.Victim

    def setUp(self):
        self.sample_zrm = CreateSampleZRM()
        self.sample_target_location = util.TargetDestination(tests_util.CreateSampleAddressIncident())
        sample_state: victim.State = tests_victim.CreateSampleState()
        self.sample_victim = victim.Victim(1, [sample_state])

    def testInit(self):
        self.assertTupleEqual(
            (
                len(self.sample_zrm.specialists), self.sample_zrm.target_location, self.sample_zrm.transported_victim,
                self.sample_zrm.time_until_destination_in_minutes, self.sample_zrm.queue_of_next_targets
            ),
            (3, None, None, None, [])
        )

    def testEquality(self):
        sample_zrm: zrm.ZRM = CreateSampleZRM()

        self.assertEqual(sample_zrm, self.sample_zrm)

    def testInequality(self):
        sample_zrm: zrm.ZRM = CreateSampleZRM()
        sample_zrm.id_ = "K01 98"

        self.assertNotEqual(sample_zrm, self.sample_zrm)

    def testSimpleGetters(self):
        self.assertTupleEqual(
            tuple1=(
                self.sample_zrm.GetPersonnelCount(), self.sample_zrm.IsDriving(),
                self.sample_zrm.IsTransportingAVictim()
            ),
            tuple2=(3, False, False)
        )

    def testStartDriving(self):
        self.sample_zrm.StartDriving(self.sample_target_location)
        self.assertEqual(self.sample_zrm.target_location, self.sample_target_location)

    def testStartDrivingWithVictim(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_target_location)
        self.assertTrue(self.sample_zrm.IsTransportingAVictim())
        self.assertTrue(self.sample_zrm.IsDriving())

    def testCalculateTimeForTheNextDestination(self):
        self.sample_zrm.target_location = self.sample_target_location
        self.sample_zrm.CalculateTimeForTheNextDestination()
        self.assertEqual(
            self.sample_zrm.time_until_destination_in_minutes,
            math.ceil(0.64*tests_util.CreateSampleDistanceAndDurationData()[1])
        )

    def testDrive(self):
        self.sample_zrm.time_until_destination_in_minutes = 10
        self.sample_zrm.DriveOrFinishDrivingAndReturnVictim()
        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, 9)

    def testFinishDrivingAndReturnVictimNoQueue(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_target_location)
        self.sample_zrm.time_until_destination_in_minutes = 0
        self.assertIsNotNone(self.sample_zrm.DriveOrFinishDrivingAndReturnVictim())
        self.assertTupleEqual(
            tuple1=(self.sample_zrm.transported_victim, self.sample_zrm.origin_location,
                    self.sample_zrm.target_location, self.sample_zrm.time_until_destination_in_minutes),
            tuple2=(None, self.sample_target_location.address, None, None)
        )

    def testFinishDrivingAndReturnVictimWithQueue(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_target_location)
        self.sample_zrm.QueueNewTargetLocation(self.sample_target_location)
        self.sample_zrm.time_until_destination_in_minutes = 0
        self.assertIsNotNone(self.sample_zrm.DriveOrFinishDrivingAndReturnVictim())
        self.assertTupleEqual(
            tuple1=(self.sample_zrm.transported_victim, self.sample_zrm.origin_location,
                    self.sample_zrm.target_location, self.sample_zrm.time_until_destination_in_minutes),
            tuple2=(None, self.sample_target_location.address, self.sample_target_location, None)
        )

    def testQueueNewTargetLocation(self):
        self.assertEqual(self.sample_zrm.queue_of_next_targets, [])
        self.sample_zrm.QueueNewTargetLocation(self.sample_target_location)
        self.assertEqual(self.sample_zrm.queue_of_next_targets, [self.sample_target_location])


if __name__ == '__main__':
    unittest.main()
