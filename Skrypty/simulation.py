import pandas as pd
import random
from typing import List, Optional, Tuple

from Skrypty.scenario_classes import Scenario
from Skrypty.sor_classes import Hospital, IncidentPlace
from Skrypty.utilities import PlaceAddress, TargetDestination
from Skrypty.victim_classes import HealthProblem, Procedure, TriageColour, Victim
from Skrypty.zrm_classes import ZRM
from zrm_classes import Specialist

# Stałe
PROCEDURES_CSV_TIME_COLUMN_NAME: str = "Czas wykonania przez ratowników [min]"
PROCEDURES_CSV_PROCEDURE_COLUMN_NAME: str = "Procedura medyczna"


class Simulation:
    # additional_scenarios: List[Scenario]
    incidents: List[IncidentPlace]  # TODO: czy zmienić na tylko jedno miejsce?
    all_hospitals: List[Hospital]
    idle_teams: List[ZRM]
    teams_in_action: List[ZRM]
    all_victims: List[Victim]
    unknown_status_victims: List[Victim]
    assessed_victims: List[Victim]
    transport_ready_victims: List[Victim]
    available_procedures: List[Procedure]
    elapsed_simulation_time: int

    def __init__(self, main_scenario_path: str):  # , additional_scenarios_paths: List[str]):
        main_scenario: Scenario = Scenario(main_scenario_path)
        # self.additional_scenarios = []
        # for additional_scenario_path in additional_scenarios_paths:
        #     self.additional_scenarios.append(Scenario(additional_scenario_path))
        main_incident: IncidentPlace = IncidentPlace(main_scenario.address, main_scenario.victims)
        self.incidents = [main_incident]
        self.all_hospitals = main_scenario.hospitals
        self.idle_teams = main_scenario.teams
        self.teams_in_action = []
        self.all_victims = main_scenario.victims
        random.shuffle(self.all_victims)
        self.unknown_status_victims = self.all_victims[:]
        self.assessed_victims = []
        self.transport_ready_victims = []
        self.available_procedures = self.LoadProcedures()
        self.elapsed_simulation_time = 0

    def __repr__(self):
        return str(self.__dict__)

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

    def PerformSimulation(self):
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
                    self.OrderIdleTeam(team)
                if team.are_specialists_outside and team.AreSpecialistsIdle():
                    self.OrderIdleSpecialists(team)
            # czy nowy wypadek z additional_scenarios?
        # sprawdzić wyniki symulacji

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
        if self.unknown_status_victims or self.transport_ready_victims:
            return False
        return not self.AnyRemainingAliveAssessedVictims()

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
                target_location.TakeInVictimToOneOfDepartments(
                    transported_victim, self.elapsed_simulation_time
                )
                self.transport_ready_victims.remove(transported_victim)
            else:
                raise RuntimeError(
                    f"Zespół {team.id_} dojechał z pacjentem {transported_victim.id_} na miejsce, które nie jest "
                    f"szpitalem"
                )

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
        reconnaissance_procedure: Procedure = self.GetProcedureByDisciplineAndNumber(0, 0)
        for specialist in first_team.specialists:
            specialist.StartPerformingProcedure(reconnaissance_procedure)

    def GetProcedureByDisciplineAndNumber(self, discipline: int, number: int) -> Optional[Procedure]:
        for procedure in self.available_procedures:
            if procedure.health_problem.discipline == discipline and procedure.health_problem.number == number:
                return procedure
        return None

    def OrderIdleTeam(self, team: ZRM):
        if team.queue_of_next_targets:
            team.StartDriving(team.queue_of_next_targets.pop())
        elif self.transport_ready_victims:
            # wziąć wg koloru (czerwony, żółty) i RPM rosnąco, jechać do szpitala
            pass
        else:
            team.SpecialistsLeaveTheVehicle()
        # TODO: albo ma jechać na miejsce wypadku - wtedy gdy zostanie przeniesiony ktoś na transport_ready

    def OrderIdleSpecialists(self, team: ZRM):
        for specialist in team.specialists:
            if self.unknown_status_victims:
                # triaż - 30sek/pacjenta, robić aż będzie puste unknown_status_victims - ile triażystów max?
                # zapisać w zmiennej liczbę triażystów
                pass
            elif self.AnyRemainingAliveAssessedVictims():
                self.HelpAssessedVictimOrPrepareForTransport(specialist, team)
            else:
                team.TrySpecialistsComeBackToTheVehicle()

    def HelpAssessedVictimOrPrepareForTransport(self, specialist: Specialist, team: ZRM):
        while self.AnyRemainingAliveAssessedVictims():
            target_victim: Victim = self.GetTargetVictimForProcedure()
            target_victim_critical_health_problems = target_victim.GetCurrentCriticalHealthProblems()
            if len(target_victim_critical_health_problems) == 0:
                try:
                    self.PrepareVictimForTransportAndSendToClosestTeamQueue(target_victim, team)
                    continue
                except RuntimeError:
                    break
            else:
                health_problem_to_treat: HealthProblem = target_victim_critical_health_problems.pop()
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

    @staticmethod
    def SortVictimsListByRPM(victims_list: List[Victim], descending: bool = False):
        victims_list.sort(key=lambda x: x.current_RPM_number, reverse=descending)

    def PrepareVictimForTransportAndSendToClosestTeamQueue(self, target_victim: Victim, team: ZRM):
        self.MoveVictimFromAssessedToTransportReady(target_victim)
        closest_zrm: Optional[ZRM] = self.GetClosestTeamWithoutQueue(team.origin_location_address)
        if not closest_zrm:
            raise RuntimeError("Brak dostępnych zespołów z pustą kolejką")
        incident_location: IncidentPlace = self.GetIncidentPlaceFromAddress(
            team.origin_location_address
        )
        closest_zrm.QueueNewTargetLocation(incident_location)

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

    def MoveVictimFromUnknownStatusToAssessed(self, victim: Victim):
        if victim not in self.unknown_status_victims:
            return
        self.unknown_status_victims.remove(victim)
        self.assessed_victims.append(victim)

    def MoveVictimFromAssessedToTransportReady(self, victim: Victim):
        if victim not in self.assessed_victims:
            return
        self.assessed_victims.remove(victim)
        self.transport_ready_victims.append(victim)
