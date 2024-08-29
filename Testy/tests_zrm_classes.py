# -*- coding: utf-8 -*-
import math
import unittest

from Skrypty import victim_classes as victim, zrm_classes as zrm
from Testy import tests_victim_classes as test_victim


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.sample_zrm = zrm.ZRM(
            "K01 47", "DM06-01", zrm.ZRMType.S,
            zrm.PlaceAddress("Topolowa", 16, "32-500", "Chrzanów")
        )
        self.sample_address: zrm.PlaceAddress = zrm.PlaceAddress(
            "Chrzanowska", 6, "32-541", "Trzebinia"
        )
        sample_state: victim.State = test_victim.CreateSampleState()
        self.sample_victim: victim.Victim = victim.Victim(1, tuple([sample_state]))

    def test_Init(self):
        self.assertTupleEqual(
            (
                len(self.sample_zrm.specialists), self.sample_zrm.target_location, self.sample_zrm.transported_victim,
                self.sample_zrm.time_until_destination_in_minutes, self.sample_zrm.queue_of_next_targets
            ),
            (3, None, None, None, [])
        )

    def testSimpleGetters(self):
        self.assertTupleEqual(
            tuple1=(
                self.sample_zrm.GetPersonnelCount(), self.sample_zrm.IsDriving(),
                self.sample_zrm.IsTransportingAVictim()
            ),
            tuple2=(3, False, False)
        )

    def testStartDriving(self):
        self.sample_zrm.StartDriving(self.sample_address)
        self.assertEqual(self.sample_zrm.target_location, self.sample_address)

    def testStartDrivingWithVictim(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_address)
        self.assertTrue(self.sample_zrm.IsTransportingAVictim())
        self.assertTrue(self.sample_zrm.IsDriving())

    def testCalculateTimeForTheNextDestination(self):
        self.sample_zrm.target_location = self.sample_address
        self.sample_zrm.CalculateTimeForTheNextDestination()
        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, math.ceil(8.49))

    def testDrive(self):
        self.sample_zrm.time_until_destination_in_minutes = 10
        self.sample_zrm.DriveOrFinishDrivingAndReturnVictim()
        self.assertEqual(self.sample_zrm.time_until_destination_in_minutes, 9)

    def testFinishDrivingAndReturnVictimNoQueue(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_address)
        self.sample_zrm.time_until_destination_in_minutes = 0
        self.assertIsNotNone(self.sample_zrm.DriveOrFinishDrivingAndReturnVictim())
        self.assertTupleEqual(
            tuple1=(self.sample_zrm.transported_victim, self.sample_zrm.origin_location,
                    self.sample_zrm.target_location, self.sample_zrm.time_until_destination_in_minutes),
            tuple2=(None, self.sample_address, None, None)
        )

    def testFinishDrivingAndReturnVictimWithQueue(self):
        self.sample_zrm.StartTransportingAVictim(self.sample_victim, self.sample_address)
        self.sample_zrm.QueueNewTargetLocation(self.sample_address)
        self.sample_zrm.time_until_destination_in_minutes = 0
        self.assertIsNotNone(self.sample_zrm.DriveOrFinishDrivingAndReturnVictim())
        self.assertTupleEqual(
            tuple1=(self.sample_zrm.transported_victim, self.sample_zrm.origin_location,
                    self.sample_zrm.target_location, self.sample_zrm.time_until_destination_in_minutes),
            tuple2=(None, self.sample_address, self.sample_address, None)
        )

    def testQueueNewTargetLocation(self):
        self.assertEqual(self.sample_zrm.queue_of_next_targets, [])
        self.sample_zrm.QueueNewTargetLocation(self.sample_address)
        self.assertEqual(self.sample_zrm.queue_of_next_targets, [self.sample_address])


if __name__ == '__main__':
    unittest.main()
