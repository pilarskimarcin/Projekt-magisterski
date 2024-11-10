from __future__ import annotations
import pandas as pd
import random
from typing import List, NamedTuple, Optional, Set, Tuple

from scenario_classes import Scenario
from sor_classes import Department, Hospital, IncidentPlace
from utilities import PlaceAddress, TargetDestination
from victim_classes import HealthProblem, Procedure, TriageColour, Victim
from zrm_classes import Specialist, ZRM

# Stałe
PROCEDURES_CSV_TIME_COLUMN_NAME: str = "Czas wykonania przez ratowników [min]"
PROCEDURES_CSV_PROCEDURE_COLUMN_NAME: str = "Procedura medyczna"


class Simulation:
    # additional_scenarios: List[Scenario]
    incidents: List[IncidentPlace]  # czy zmienić na tylko jedno miejsce?
    all_hospitals: List[Hospital]
    idle_teams: List[ZRM]
    teams_in_action: List[ZRM]
    all_victims: List[Victim]
    unknown_status_victims: List[Victim]
    assessed_victims: List[Victim]
    transport_ready_victims: List[Victim]
    available_procedures: List[Procedure]
    elapsed_simulation_time: int
    solution: List[SolutionRecord]
    current_solution_index: int

    def __init__(self, main_scenario_path: str):  # , additional_scenarios_paths: List[str]):
        main_scenario: Scenario = Scenario(main_scenario_path)
        # self.additional_scenarios = []
        # for additional_scenario_path in additional_scenarios_paths:
        #     self.additional_scenarios.append(Scenario(additional_scenario_path))
        main_incident: IncidentPlace = IncidentPlace(main_scenario.address, main_scenario.victims)
        self.incidents = [main_incident]
        self.all_hospitals = main_scenario.hospitals
        self.SortHospitals()
        self.idle_teams = main_scenario.teams
        self.teams_in_action = []
        self.all_victims = main_scenario.victims
        random.shuffle(self.all_victims)
        self.unknown_status_victims = self.all_victims[:]
        self.assessed_victims = []
        self.transport_ready_victims = []
        self.available_procedures = self.LoadProcedures()
        self.elapsed_simulation_time = 0
        self.solution = []
        self.current_solution_index = 1

    def __repr__(self):
        return str(self.__dict__)

    def SortHospitals(self):
        hospitals_times_to_incident: List[float] = []
        for hospital in self.all_hospitals:
            hospitals_times_to_incident.append(
                self.incidents[0].address.GetDistanceAndDurationToOtherPlace(hospital.address)[1]
            )
        hospitals_and_times: List[Tuple[Hospital, float]] = list(zip(self.all_hospitals, hospitals_times_to_incident))
        hospitals_and_times.sort(key=lambda x: x[1])
        hospitals_tuple, _ = list(zip(*hospitals_and_times))
        self.all_hospitals = list(hospitals_tuple)

    @staticmethod
    def LoadProcedures() -> List[Procedure]:
        procedures_dataframe: pd.DataFrame = pd.read_csv(
            "../Dane/Procedury.csv", index_col=0, header=0, encoding="utf8", sep=";"
        )
        available_procedures: pd.DataFrame = procedures_dataframe[
            procedures_dataframe[PROCEDURES_CSV_TIME_COLUMN_NAME] != "-"
            ]
        times: pd.Series = available_procedures[PROCEDURES_CSV_TIME_COLUMN_NAME]
        procedure_symbols: pd.Series = available_procedures[PROCEDURES_CSV_PROCEDURE_COLUMN_NAME]
        return [
            Procedure.FromString(procedure_string, time)
            for procedure_string, time in zip(procedure_symbols.values, times.values)
        ]

    def PerformSimulation(self) -> SimulationResultsTuple:
        main_incident: IncidentPlace = self.incidents[0]
        first_team: ZRM = self.SendOutNTeamsToTheIncidentReturnFirst(
            main_incident, main_incident.reported_victims_count
        )
        while not self.CheckIfSimulationEndReached():
            self.SimulationTimeProgresses()
            for incident in self.incidents:
                self.TryHandleReconnaissance(first_team, incident)
            for team in self.teams_in_action:
                if not team.IsDriving() and not team.are_specialists_outside:
                    self.OrderIdleTeamInAction(team)
                if team.are_specialists_outside and team.AreSpecialistsIdle():
                    self.OrderIdleSpecialists(team)
        return self.SimulationResults()

    def SendOutNTeamsToTheIncidentReturnFirst(self, incident_place: IncidentPlace, n_teams_to_send: int) -> ZRM:
        """Wysyła pierwsze zespoły na miejsce wypadku, zwraca ten, który przyjedzie pierwszy"""
        teams_times_to_reach_incident: List[Tuple[str, float]] = (
            self.GetTeamsWithoutQueueAndTimesToReachTheAddressAscending(
                self.idle_teams, incident_place.address
            )
        )
        for count, team_and_time in enumerate(teams_times_to_reach_incident):
            team_id, _ = team_and_time
            if count >= n_teams_to_send:
                break
            else:
                team: ZRM = self.GetTeamById(team_id)
                team.StartDriving(incident_place)
                self.TeamIntoAction(team)
        return self.GetTeamById(teams_times_to_reach_incident[0][0])

    @staticmethod
    def GetTeamsWithoutQueueAndTimesToReachTheAddressAscending(teams: List[ZRM], address: PlaceAddress) \
            -> List[Tuple[str, float]]:
        teams_times_to_reach_incident: List[Tuple[str, float]] = []
        for team in teams:
            if team.queue_of_next_targets or team.are_specialists_outside:
                continue
            if team.IsDriving():
                time_to_reach_address: float = (
                        team.time_until_destination_in_minutes +
                        team.target_location.address.GetDistanceAndDurationToOtherPlace(address)[1]
                )
            else:
                time_to_reach_address: float = (
                    team.origin_location_address.GetDistanceAndDurationToOtherPlace(address)[1]
                )
            teams_times_to_reach_incident.append(
                (
                    team.id_,
                    time_to_reach_address
                )
            )
        teams_times_to_reach_incident.sort(key=lambda x: x[1])
        return teams_times_to_reach_incident

    def GetTeamById(self, team_id: str) -> Optional[ZRM]:
        for team in self.idle_teams + self.teams_in_action:
            if team.id_ == team_id:
                return team
        return None

    def TeamIntoAction(self, team: ZRM):
        if team not in self.idle_teams:
            return
        self.idle_teams.remove(team)
        self.teams_in_action.append(team)

    def CheckIfSimulationEndReached(self) -> bool:
        if self.unknown_status_victims or self.transport_ready_victims or self.AnyRemainingAliveAssessedVictims():
            return False
        return len([victim.IsDead() for victim in self.assessed_victims]) + len(self.solution) == len(self.all_victims)

    def AnyRemainingAliveAssessedVictims(self) -> bool:
        return any([not victim.IsDead() for victim in self.assessed_victims])

    def SimulationTimeProgresses(self):
        self.elapsed_simulation_time += 1
        for team in self.teams_in_action:
            self.MoveTeam(team)
            team.SpecialistsContinuePerformingProcedures()
        for victim in self.all_victims:
            victim.LowerRPM(self.elapsed_simulation_time)

    def MoveTeam(self, team: ZRM):
        target_location: TargetDestination = team.target_location
        transported_victim: Optional[Victim] = team.DriveOrFinishDrivingAndReturnVictim()
        if transported_victim:
            if isinstance(target_location, Hospital):
                target_location.RemoveVictimFromIncoming(transported_victim)
                if transported_victim.IsDead():
                    self.assessed_victims.append(transported_victim)
                    return
                chosen_department: Department = target_location.TakeInVictimToOneOfDepartments(
                    transported_victim, self.elapsed_simulation_time
                )
                self.solution.append(SolutionRecord(
                    self.current_solution_index, transported_victim.id_, team.id_,
                    self.HospitalAndDepartmentId(target_location, chosen_department),
                    self.elapsed_simulation_time
                ))
                self.current_solution_index += 1
            else:
                raise RuntimeError(
                    f"Zespół {team.id_} dojechał z pacjentem {transported_victim.id_} na miejsce, które nie jest "
                    f"szpitalem"
                )

    @staticmethod
    def HospitalAndDepartmentId(hospital: Hospital, department: Department) -> str:
        return str(hospital.id_)+"-"+str(department.id_)

    def TryHandleReconnaissance(self, first_team: ZRM, incident_place: IncidentPlace):
        if incident_place.NeedsReconnaissance():
            if not first_team.are_specialists_outside:
                if not first_team.IsDriving():
                    self.PerformReconnaissance(first_team)
            elif first_team.AreSpecialistsIdle():
                n_newfound_victims: int = len(incident_place.victims) - incident_place.reported_victims_count
                incident_place.reported_victims_count = len(incident_place.victims)
                if self.idle_teams:
                    _ = self.SendOutNTeamsToTheIncidentReturnFirst(incident_place, n_newfound_victims)

    def PerformReconnaissance(self, first_team: ZRM):
        first_team.SpecialistsLeaveTheVehicle()
        for specialist in first_team.specialists:
            specialist.StartPerformingProcedure(self.GetReconnaissanceProcedure())

    def GetReconnaissanceProcedure(self):
        return self.GetProcedureByDisciplineAndNumber(0, 0)

    def GetProcedureByDisciplineAndNumber(self, discipline: int, number: int) -> Optional[Procedure]:
        for procedure in self.available_procedures:
            if procedure.health_problem.discipline == discipline and procedure.health_problem.number == number:
                return procedure
        return None

    def OrderIdleTeamInAction(self, team: ZRM):
        if team.queue_of_next_targets:
            team.StartDriving(team.queue_of_next_targets.pop())
        elif team.origin_location_address != self.incidents[0].address:
            team.StartDriving(self.incidents[0])
        elif self.transport_ready_victims:
            self.HandleTransportReadyVictims(team)
        else:
            team.SpecialistsLeaveTheVehicle()

    def HandleTransportReadyVictims(self, team: ZRM):
        self.SortVictimsListByRPM(self.transport_ready_victims)
        for victim in self.transport_ready_victims[:]:
            if victim.IsDead():
                self.MoveVictimFromTransportReadyToAssessed(victim)
                continue
            target_hospital: Hospital = self.FindAppropriateAvailableHospital(victim)
            if not target_hospital:
                raise RuntimeError("Nie ma szpitala, mogącego przyjąć tego pacjenta")
            team.StartTransportingAVictim(victim, target_hospital)
            self.transport_ready_victims.remove(victim)
            break

    def FindAppropriateAvailableHospital(self, target_victim: Victim) -> Optional[Hospital]:
        for hospital in self.all_hospitals:
            if hospital.CanVictimBeTakenIn(target_victim):
                return hospital
        return None

    @staticmethod
    def SortVictimsListByRPM(victims_list: List[Victim], descending: bool = False):
        victims_list.sort(key=lambda x: x.current_RPM_number, reverse=descending)

    def MoveVictimFromTransportReadyToAssessed(self, victim: Victim):
        if victim not in self.transport_ready_victims:
            return
        self.transport_ready_victims.remove(victim)
        self.assessed_victims.append(victim)

    def OrderIdleSpecialists(self, team: ZRM):
        for specialist in team.specialists:
            if self.unknown_status_victims:
                self.PerformTriage(specialist)
            elif self.AnyRemainingAssessedVictimsNeedingProcedures():
                self.HelpAssessedVictimOrPrepareForTransport(specialist, team)
            else:
                team.TrySpecialistsComeBackToTheVehicle()

    def AnyRemainingAssessedVictimsNeedingProcedures(self) -> bool:
        return any([not (victim.IsDead() or victim.under_procedure) for victim in self.assessed_victims])

    def PerformTriage(self, specialist: Specialist):
        random_unknown_status_victim: Victim = random.choice(self.unknown_status_victims)
        self.MoveVictimFromUnknownStatusToAssessed(random_unknown_status_victim)
        specialist.StartPerformingProcedure(self.GetTriageProcedure())

    def MoveVictimFromUnknownStatusToAssessed(self, victim: Victim):
        if victim not in self.unknown_status_victims:
            return
        self.unknown_status_victims.remove(victim)
        self.assessed_victims.append(victim)

    def GetTriageProcedure(self):
        return self.GetProcedureByDisciplineAndNumber(0, 1)

    def HelpAssessedVictimOrPrepareForTransport(self, specialist: Specialist, team: ZRM):
        while self.AnyRemainingAssessedVictimsNeedingProcedures():
            target_victim: Victim = self.GetTargetVictimForProcedure()
            target_victim_critical_problems: Set[HealthProblem] = target_victim.GetCurrentCriticalHealthProblems()
            if len(target_victim_critical_problems) == 0:
                non_critical_procedure_to_perform: Procedure = self.GetAnyPossibleProcedureToPerform(target_victim)
                if not non_critical_procedure_to_perform:
                    try:
                        self.PrepareVictimForTransportAndSendToClosestTeamQueue(target_victim, team)
                        continue
                    except RuntimeError:
                        break
                else:
                    specialist.StartPerformingProcedure(non_critical_procedure_to_perform, target_victim)
                    return
            else:
                health_problem_to_treat: HealthProblem = target_victim_critical_problems.pop()
                procedure_to_be_performed: Procedure = self.GetProcedureByDisciplineAndNumber(
                    health_problem_to_treat.discipline, health_problem_to_treat.number
                )
                specialist.StartPerformingProcedure(procedure_to_be_performed, target_victim)
                return
        if specialist == team.specialists[-1]:
            team.TrySpecialistsComeBackToTheVehicle()

    def GetTargetVictimForProcedure(self) -> Optional[Victim]:
        victims_yellow: List[Victim] = []
        victims_red: List[Victim] = []
        for victim in self.assessed_victims:
            if victim.under_procedure:
                continue
            match victim.current_state.triage_colour:
                case TriageColour.YELLOW:
                    victims_yellow.append(victim)
                case TriageColour.RED:
                    victims_red.append(victim)
        if victims_red:
            self.SortVictimsListByRPM(victims_red)
            return victims_red[0]
        elif victims_yellow:
            self.SortVictimsListByRPM(victims_yellow)
            return victims_yellow[0]
        return None

    def GetAnyPossibleProcedureToPerform(self, target_victim: Victim):
        base_problems: Set[HealthProblem] = set(
            target_victim.current_state.health_problems
        )
        healed_problems: Set[HealthProblem] = {
            procedure.health_problem for procedure in target_victim.procedures_performed_so_far
        }
        non_healed_problems: Set[HealthProblem] = base_problems.difference(healed_problems)
        for non_healed_problem in non_healed_problems:
            found_procedure: Optional[Procedure] = self.GetProcedureByDisciplineAndNumber(
                non_healed_problem.discipline, non_healed_problem.number
            )
            if found_procedure:
                return found_procedure
        return None

    def PrepareVictimForTransportAndSendToClosestTeamQueue(self, target_victim: Victim, team: ZRM):
        self.MoveVictimFromAssessedToTransportReady(target_victim)
        closest_zrm: Optional[ZRM] = self.GetClosestTeamWithoutQueue(team.origin_location_address)
        if not closest_zrm:
            raise RuntimeError("Brak dostępnych zespołów z pustą kolejką")
        incident_location: IncidentPlace = self.GetIncidentPlaceFromAddress(
            team.origin_location_address
        )
        closest_zrm.QueueNewTargetLocation(incident_location)

    def MoveVictimFromAssessedToTransportReady(self, victim: Victim):
        if victim not in self.assessed_victims:
            return
        self.assessed_victims.remove(victim)
        self.transport_ready_victims.append(victim)

    def GetClosestTeamWithoutQueue(self, target_address: PlaceAddress) -> Optional[ZRM]:
        teams_and_times = self.GetTeamsWithoutQueueAndTimesToReachTheAddressAscending(
            self.teams_in_action, target_address
        )
        closest_team_id, _ = teams_and_times[0] if teams_and_times else (None, None)
        return self.GetTeamById(closest_team_id) if closest_team_id else None

    def GetIncidentPlaceFromAddress(self, address: PlaceAddress) -> Optional[IncidentPlace]:
        for incident in self.incidents:
            if incident.address == address:
                return incident
        return None

    def SimulationResults(self) -> SimulationResultsTuple:
        if not self.CheckIfSimulationEndReached():
            raise RuntimeError("Symulacja jeszcze nie została zakończona")
        n_dead_victims: int = len(self.assessed_victims)
        average_RPM: float = self.CalculateAverageRPM()
        average_help_time: float = self.CalculateAverageHelpTime()
        return SimulationResultsTuple(
            n_dead_victims, round(average_RPM, 2), self.elapsed_simulation_time, round(average_help_time, 2)
        )

    def CalculateAverageRPM(self):
        return sum(victim.current_RPM_number for victim in self.all_victims) / len(self.all_victims)

    def CalculateAverageHelpTime(self) -> float:
        admitted_to_hospital_victims: List[Victim] = [
            victim for victim in self.all_victims if victim.hospital_admittance_time
        ]
        return (sum(victim.hospital_admittance_time for victim in admitted_to_hospital_victims) /
                len(admitted_to_hospital_victims)) if admitted_to_hospital_victims else 0


class SolutionRecord(NamedTuple):
    number: int
    victim_id: int
    team_id: str
    hospital_department_id: str
    elapsed_simulation_time: int

    def __repr__(self):
        return (f"{self.number}. (id poszkodowanego: {self.victim_id}, id zespołu: {self.team_id}, "
                f"id oddziału szpitalnego: {self.hospital_department_id}, "
                f"czas przyjęcia do szpitala: {self.elapsed_simulation_time})")


class SimulationResultsTuple(NamedTuple):
    dead_victims_count: int
    victims_average_RPM: float
    total_simulation_time_minutes: int
    average_help_time_minutes: float


if __name__ == '__main__':
    scenario_path: str = "../Scenariusze/Scenariusz 6.txt"
    print(Simulation(scenario_path).PerformSimulation())
