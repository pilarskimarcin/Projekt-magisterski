# -*- coding: utf-8 -*-
from typing import List
import unittest

from Skrypty import sor_classes as sor
from Skrypty import victim_classes as victim
from Testy import tests_utilities as tests_util


def CreateSampleIncidentPlace() -> sor.IncidentPlace:
    return sor.IncidentPlace(
        tests_util.CreateSampleAddressIncident(),
        CreateSampleVictims()
    )


def CreateSampleVictims() -> List[victim.Victim]:
    sample_state1: victim.State = victim.State(
        number=1, is_victim_walking=False, respiratory_rate=12, pulse_rate=120, is_victim_following_orders=True,
        triage_colour=victim.TriageColour.YELLOW, health_problems=[
            victim.HealthProblem(25, 1), victim.HealthProblem(25, 4)
        ], description=u"Kobieta lat 17 zgłasza problem z poruszaniem się, na prośbę o opuszczenie strefy "
                       u"niebezpiecznej, zgłasza ból w obrębie stawu kolanowego, dolegliwości uniemożliwiają "
                       u"samodzielne poruszanie się, dolegliwości bólowe w obrębie stawu barkowego (widoczna "
                       u"asymetria barku lewego w stosunku do prawego, bolesność palpacyjna).")
    sample_state2: victim.State = victim.State(
        number=1, is_victim_walking=False, respiratory_rate=12, pulse_rate=130, is_victim_following_orders=True,
        triage_colour=victim.TriageColour.YELLOW, health_problems=[
            victim.HealthProblem(25, 2)
        ], description=u"Mężczyzna lat 13 zgłasza problem z poruszaniem się, na prośbę o opuszczenie strefy "
                       u"niebezpiecznej, zgłasza ból w obrębie piszczeli prawej, widoczna deformacja, widoczny uraz "
                       u"głowy nie wymagający interwencji chirurgicznej.")
    return [
        victim.Victim(1, [sample_state1]), victim.Victim(2, [sample_state1]),
        victim.Victim(3, [sample_state2]), victim.Victim(4, [sample_state2]),
    ]


class IncidentPlaceTests(unittest.TestCase):
    sample_incident_place: sor.IncidentPlace

    def setUp(self):
        self.sample_incident_place = CreateSampleIncidentPlace()

    def testGetStartingAmountOfVictims(self):
        while len(self.sample_incident_place.victims) < 88:
            self.sample_incident_place.victims.extend(CreateSampleVictims())

        self.assertEqual(26 <= self.sample_incident_place.GetStartingAmountOfVictims() <= 66, True)

    def testTryTakeVictimCorrectId(self):
        sample_victim_id: int = 1
        sample_victim: victim.Victim = CreateSampleVictims()[0]

        self.assertEqual(self.sample_incident_place.TryTakeVictim(sample_victim_id), sample_victim)

    def testTryTakeVictimWrongId(self):
        sample_victim_id: int = 5

        self.assertIsNone(self.sample_incident_place.TryTakeVictim(sample_victim_id))

    def testNeedsReconnaissanceTrue(self):
        self.assertTrue(self.sample_incident_place.NeedsReconnaissance())

    def testNeedsReconnaissanceFalse(self):
        self.sample_incident_place.reported_victims_count = len(self.sample_incident_place.victims)

        self.assertFalse(self.sample_incident_place.NeedsReconnaissance())


def AssertDepartmentTookInVictim(
        test_case: unittest.TestCase, department: sor.Department, sample_victim: victim.Victim, sample_time: float,
        sample_beds_amount: int
):
    test_case.assertEqual(department.admitted_victims, [sample_victim])
    test_case.assertEqual(department.admitted_victims[0].hospital_admittance_time, sample_time)
    test_case.assertEqual(department.current_beds_count, sample_beds_amount - 1)


def CreateSampleDepartment() -> sor.Department:
    return sor.Department(
        id_=4, name="Oddział chirurgii naczyniowej", medical_categories=[39, 37], current_beds_count=15
    )


class DepartmentTests(unittest.TestCase):
    sample_department: sor.Department
    sample_victim: victim.Victim
    sample_time: int

    def setUp(self):
        self.sample_department = CreateSampleDepartment()
        self.sample_victim = CreateSampleVictims()[0]
        self.sample_time = 65

    def testInit(self):
        self.assertEqual(self.sample_department.admitted_victims, [])

    def testEquality(self):
        self.assertEqual(CreateSampleDepartment(), self.sample_department)

    def testInequality(self):
        sample_department: sor.Department = CreateSampleDepartment()
        sample_department.current_beds_count -= 1

        self.assertNotEqual(sample_department, self.sample_department)

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
    sample_departments: List[sor.Department]
    sample_hospital: sor.Hospital

    def setUp(self):
        self.sample_departments = [
            sor.Department(id_=1, name="Oddział chirurgii urazowo-ortopedycznej", medical_categories=[25],
                           current_beds_count=22),
            CreateSampleDepartment(),
            sor.Department(id_=6, name="Szpitalny Oddział Ratunkowy", medical_categories=[15],
                           current_beds_count=12)
        ]
        self.sample_hospital = self.CreateSampleHospital()

    def CreateSampleHospital(self) -> sor.Hospital:
        return sor.Hospital(
            id_=1, name="Szpital Powiatowy w Chrzanowie",
            address=sor.PlaceAddress("Topolowa", "16", "32-500", "Chrzanów"),
            departments=self.sample_departments
        )

    def testEquality(self):
        self.assertEqual(self.CreateSampleHospital(), self.sample_hospital)

    def testInequality(self):
        sample_hospital: sor.Hospital = self.CreateSampleHospital()
        sample_hospital.id_ = 2

        self.assertNotEqual(sample_hospital, self.sample_hospital)

    def testTryGetDepartment(self):
        self.assertEqual(self.sample_hospital.TryGetDepartment(15), self.sample_hospital.departments[2])

    def testTryGetDepartmentNoFreeBeds(self):
        self.sample_hospital.TryGetDepartment(15).current_beds_count = 0

        self.assertIsNone(self.sample_hospital.TryGetDepartment(15))

    def testTryGetDepartmentNoFreeBedsBecauseIncoming(self):
        sample_department: sor.Department = self.sample_hospital.TryGetDepartment(15)
        sample_department.current_beds_count = 1
        self.sample_hospital.incoming_victims.setdefault(sample_department.id_, []).append(CreateSampleVictims()[0])

        self.assertIsNone(self.sample_hospital.TryGetDepartment(15))

    def testTryGetDepartmentWrongDiscipline(self):
        self.assertIsNone(self.sample_hospital.TryGetDepartment(1))

    def testTakeInVictimToOneOfDepartments(self):
        sample_victim: victim.Victim = CreateSampleVictims()[0]
        sample_department: sor.Department = self.sample_hospital.TryGetDepartment(
            sample_victim.GetCurrentHealthProblemDisciplines().pop()
        )
        sample_time: int = 65
        sample_beds_amount: int = sample_department.current_beds_count

        self.assertEqual(
            self.sample_hospital.TakeInVictimToOneOfDepartments(sample_victim, sample_time),
            sample_department
        )
        AssertDepartmentTookInVictim(
            test_case=self, department=sample_department, sample_victim=sample_victim, sample_time=sample_time,
            sample_beds_amount=sample_beds_amount
        )

    def testTakeInVictimToOneOfDepartmentsNoFittingDepartments(self):
        sample_victim: victim.Victim = CreateSampleVictims()[0]
        sample_time: float = 65.0
        self.sample_hospital.departments.pop(0)

        self.assertRaises(
            RuntimeError,
            self.sample_hospital.TakeInVictimToOneOfDepartments, sample_victim, sample_time
        )

    def testAvailableBedsInDepartmentNoIncomingVictims(self):
        sample_department: sor.Department = self.sample_hospital.departments[0]

        self.assertEqual(
            self.sample_hospital.AvailableBedsInDepartment(sample_department),
            sample_department.current_beds_count
        )

    def testAvailableBedsInDepartmentSomeIncomingVictims(self):
        sample_department: sor.Department = self.sample_hospital.departments[0]
        n_incoming_victims: int = 2  # max 4 - tyle zwraca CreateSampleVictims
        self.sample_hospital.incoming_victims[sample_department.id_] = CreateSampleVictims()[:n_incoming_victims]

        self.assertEqual(
            self.sample_hospital.AvailableBedsInDepartment(sample_department),
            sample_department.current_beds_count - n_incoming_victims
        )

    def testCanVictimBeTakenInTrueNoIncomingVictimsBefore(self):
        sample_victim: victim.Victim = CreateSampleVictims()[0]
        self.sample_hospital.departments.pop()
        sample_department_id: int = self.sample_hospital.departments[0].id_

        self.assertEqual(self.sample_hospital.CanVictimBeTakenIn(sample_victim), True)
        self.assertEqual(self.sample_hospital.incoming_victims[sample_department_id], [sample_victim])

    def testCanVictimBeTakenInTrueOneIncomingVictimBefore(self):
        sample_victim, sample_victim_2 = CreateSampleVictims()[:2]
        self.sample_hospital.departments.pop()
        sample_department_id: int = self.sample_hospital.departments[0].id_
        self.sample_hospital.incoming_victims[sample_department_id] = [sample_victim]

        self.assertEqual(self.sample_hospital.CanVictimBeTakenIn(sample_victim_2), True)
        self.assertEqual(
            self.sample_hospital.incoming_victims[sample_department_id],
            [sample_victim, sample_victim_2]
        )

    def testCanVictimBeTakenInNoDepartmentFalse(self):
        sample_victim: victim.Victim = CreateSampleVictims()[0]
        self.sample_hospital.departments.pop(0)

        self.assertEqual(self.sample_hospital.CanVictimBeTakenIn(sample_victim), False)

    def testCanVictimBeTakenInNoAvailableBedsFalse(self):
        sample_victim: victim.Victim = CreateSampleVictims()[0]
        self.sample_hospital.departments.pop()
        self.sample_hospital.departments[0].current_beds_count = 0

        self.assertEqual(self.sample_hospital.CanVictimBeTakenIn(sample_victim), False)

    def testCanVictimBeTakenInIsAlreadyIncomingError(self):
        sample_victim: victim.Victim = CreateSampleVictims()[0]
        self.sample_hospital.incoming_victims[self.sample_departments[0].id_] = [sample_victim]

        self.assertRaises(RuntimeError, self.sample_hospital.CanVictimBeTakenIn, sample_victim)

    def testIsVictimInIncomingVictimsIsInFirstItem(self):
        sample_victims: List[victim.Victim] = CreateSampleVictims()
        self.sample_hospital.incoming_victims[self.sample_departments[0].id_] = [sample_victims[0]]
        self.sample_hospital.incoming_victims[self.sample_departments[1].id_] = [sample_victims[1]]
        self.sample_hospital.incoming_victims[self.sample_departments[1].id_].append(sample_victims[2])

        self.assertEqual(self.sample_hospital.IsVictimInIncomingVictims(sample_victims[0]), True)

    def testIsVictimInIncomingVictimsIsInSecondItem(self):
        sample_victims: List[victim.Victim] = CreateSampleVictims()
        self.sample_hospital.incoming_victims[self.sample_departments[0].id_] = [sample_victims[0]]
        self.sample_hospital.incoming_victims[self.sample_departments[1].id_] = [sample_victims[1]]
        self.sample_hospital.incoming_victims[self.sample_departments[1].id_].append(sample_victims[2])

        self.assertEqual(self.sample_hospital.IsVictimInIncomingVictims(sample_victims[1]), True)

    def testIsVictimInIncomingVictimsFalse(self):
        sample_victims: List[victim.Victim] = CreateSampleVictims()
        self.sample_hospital.incoming_victims[self.sample_departments[0].id_] = [sample_victims[0]]
        self.sample_hospital.incoming_victims[self.sample_departments[1].id_] = [sample_victims[1]]
        self.sample_hospital.incoming_victims[self.sample_departments[1].id_].append(sample_victims[2])

        self.assertEqual(self.sample_hospital.IsVictimInIncomingVictims(sample_victims[3]), False)

    def testRemoveVictimFromIncomingNoSuchVictim(self):
        sample_victim, sample_victim_2 = CreateSampleVictims()[:2]
        prev_incoming_victims = self.sample_hospital.incoming_victims = {
            self.sample_departments[0].id_: [sample_victim]
        }
        self.sample_hospital.RemoveVictimFromIncoming(sample_victim_2)

        self.assertEqual(self.sample_hospital.incoming_victims, prev_incoming_victims)

    def testRemoveVictimFromIncomingOnlyOneIncomingForDepartment(self):
        sample_victim: victim.Victim = CreateSampleVictims()[0]
        self.sample_hospital.incoming_victims = {self.sample_departments[0].id_: [sample_victim]}
        self.sample_hospital.RemoveVictimFromIncoming(sample_victim)

        self.assertEqual(self.sample_hospital.incoming_victims, {})

    def testRemoveVictimFromIncomingManyVictimsIncomingForDepartment(self):
        sample_victim, sample_victim_2 = CreateSampleVictims()[:2]
        self.sample_hospital.incoming_victims = {
            self.sample_departments[0].id_: [sample_victim, sample_victim_2]
        }
        self.sample_hospital.RemoveVictimFromIncoming(sample_victim_2)

        self.assertEqual(
            self.sample_hospital.incoming_victims,
            {self.sample_departments[0].id_: [sample_victim]}
        )


if __name__ == "__main__":
    unittest.main()
