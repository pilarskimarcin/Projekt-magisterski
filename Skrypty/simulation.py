import math
import pandas as pd
import random
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
    additional_incidents: List[IncidentPlace]
    all_hospitals: List[Hospital]
    all_teams: List[ZRM]
    all_victims: List[Victim]
    main_incident: IncidentPlace
    available_procedures: List[Procedure]
    elapsed_simulation_time: int

    def __init__(self, main_scenario_path: str, additional_scenarios_paths: List[str]):
        main_scenario: Scenario = Scenario(main_scenario_path)
        self.additional_scenarios = []
        for additional_scenario_path in additional_scenarios_paths:
            self.additional_scenarios.append(Scenario(additional_scenario_path))
        self.additional_incidents = []
        self.all_hospitals = main_scenario.hospitals
        self.all_teams = main_scenario.teams
        self.all_victims = main_scenario.victims
        self.main_incident = IncidentPlace(
            main_scenario.address, main_scenario.victims
        )
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
        reported_victims_count: int = self.GetStartingAmountOfVictims()
        self.SendOutFirstTeamsToTheIncident(reported_victims_count)
        while not self.CheckIfSimulationEndReached():
            self.SimulationRegularStep()
            # TODO: Sprawdzić czy w poprzedniej turze coś się zdarzyło, dotarło się gdzieś itd
        # rozponanie ->

        # więcej jednostek ->

        # pomaganie i transport ->

        # wszyscy w szpitalu, KONIEC, zapisanie czasu zakończenia

    def GetStartingAmountOfVictims(self) -> int:
        victims_total_count: int = len(self.all_victims)
        return math.floor(random.uniform(0.3, 0.75) * victims_total_count)

    def GetTeamById(self, team_id: str) -> Optional[ZRM]:
        for team in self.all_teams:
            if team.id_ == team_id:
                return team
        return None

    def SendOutFirstTeamsToTheIncident(self, reported_victims_count: int):
        teams_times_to_reach_incident: List[Tuple[str, float]] = []
        for team in self.all_teams:
            teams_times_to_reach_incident.append(
                (team.id_, team.origin_location.CalculateDistanceAndDurationToOtherPlace(self.main_incident.address)[1])
            )
        teams_times_to_reach_incident.sort(key=lambda x: x[1])
        for count, team_and_time in enumerate(teams_times_to_reach_incident):
            team_id, _ = team_and_time
            if count < reported_victims_count:
                team: ZRM = self.GetTeamById(team_id)
                team.StartDriving(self.main_incident)

    def CheckIfSimulationEndReached(self) -> bool:
        for victim in self.all_victims:
            if not victim.has_been_assessed:
                return False
            if not victim.IsDead() and not victim.HasBeenAdmittedToHospital():
                return False
        return True

    def SimulationRegularStep(self):
        self.elapsed_simulation_time += 1
        for team in self.all_teams:
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
