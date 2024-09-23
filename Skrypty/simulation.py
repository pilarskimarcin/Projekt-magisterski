import pandas as pd
from typing import List, Optional, Tuple

from Skrypty.scenario_classes import Scenario
from Skrypty.sor_classes import Hospital, IncidentPlace
from Skrypty.utilities import TargetDestination
from Skrypty.victim_classes import Procedure, Victim
from Skrypty.zrm_classes import ZRM

# Stałe
PROCEDURES_CSV_TIME_COLUMN_NAME: str = "Czas wykonania przez ratowników [min]"
PROCEDURES_CSV_PROCEDURE_COLUMN_NAME: str = "Procedura medyczna"


class Simulation:
    additional_scenarios: List[Scenario]
    incidents: List[IncidentPlace]
    all_hospitals: List[Hospital]
    idle_teams: List[ZRM]
    teams_in_action: List[ZRM]
    all_victims: List[Victim]
    available_procedures: List[Procedure]
    elapsed_simulation_time: int

    def __init__(self, main_scenario_path: str, additional_scenarios_paths: List[str]):
        main_scenario: Scenario = Scenario(main_scenario_path)
        self.additional_scenarios = []
        for additional_scenario_path in additional_scenarios_paths:
            self.additional_scenarios.append(Scenario(additional_scenario_path))
        main_incident: IncidentPlace = IncidentPlace(main_scenario.address, main_scenario.victims)
        self.incidents = [main_incident]
        self.all_hospitals = main_scenario.hospitals
        self.idle_teams = main_scenario.teams
        self.teams_in_action = []
        self.all_victims = main_scenario.victims
        self.available_procedures = self.LoadProcedures()
        self.elapsed_simulation_time = 0

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
            self.SimulationRegularStep()
            for incident in self.incidents:
                self.TryHandleReconnaissance(first_team, incident)
            # Mogą dojechać na miejsce inni - powinno assessować poszkodowanych i zacząć im pomagać
            # Koniec rekonesansu - wiadomo ile poszkodowanych, jeśli więcej niż karetek jadących/na miejscu to wysłać
            # tyle ile trzeba
            # TODO: Sprawdzić czy w poprzedniej turze coś się zdarzyło, dotarło się gdzieś itd
            # pomaganie i transport ->
        # wszyscy w szpitalu, KONIEC, zapisanie czasu zakończenia

    def SendOutNTeamsToTheIncidentReturnFirst(self, incident_place: IncidentPlace, n_teams_to_send: int) -> ZRM:
        """Wysyła pierwsze zespoły na miejsce wypadku, zwraca ten, który przyjedzie pierwszy"""
        teams_times_to_reach_incident: List[Tuple[str, float]] = self.TeamsAndTimesToReachTheIncidentAsc(incident_place)
        for count, team_and_time in enumerate(teams_times_to_reach_incident):
            team_id, _ = team_and_time
            if count < n_teams_to_send:
                team: ZRM = self.GetTeamById(team_id)
                team.StartDriving(incident_place)
                self.TeamIntoAction(team)
        return self.GetTeamById(teams_times_to_reach_incident[0][0])

    def TeamIntoAction(self, team: ZRM):
        self.idle_teams.remove(team)
        self.teams_in_action.append(team)

    def TeamsAndTimesToReachTheIncidentAsc(self, incident_place: IncidentPlace) -> List[Tuple[str, float]]:
        teams_times_to_reach_incident: List[Tuple[str, float]] = []
        for team in self.idle_teams:
            teams_times_to_reach_incident.append(
                (
                    team.id_,
                    team.origin_location_address.GetDistanceAndDurationToOtherPlace(incident_place.address)[1]
                )
            )
        teams_times_to_reach_incident.sort(key=lambda x: x[1])
        return teams_times_to_reach_incident

    def GetTeamById(self, team_id: str) -> Optional[ZRM]:
        for team in self.idle_teams + self.teams_in_action:
            if team.id_ == team_id:
                return team
        return None

    def SimulationRegularStep(self):
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
                    self.SendOutNTeamsToTheIncidentReturnFirst(incident_place, n_newfound_victims)

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

    def CheckIfSimulationEndReached(self) -> bool:
        for victim in self.all_victims:
            if not victim.has_been_assessed:
                return False
            if not victim.IsDead() and not victim.HasBeenAdmittedToHospital():
                return False
        return True
