# -*- coding: utf-8 -*-
from typing import List
import unittest

from Skrypty import sor_classes as sor, victim_classes as victim
from Testy import tests_victim_classes as victim_test


def AssertDepartmentTookInVictim(
        test_case: unittest.TestCase, department: sor.Department, sample_victim: victim.Victim, sample_time: float,
        sample_beds_amount: int
):
    test_case.assertEqual(department.admitted_victims, [sample_victim])
    test_case.assertEqual(department.admitted_victims[0].hospital_admittance_time, sample_time)
    test_case.assertEqual(department.current_beds_count, sample_beds_amount - 1)


class DepartmentTests(unittest.TestCase):

    def setUp(self):
        self.sample_department = sor.Department(
            id_=4, name="Oddział chirurgii naczyniowej", medical_categories=[39, 37], current_beds_count=15
        )
        sample_state: victim.State = victim_test.CreateSampleState()
        self.sample_victim: victim.Victim = victim.Victim(1, tuple([sample_state]))
        self.sample_time: float = 65.0

    def testInit(self):
        self.assertEqual(self.sample_department.admitted_victims, [])

    def testTakeInVictim(self):
        sample_beds_amount: int = self.sample_department.current_beds_count

        self.sample_department.TakeInVictim(self.sample_victim, self.sample_time)

        AssertDepartmentTookInVictim(
            test_case=self, department=self.sample_department, sample_victim=self.sample_victim,
            sample_time=self.sample_time, sample_beds_amount=sample_beds_amount
        )

    def testTakeInVictimNoAvailableBeds(self):
        self.sample_department.current_beds_count = 0

        self.assertRaises(
            RuntimeError,
            self.sample_department.TakeInVictim, self.sample_victim, self.sample_time
        )


class HospitalTests(unittest.TestCase):

    def setUp(self):
        sample_departments: List[sor.Department] = [
            sor.Department(id_=1, name="Oddział chirurgii urazowo-ortopedycznej", medical_categories=[25],
                           current_beds_count=22),
            sor.Department(id_=4, name="Oddział chirurgii naczyniowej", medical_categories=[39, 37],
                           current_beds_count=15),
            sor.Department(id_=6, name="Szpitalny Oddział Ratunkowy", medical_categories=[15],
                           current_beds_count=12)
        ]

        self.sample_hospital = sor.Hospital(
            id_=1, name="Szpital Powiatowy w Chrzanowie",
            address=sor.PlaceAddress("Topolowa", 16, "32-500", "Chrzanów"),
            departments=sample_departments
        )

    def testTryGetDepartment(self):
        self.assertEqual(self.sample_hospital.TryGetDepartment(15), self.sample_hospital.departments[2])

    def testTryGetDepartmentFailed(self):
        self.assertIsNone(self.sample_hospital.TryGetDepartment(1))

    def testTakeInVictimToOneOfDepartments(self):
        sample_department: sor.Department = self.sample_hospital.TryGetDepartment(victim.EMERGENCY_DISCIPLINE_NUMBER)
        sample_state: victim.State = victim_test.CreateSampleState()
        sample_victim: victim.Victim = victim.Victim(1, tuple([sample_state]))
        sample_time: float = 65.0
        sample_beds_amount: int = sample_department.current_beds_count

        self.sample_hospital.TakeInVictimToOneOfDepartments(sample_victim, sample_time)

        AssertDepartmentTookInVictim(
            test_case=self, department=sample_department, sample_victim=sample_victim,
            sample_time=sample_time, sample_beds_amount=sample_beds_amount
        )

    def testNoFittingDepartments(self):
        sample_state: victim.State = victim_test.CreateSampleState()
        sample_victim: victim.Victim = victim.Victim(1, tuple([sample_state]))
        sample_time: float = 65.0
        self.sample_hospital.departments.pop()

        self.assertRaises(RuntimeError, self.sample_hospital.TakeInVictimToOneOfDepartments, sample_victim, sample_time)


if __name__ == '__main__':
    unittest.main()
