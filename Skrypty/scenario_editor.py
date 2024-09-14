import os
import random

import pandas as pd
import PyQt6.QtCore as Qc
import PyQt6.QtGui as Qg
import PyQt6.QtWidgets as Qt
import sys
import traceback
from typing import Dict, List, Optional, Union

# Parametry dla Qt
FONT_SIZE: int = 8
MIN_HEIGHT: int = 300
MIN_WIDTH: int = 500

# Stałe
SOR_COLUMN_BEDS: str = "Liczba łóżek"
PROFILES_PATH: str = "../Profile pacjentów"
TABLE_COLUMN_SCALE_FACTOR: float = 1.8
TITLE: str = "Edytor scenariuszy - "
TITLE_OFFSET_IN_SCENARIO: int = 1
ZRM_DATA_TITLE: str = "ZRM: "

# Włączenie Qt
app = Qt.QApplication(sys.argv)
sys.excepthook = lambda *args: (traceback.print_exception(*args, file=sys.stdout))
app.setFont(Qg.QFont("Arial", FONT_SIZE))


def CreateTableFromDataFrame(data: pd.DataFrame) -> Qt.QTableWidget:
    n_rows: int = len(data)
    n_cols: int = len(data.columns)
    table_widget = Qt.QTableWidget(n_rows, n_cols)
    table_widget.setHorizontalHeaderLabels(data.columns)
    for i in range(n_rows):
        for j in range(n_cols):
            table_widget.setItem(i, j, Qt.QTableWidgetItem(str(data.iloc[i][j])))
    table_widget.resizeColumnsToContents()
    table_widget.setSelectionMode(Qt.QTableWidget.SelectionMode.MultiSelection)
    return table_widget


def ClearLayout(layout: Qt.QLayout):
    for child_index in range(layout.count())[::-1]:
        item: Qt.QLayoutItem = layout.itemAt(child_index)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            ClearLayout(item.layout())
            item.layout().deleteLater()
        else:
            print(item)
    return


def FindIndexesOfSelectedRowsInTable(table: Union[Qt.QTableWidget, Qt.QListWidget]) -> List[int]:
    selected_rows: List[int] = list(
        {qmodel_index.row() for qmodel_index in table.selectedIndexes()}
    )
    selected_rows = sorted(selected_rows)
    return selected_rows


class MainApp(Qt.QMainWindow):
    """Klasa obejmująca główne okno aplikacji"""
    # Layout
    main_layout: Qt.QVBoxLayout
    temp_window: Qt.QWidget
    tab1_layout: Qt.QVBoxLayout
    tab1_scroll_widget: Qt.QScrollArea
    tab1_spin_boxes: List[Qt.QSpinBox]
    table_choice_SOR_button: Qt.QPushButton
    tab2_layout: Qt.QVBoxLayout
    tab2_scroll_widget: Qt.QScrollArea
    table_choice_ZRM_button: Qt.QPushButton
    tab3_layout: Qt.QVBoxLayout
    tab3_scroll_widget: Qt.QScrollArea
    tab3_spin_boxes: List[Qt.QSpinBox]
    list_choice_profiles_button: Qt.QPushButton
    new_scenario_button: Qt.QPushButton
    save_scenario_button: Qt.QPushButton
    open_scenario_button: Qt.QPushButton

    # Inne pola
    chosen_SOR_departments: Dict[int, int]
    chosen_ZRM_teams: List[int]
    chosen_profiles: Dict[str, int]
    current_file: str
    is_saved: bool
    victims_number: int

    def __init__(self):
        super(MainApp, self).__init__()
        self.ClearEverything()
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.MoveToMiddleOfScreen()
        self.Layout()
        self.ConnectMainSignals()

    def ClearEverything(self):
        self.chosen_SOR_departments = {}
        self.tab1_spin_boxes = []
        self.chosen_ZRM_teams = []
        self.chosen_profiles = {}
        self.victims_number = 0
        self.tab3_spin_boxes = []
        self.current_file = ""
        self.is_saved = False
        self.SetWindowTitle()

    def SetWindowTitle(self):
        if self.current_file == "":
            self.setWindowTitle(TITLE + "nowy*")
        else:
            self.setWindowTitle(TITLE + self.current_file.split("/")[-1])

    def MoveToMiddleOfScreen(self):
        max_size: Qc.QSize = self.screen().availableSize()
        self.move((max_size.width() - MIN_WIDTH) // 2, (max_size.height() - MIN_HEIGHT) // 2)

    def Layout(self):
        self.CreateTabsForMainWindow()
        self.CreateAndAddButtons()

    def CreateTabsForMainWindow(self):
        self.tab1_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.tab1_scroll_widget = Qt.QScrollArea()
        tab1: Qt.QWidget = self.CreateTab(self.tab1_layout, self.tab1_scroll_widget)

        self.tab2_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.tab2_scroll_widget = Qt.QScrollArea()
        tab2: Qt.QWidget = self.CreateTab(self.tab2_layout, self.tab2_scroll_widget)

        self.tab3_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.tab3_scroll_widget = Qt.QScrollArea()
        tab3: Qt.QWidget = self.CreateTab(self.tab3_layout, self.tab3_scroll_widget)

        tab_widget: Qt.QTabWidget = Qt.QTabWidget()
        tab_widget.addTab(tab1, "Oddziały SOR")
        tab_widget.addTab(tab2, "ZRM")
        tab_widget.addTab(tab3, "Profile pacjentów")
        self.CreateMainLayoutFromTabWidget(tab_widget)
        self.UpdateThreeTabs()

    @staticmethod
    def CreateTab(tab_layout: Qt.QVBoxLayout, tab_scroll_widget: Qt.QScrollArea) -> Qt.QWidget:
        tab: Qt.QWidget = Qt.QWidget()
        tab_layout.addWidget(tab_scroll_widget)
        tab.setLayout(tab_layout)
        return tab

    def CreateMainLayoutFromTabWidget(self, tab_widget: Qt.QTabWidget):
        self.main_layout = Qt.QVBoxLayout()
        self.main_layout.addWidget(tab_widget)
        widget: Qt.QWidget = Qt.QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def UpdateThreeTabs(self):
        self.UpdateSOR()
        self.UpdateZRM()
        self.UpdateProfiles()

    def UpdateSOR(self):
        ClearLayout(self.tab1_layout)
        self.tab1_spin_boxes = []
        self.CreateScrollAreaForSORTab()

        self.table_choice_SOR_button.clicked.connect(self.CreateTableToChooseSORDepartments)

    def CreateScrollAreaForSORTab(self):
        tab1_widget: Qt.QWidget = self.CreateWidgetWithSORContents()
        self.tab1_scroll_widget = Qt.QScrollArea()
        self.tab1_scroll_widget.setWidget(tab1_widget)
        self.tab1_layout.addWidget(self.tab1_scroll_widget)
        self.table_choice_SOR_button = Qt.QPushButton("Wybierz oddziały")
        self.tab1_layout.addWidget(self.table_choice_SOR_button)

    def CreateWidgetWithSORContents(self) -> Qt.QWidget:
        tab1_widget = Qt.QWidget()
        tab1_widget.setLayout(Qt.QVBoxLayout())
        tab1_widget.layout().addWidget(Qt.QLabel("Oddziały uwzględnione w scenariuszu"))
        for department_number, beds_count in self.chosen_SOR_departments.items():
            tab1_widget.layout().addLayout(self.CreateRowOfSORItems(department_number, beds_count), 1)
        return tab1_widget

    def CreateRowOfSORItems(self, department_number: int, beds_count: int) -> Qt.QHBoxLayout:
        row: Qt.QHBoxLayout = Qt.QHBoxLayout()
        row.addWidget(Qt.QLabel("Oddział " + str(department_number) + ", liczba wolnych łóżek: "))
        spin_box: Qt.QSpinBox = self.CreateSpinBox(beds_count)
        spin_box.setMaximum(beds_count)
        row.addWidget(spin_box)
        self.tab1_spin_boxes.append(spin_box)
        return row

    @staticmethod
    def CreateSpinBox(value: int) -> Qt.QSpinBox:
        spin_box = Qt.QSpinBox()
        spin_box.setValue(value)
        return spin_box

    def CreateAndAddButtons(self):
        self.new_scenario_button = Qt.QPushButton("Nowy")
        self.save_scenario_button = Qt.QPushButton("Zapisz")
        self.open_scenario_button = Qt.QPushButton("Otwórz")
        buttons: Qt.QHBoxLayout = Qt.QHBoxLayout()
        buttons.addWidget(self.new_scenario_button, 1)
        buttons.addWidget(self.save_scenario_button, 1)
        buttons.addWidget(self.open_scenario_button, 1)
        self.main_layout.addLayout(buttons)

    def ConnectMainSignals(self):
        self.new_scenario_button.clicked.connect(self.CreateNewScenario)
        self.save_scenario_button.clicked.connect(self.SaveScenario)
        self.open_scenario_button.clicked.connect(self.OpenExistingScenario)

    def UpdateZRM(self):
        ClearLayout(self.tab2_layout)
        self.CreateScrollAreaForZRMTab()
        self.table_choice_ZRM_button.clicked.connect(self.CreateTableToChooseZRMTeams)

    def CreateScrollAreaForZRMTab(self):
        self.tab2_scroll_widget = Qt.QScrollArea()
        self.tab2_scroll_widget.setWidget(self.CreateWidgetWithZRMData())
        self.tab2_layout.addWidget(self.tab2_scroll_widget)
        self.table_choice_ZRM_button = Qt.QPushButton("Wybierz zespoły")
        self.tab2_layout.addWidget(self.table_choice_ZRM_button)

    def CreateWidgetWithZRMData(self) -> Qt.QWidget:
        tab2_widget = Qt.QWidget()
        tab2_widget.setLayout(Qt.QVBoxLayout())
        tab2_widget.layout().addWidget(Qt.QLabel("Zespoły uwzględnione w scenariuszu"))
        for number in self.chosen_ZRM_teams:
            tab2_widget.layout().addWidget(Qt.QLabel("Zespół nr " + str(number)))
        return tab2_widget

    def UpdateProfiles(self):
        ClearLayout(self.tab3_layout)
        self.tab3_spin_boxes = []
        self.CreateScrollAreaForProfilesTab()
        self.list_choice_profiles_button.clicked.connect(self.CreateListViewToChooseProfiles)

    def CreateScrollAreaForProfilesTab(self):
        self.tab3_scroll_widget = Qt.QScrollArea()
        self.tab3_scroll_widget.setWidget(self.CreateWidgetWithProfilesContents())
        self.tab3_layout.addWidget(self.tab3_scroll_widget)
        row: Qt.QHBoxLayout = Qt.QHBoxLayout()
        row.addWidget(Qt.QLabel("Sumaryczna liczba ofiar: "))
        spin_box: Qt.QSpinBox = self.CreateSpinBox(self.victims_number)
        row.addWidget(spin_box)
        self.tab3_spin_boxes.append(spin_box)
        self.tab3_layout.addLayout(row, 1)
        self.list_choice_profiles_button = Qt.QPushButton("Wybierz profile")
        self.tab3_layout.addWidget(self.list_choice_profiles_button)

    def CreateWidgetWithProfilesContents(self) -> Qt.QWidget:
        tab3_widget = Qt.QWidget()
        tab3_widget.setLayout(Qt.QVBoxLayout())
        tab3_widget.layout().addWidget(Qt.QLabel("Profile uwzględnione w scenariuszu"))
        for profile, amount in self.chosen_profiles.items():
            row: Qt.QHBoxLayout = self.CreateRowOfProfilesItems(profile, amount)
            tab3_widget.layout().addLayout(row, 1)
        return tab3_widget

    def CreateRowOfProfilesItems(self, profile: str, amount: int):
        row: Qt.QHBoxLayout = Qt.QHBoxLayout()
        row.addWidget(Qt.QLabel(profile + " liczba ofiar: "))
        spin_box: Qt.QSpinBox = self.CreateSpinBox(amount)
        row.addWidget(spin_box)
        self.tab3_spin_boxes.append(spin_box)
        return row

    def CreateTableToChooseSORDepartments(self):
        self.temp_window = Qt.QWidget()
        self.temp_window.setWindowTitle("Zaznacz oddziały do uwzględnienia w scenariuszu")
        self.temp_window.setFixedSize(MIN_WIDTH, MIN_HEIGHT)
        temp_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.temp_window.setLayout(temp_layout)
        temp_data: pd.DataFrame = LoadSOR()
        table_SOR_departaments: Qt.QTableWidget = CreateTableFromDataFrame(temp_data)
        # Dwie kolumny muszą być ręcznie zmniejszone
        table_SOR_departaments.setColumnWidth(2, int(table_SOR_departaments.columnWidth(2) / TABLE_COLUMN_SCALE_FACTOR))
        table_SOR_departaments.setColumnWidth(4, int(table_SOR_departaments.columnWidth(4) / TABLE_COLUMN_SCALE_FACTOR))
        temp_layout.addWidget(table_SOR_departaments)
        accept_button: Qt.QPushButton = Qt.QPushButton("Wybierz zaznaczone oddziały")
        temp_layout.addWidget(accept_button)

        def ChooseSelectedSORRows():
            self.chosen_SOR_departments = {}
            selected_rows: List[int] = FindIndexesOfSelectedRowsInTable(table_SOR_departaments)
            # Domyślnie podane maksymalne możliwe liczby łóżek na oddziałach
            SOR_ids: pd.Series = temp_data.index.to_series()
            SOR_beds_counts: pd.Series = temp_data[SOR_COLUMN_BEDS]
            for row_index in selected_rows:
                self.chosen_SOR_departments[SOR_ids.iloc[row_index]] = SOR_beds_counts.iloc[row_index]
            self.temp_window.close()
            self.UpdateSOR()

        accept_button.clicked.connect(ChooseSelectedSORRows)

        self.temp_window.show()

    def CreateTableToChooseZRMTeams(self):
        self.temp_window = Qt.QWidget()
        self.temp_window.setWindowTitle("Zaznacz zespoły do uwzględnienia w scenariuszu")
        self.temp_window.setFixedSize(MIN_WIDTH, MIN_HEIGHT)
        temp_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.temp_window.setLayout(temp_layout)
        temp_data: pd.DataFrame = LoadZRM()
        table_ZRM_teams: Qt.QTableWidget = CreateTableFromDataFrame(temp_data)
        temp_layout.addWidget(table_ZRM_teams)
        accept_button: Qt.QPushButton = Qt.QPushButton("Wybierz zaznaczone zespoły")
        temp_layout.addWidget(accept_button)

        def ChooseSelectedZRMRows():
            self.chosen_ZRM_teams = []
            selected_rows: List[int] = FindIndexesOfSelectedRowsInTable(table_ZRM_teams)
            ZRM_ids: pd.Series = temp_data.index.to_series()
            for row_index in selected_rows:
                self.chosen_ZRM_teams.append(ZRM_ids.iloc[row_index])
            self.temp_window.close()
            self.UpdateZRM()

        accept_button.clicked.connect(ChooseSelectedZRMRows)
        self.temp_window.show()

    def CreateListViewToChooseProfiles(self):
        self.temp_window = Qt.QWidget()
        self.temp_window.setWindowTitle("Zaznacz profile do uwzględnienia w scenariuszu")
        self.temp_window.setFixedSize(MIN_WIDTH, MIN_HEIGHT)
        temp_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.temp_window.setLayout(temp_layout)
        temp_data: List[str] = LoadProfiles()
        list_profiles: Qt.QListWidget = Qt.QListWidget()
        for item in temp_data:
            list_profiles.addItem(item)
        list_profiles.setSelectionMode(Qt.QTableWidget.SelectionMode.MultiSelection)
        temp_layout.addWidget(list_profiles)
        accept_button: Qt.QPushButton = Qt.QPushButton("Wybierz zaznaczone profile")
        temp_layout.addWidget(accept_button)

        def ChooseSelectedProfiles():
            self.chosen_profiles = {}
            selected_rows: List[int] = FindIndexesOfSelectedRowsInTable(list_profiles)
            # Domyślnie 1 ofiara o danym profilu
            for row_index in selected_rows:
                profile: str = temp_data[row_index]
                self.chosen_profiles[profile] = 1
            # Liczba ofiar to liczba profili początkowo
            self.victims_number = len(self.chosen_profiles)
            self.temp_window.close()
            self.UpdateProfiles()

        accept_button.clicked.connect(ChooseSelectedProfiles)
        self.temp_window.show()

    def EmergencySaveScenario(self):
        if (
                not self.is_saved and (
                len(self.chosen_SOR_departments) != 0 or len(self.chosen_ZRM_teams) != 0 or
                len(self.chosen_profiles) != 0)
        ):
            result: int = Qt.QMessageBox.question(
                self, "Błąd",
                "Obecnie utworzony scenariusz nie został zapisany.\nCzy chcesz go zapisać przed utworzeniem nowego?"
            )
            if result == Qt.QMessageBox.StandardButton.Yes:
                self.SaveScenario()

    def CreateNewScenario(self):
        self.EmergencySaveScenario()
        self.ClearEverything()
        self.UpdateThreeTabs()

    def SaveScenario(self):
        if self.CheckIfNotEnoughData():
            return
        self.UpdateVictimsCounts()
        self.SaveFileChoice()
        if self.current_file == "":  # Anulowano
            return
        address: Optional[str] = self.GetAddressOfTheIncident()
        if address is None:  # Anulowano
            return
        saved_contents: str = ""
        saved_contents += self.SaveSORData()
        saved_contents += self.SaveZRMData()
        saved_contents += self.SaveProfilesData()
        saved_contents += f"\nAdres: {address}"
        self.SaveContentsIntoFile(saved_contents)

    def CheckIfNotEnoughData(self) -> bool:
        if len(self.chosen_SOR_departments) == 0 or len(self.chosen_ZRM_teams) == 0 or len(self.chosen_profiles) == 0:
            Qt.QMessageBox(
                Qt.QMessageBox.Icon.Warning, "Błąd",
                "Nie wszystkie elementy uwzględnione w scenariuszu zostały wybrane",
                Qt.QMessageBox.StandardButton.Ok, self
            ).exec()
            return True
        return False

    def UpdateVictimsCounts(self):
        for index, profile in enumerate(self.chosen_profiles.keys()):
            self.chosen_profiles[profile] = self.tab3_spin_boxes[index].value()
        victims_number_spinbox: Qt.QSpinBox = self.tab3_spin_boxes[-1]
        self.victims_number = victims_number_spinbox.value()
        n_known_victims: int = sum(self.chosen_profiles.values())
        if n_known_victims >= self.victims_number:
            self.victims_number = n_known_victims
        else:
            random_profile: str
            for _ in range(self.victims_number - n_known_victims):
                random_profile = random.choice(list(self.chosen_profiles.keys()))
                self.chosen_profiles[random_profile] += 1

    def SaveFileChoice(self):
        if self.current_file == "":
            self.current_file, _ = Qt.QFileDialog.getSaveFileName(
                self, "Zapisz scenariusz", "Scenariusze", "Pliki tekstowe (*.txt)"
            )

    def GetAddressOfTheIncident(self):
        choice = Qt.QInputDialog(self)
        choice.setCancelButtonText("Anuluj")
        results = choice.getText(self, "Adres zdarzenia", "Podaj adres zdarzenia")
        if not results[1]:
            return None
        return results[0]

    def SaveSORData(self) -> str:
        saved_contents: str = "Oddziały - liczba miejsc\n"
        department_beds_count: int
        for index, profile in enumerate(self.chosen_SOR_departments.keys()):
            department_beds_count = self.tab1_spin_boxes[index].value()
            saved_contents += f"{profile} {department_beds_count}\n"
        return saved_contents

    def SaveZRMData(self) -> str:
        saved_contents: str = f"\n{ZRM_DATA_TITLE}{', '.join([str(team_id) for team_id in self.chosen_ZRM_teams])}\n"
        return saved_contents

    def SaveProfilesData(self) -> str:
        saved_contents: str = "\nProfile - liczba poszkodowanych\n"
        for profile, counts_of_victims_per_profile in self.chosen_profiles.items():
            saved_contents += f"{profile} {counts_of_victims_per_profile}\n"
        saved_contents += f"\nCałkowita liczba poszkodowanych: {self.victims_number}\n"
        return saved_contents

    def SaveContentsIntoFile(self, saved_contents: str):
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(saved_contents)
        Qt.QMessageBox(
            Qt.QMessageBox.Icon.Information, "Sukces", "Scenariusz zapisany prawidłowo",
            Qt.QMessageBox.StandardButton.Ok, self
        ).exec()
        self.SetWindowTitle()
        self.is_saved = True
        return

    def OpenExistingScenario(self):
        self.EmergencySaveScenario()
        self.ClearEverything()
        self.current_file, _ = Qt.QFileDialog.getOpenFileName(
            self, "Otwórz scenariusz", "Scenariusze", "Pliki tekstowe (*.txt)"
        )
        if self.current_file == "":  # Cancelled
            return
        with open(self.current_file, "r", encoding="utf-8") as f:
            departments_part: str
            teams_part: str
            victims_part: str
            total_victims_part: str
            departments_part, teams_part, victims_part, total_victims_part = f.read().split("\n\n")
            self.ParseDepartments(departments_part)
            self.ParseTeams(teams_part)
            self.ParseProfiles(victims_part)
            self.ParseTotalVictimsCount(total_victims_part)
        self.is_saved = True
        self.SetWindowTitle()
        self.UpdateThreeTabs()

    def ParseDepartments(self, departments_data: str):
        for line in departments_data.split("\n")[TITLE_OFFSET_IN_SCENARIO:]:
            SOR_id, beds_number = line.split()
            self.chosen_SOR_departments[int(SOR_id)] = int(beds_number)

    def ParseTeams(self, teams_data: str):
        teams_data_without_title: str = teams_data[len(ZRM_DATA_TITLE):]
        self.chosen_ZRM_teams = [int(number) for number in teams_data_without_title.split(", ")]

    def ParseProfiles(self, profiles_data: str):
        for line in profiles_data.split("\n")[TITLE_OFFSET_IN_SCENARIO:]:
            profile, amount = line.split()
            self.chosen_profiles[profile] = int(amount)

    def ParseTotalVictimsCount(self, total_victims_data: str):
        self.victims_number = int(total_victims_data.split()[-1])


def LoadSOR() -> pd.DataFrame:
    return pd.read_csv("../Dane/SOR.csv", encoding="utf-8", sep=";", index_col=0)


def LoadZRM() -> pd.DataFrame:
    return pd.read_csv("../Dane/ZRM.csv", encoding="utf-8", sep=";", index_col=0)


def LoadProfiles() -> List[str]:
    data_profiles: List[str] = []
    for triage_colour_folder in os.listdir(PROFILES_PATH):
        for profile in os.listdir(PROFILES_PATH + "/" + triage_colour_folder):
            if profile.startswith("_"):  # Template
                continue
            profile = RemoveExtensionFromFile(profile)
            data_profiles.append(f"{triage_colour_folder}/{profile}")
    return data_profiles


def RemoveExtensionFromFile(file_name: str) -> str:
    return file_name[:-4]


if __name__ == '__main__':
    window = MainApp()
    window.show()
    app.exec()
