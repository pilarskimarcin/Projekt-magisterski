import os
import random

import pandas as pd
import PyQt6.QtCore as Qc
import PyQt6.QtGui as Qg
import PyQt6.QtWidgets as Qt
import sys
import traceback
from typing import Dict, List

# Qt parameters
FONT_SIZE: int = 8
MIN_HEIGHT: int = 300
MIN_WIDTH: int = 500

# Other constants
SOR_COLUMN_ID: str = "Lp."
SOR_COLUMN_BEDS: str = "Liczba łóżek"
ZRM_COLUMN_ID: str = "Lp."
PROFILES_PATH: str = "Profile pacjentów"
TABLE_COLUMN_SCALE_FACTOR: float = 1.8
TITLE: str = "Edytor scenariuszy - "

# Starting Qt
app = Qt.QApplication(sys.argv)
sys.excepthook = lambda *args: (traceback.print_exception(*args, file=sys.stdout))
app.setFont(Qg.QFont("Arial", FONT_SIZE))


def table_generic(data: pd.DataFrame) -> Qt.QTableWidget:
    """
    Create a table from the input data
    :param data: pd.DataFrame
    :return: the created QTableWidget
    """
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


def clear_layout(layout: Qt.QLayout):
    for child_index in range(layout.count())[::-1]:
        item: Qt.QLayoutItem = layout.itemAt(child_index)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            clear_layout(item.layout())
            item.layout().deleteLater()
        else:
            print(item)
    return


class MainApp(Qt.QMainWindow):
    """
    The class corresponding to the main window of the app
    """
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

    # Other attributes
    chosen_SOR: Dict[int, int]
    chosen_ZRM: List[int]
    chosen_profiles: Dict[str, int]
    current_file: str
    is_saved: bool
    max_size: Qc.QSize
    victims_number: int

    def __init__(self):
        super(MainApp, self).__init__()
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.clear_everything()

        # Size
        self.max_size = self.screen().availableSize()
        self.move((self.max_size.width() - MIN_WIDTH) // 2, (self.max_size.height() - MIN_HEIGHT) // 2)

        # Adding to the layout
        self.layout()

        # Connecting signals
        self.new_scenario_button.clicked.connect(self.new_scenario)
        self.save_scenario_button.clicked.connect(self.save_scenario)
        self.open_scenario_button.clicked.connect(self.open_existing_scenario)

    def clear_everything(self):
        self.chosen_SOR = {}
        self.tab1_spin_boxes = []
        self.chosen_ZRM = []
        self.chosen_profiles = {}
        self.victims_number = 0
        self.tab3_spin_boxes = []
        self.current_file = ""
        self.is_saved = False
        self.set_window_title()

    def set_window_title(self):
        """Sets the title depending on whether it's an already saved file or a new one"""
        if self.current_file == "":
            self.setWindowTitle(TITLE + "nowy*")
        else:
            self.setWindowTitle(TITLE + self.current_file.split("/")[-1])

    def update_three_tabs(self):
        self.update_SOR()
        self.update_ZRM()
        self.update_profiles()

    def layout(self):
        """Adds all elements to the layout"""
        # The main window - 3 tabs
        tab1: Qt.QWidget = Qt.QWidget()
        self.tab1_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.tab1_scroll_widget = Qt.QScrollArea()
        self.tab1_layout.addWidget(self.tab1_scroll_widget)
        tab1.setLayout(self.tab1_layout)

        tab2: Qt.QWidget = Qt.QWidget()
        self.tab2_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.tab2_scroll_widget = Qt.QScrollArea()
        self.tab2_layout.addWidget(self.tab2_scroll_widget)
        tab2.setLayout(self.tab2_layout)

        tab3: Qt.QWidget = Qt.QWidget()
        self.tab3_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.tab3_scroll_widget = Qt.QScrollArea()
        self.tab3_layout.addWidget(self.tab3_scroll_widget)
        tab3.setLayout(self.tab3_layout)

        # Tab widget, containing the 3 tabs
        tab_widget: Qt.QTabWidget = Qt.QTabWidget()
        tab_widget.addTab(tab1, "Oddziały SOR")
        tab_widget.addTab(tab2, "ZRM")
        tab_widget.addTab(tab3, "Profile pacjentów")
        self.main_layout = Qt.QVBoxLayout()
        widget: Qt.QWidget = Qt.QWidget()
        widget.setLayout(self.main_layout)
        self.main_layout.addWidget(tab_widget)
        self.setCentralWidget(widget)
        self.update_three_tabs()

        # Buttons
        self.new_scenario_button = Qt.QPushButton("Nowy")
        self.save_scenario_button = Qt.QPushButton("Zapisz")
        self.open_scenario_button = Qt.QPushButton("Otwórz")
        buttons: Qt.QHBoxLayout = Qt.QHBoxLayout()
        buttons.addWidget(self.new_scenario_button, 1)
        buttons.addWidget(self.save_scenario_button, 1)
        buttons.addWidget(self.open_scenario_button, 1)
        self.main_layout.addLayout(buttons)

    def update_SOR(self):
        # Clearing everything in tab1
        clear_layout(self.tab1_layout)
        self.tab1_spin_boxes = []

        # Widget with all the contents of tab1
        tab1_widget = Qt.QWidget()
        tab1_widget.setLayout(Qt.QVBoxLayout())
        tab1_widget.layout().addWidget(Qt.QLabel("Oddziały uwzględnione w scenariuszu"))
        spin_box: Qt.QSpinBox
        for k, v in self.chosen_SOR.items():
            row: Qt.QHBoxLayout = Qt.QHBoxLayout()
            row.addWidget(Qt.QLabel("Oddział " + str(k) + ", liczba wolnych łóżek: "))
            spin_box = Qt.QSpinBox()
            spin_box.setValue(v)
            spin_box.setMaximum(v)
            row.addWidget(spin_box)
            self.tab1_spin_boxes.append(spin_box)
            tab1_widget.layout().addLayout(row, 1)

        # ScrollArea to contain the contents
        self.tab1_scroll_widget = Qt.QScrollArea()
        self.tab1_scroll_widget.setWidget(tab1_widget)
        self.tab1_layout.addWidget(self.tab1_scroll_widget)
        self.table_choice_SOR_button = Qt.QPushButton("Wybierz oddziały")
        self.tab1_layout.addWidget(self.table_choice_SOR_button)

        self.table_choice_SOR_button.clicked.connect(self.table_choice_SOR)

    def update_ZRM(self):
        # Clearing everything in tab2
        clear_layout(self.tab2_layout)

        # Widget with all the contents of tab2
        tab2_widget = Qt.QWidget()
        tab2_widget.setLayout(Qt.QVBoxLayout())
        tab2_widget.layout().addWidget(Qt.QLabel("Zespoły uwzględnione w scenariuszu"))
        for number in self.chosen_ZRM:
            tab2_widget.layout().addWidget(Qt.QLabel("Zespół nr " + str(number)))

        # ScrollArea to contain the contents
        self.tab2_scroll_widget = Qt.QScrollArea()
        self.tab2_scroll_widget.setWidget(tab2_widget)
        self.tab2_layout.addWidget(self.tab2_scroll_widget)
        self.table_choice_ZRM_button = Qt.QPushButton("Wybierz zespoły")
        self.tab2_layout.addWidget(self.table_choice_ZRM_button)

        self.table_choice_ZRM_button.clicked.connect(self.table_choice_ZRM)

    def update_profiles(self):
        # Clearing everything in tab3
        clear_layout(self.tab3_layout)
        self.tab3_spin_boxes = []

        # Widget with all the contents of tab2
        tab3_widget = Qt.QWidget()
        tab3_widget.setLayout(Qt.QVBoxLayout())
        tab3_widget.layout().addWidget(Qt.QLabel("Profile uwzględnione w scenariuszu"))
        spin_box: Qt.QSpinBox
        for profile, amount in self.chosen_profiles.items():
            row: Qt.QHBoxLayout = Qt.QHBoxLayout()
            row.addWidget(Qt.QLabel(profile + " liczba ofiar: "))
            spin_box = Qt.QSpinBox()
            spin_box.setValue(amount)
            row.addWidget(spin_box)
            self.tab3_spin_boxes.append(spin_box)
            tab3_widget.layout().addLayout(row, 1)

        # ScrollArea to contain the contents
        self.tab3_scroll_widget = Qt.QScrollArea()
        self.tab3_scroll_widget.setWidget(tab3_widget)
        self.tab3_layout.addWidget(self.tab3_scroll_widget)
        row: Qt.QHBoxLayout = Qt.QHBoxLayout()
        row.addWidget(Qt.QLabel("Sumaryczna liczba ofiar: "))
        spin_box = Qt.QSpinBox()
        spin_box.setValue(self.victims_number)
        row.addWidget(spin_box)
        self.tab3_spin_boxes.append(spin_box)
        self.tab3_layout.addLayout(row, 1)
        self.list_choice_profiles_button = Qt.QPushButton("Wybierz profile")
        self.tab3_layout.addWidget(self.list_choice_profiles_button)

        self.list_choice_profiles_button.clicked.connect(self.list_choice_profiles)

    def table_choice_SOR(self):
        """Create a table to choose SOR departments"""
        self.temp_window = Qt.QWidget()
        self.temp_window.setWindowTitle("Zaznacz oddziały do uwzględnienia w scenariuszu")
        self.temp_window.setFixedSize(MIN_WIDTH, MIN_HEIGHT)
        temp_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.temp_window.setLayout(temp_layout)
        temp_data: pd.DataFrame = load_SOR()
        table_SOR_depts: Qt.QTableWidget = table_generic(temp_data)
        # Two columns need to be shrinked a bit
        table_SOR_depts.setColumnWidth(2, int(table_SOR_depts.columnWidth(2) / TABLE_COLUMN_SCALE_FACTOR))
        table_SOR_depts.setColumnWidth(4, int(table_SOR_depts.columnWidth(4) / TABLE_COLUMN_SCALE_FACTOR))
        temp_layout.addWidget(table_SOR_depts)
        accept_button: Qt.QPushButton = Qt.QPushButton("Wybierz zaznaczone oddziały")
        temp_layout.addWidget(accept_button)

        def choose_selected_rows():
            self.chosen_SOR = {}
            # Find indexes of selected rows
            selected_rows: List[int] = sorted(list(
                {qmodelindex.row() for qmodelindex in table_SOR_depts.selectedIndexes()}
            ))
            # Add the max possible beds to each department in the saved data
            for row in selected_rows:
                self.chosen_SOR[temp_data[SOR_COLUMN_ID].iloc[row]] = temp_data[SOR_COLUMN_BEDS].iloc[row]
            self.temp_window.close()
            self.update_SOR()

        accept_button.clicked.connect(choose_selected_rows)

        self.temp_window.show()

    def table_choice_ZRM(self):
        """Create a table to choose ZRM teams"""
        self.temp_window = Qt.QWidget()
        self.temp_window.setWindowTitle("Zaznacz zespoły do uwzględnienia w scenariuszu")
        self.temp_window.setFixedSize(MIN_WIDTH, MIN_HEIGHT)
        temp_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.temp_window.setLayout(temp_layout)
        temp_data: pd.DataFrame = load_ZRM()
        table_ZRM_teams: Qt.QTableWidget = table_generic(temp_data)
        temp_layout.addWidget(table_ZRM_teams)
        accept_button: Qt.QPushButton = Qt.QPushButton("Wybierz zaznaczone zespoły")
        temp_layout.addWidget(accept_button)

        def choose_selected_rows():
            self.chosen_ZRM = []
            # Find indexes of selected rows
            selected_rows: List[int] = sorted(list(
                {qmodelindex.row() for qmodelindex in table_ZRM_teams.selectedIndexes()}
            ))
            # Adding the chosen teams to the saved data
            for row in selected_rows:
                self.chosen_ZRM.append(temp_data[ZRM_COLUMN_ID].iloc[row])
            self.temp_window.close()
            self.update_ZRM()

        accept_button.clicked.connect(choose_selected_rows)

        self.temp_window.show()

    def list_choice_profiles(self):
        """Create a list view to choose patients' profiles"""
        self.temp_window = Qt.QWidget()
        self.temp_window.setWindowTitle("Zaznacz profile do uwzględnienia w scenariuszu")
        self.temp_window.setFixedSize(MIN_WIDTH, MIN_HEIGHT)
        temp_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        self.temp_window.setLayout(temp_layout)
        temp_data: List[str] = load_profiles()
        list_profiles: Qt.QListWidget = Qt.QListWidget()
        for item in temp_data:
            list_profiles.addItem(item)
        list_profiles.setSelectionMode(Qt.QTableWidget.SelectionMode.MultiSelection)
        temp_layout.addWidget(list_profiles)
        accept_button: Qt.QPushButton = Qt.QPushButton("Wybierz zaznaczone profile")
        temp_layout.addWidget(accept_button)

        def choose_selected_profiles():
            self.chosen_profiles = {}
            # Find indexes of selected rows
            selected_rows: List[int] = sorted(list(
                {qmodelindex.row() for qmodelindex in list_profiles.selectedIndexes()}
            ))
            # Add each profile with base number of 1 patient with this profile
            for row in selected_rows:
                self.chosen_profiles[temp_data[row]] = 1
            # Base number of victims is equal to the chosen profiles
            self.victims_number = len(self.chosen_profiles)
            self.temp_window.close()
            self.update_profiles()

        accept_button.clicked.connect(choose_selected_profiles)

        self.temp_window.show()

    def new_scenario(self):
        """Create a new blank scenario"""
        if not self.is_saved:
            result: int = Qt.QMessageBox.question(
                self, "Błąd",
                "Obecnie utworzony scenariusz nie został zapisany.\nCzy chcesz go zapisać przed utworzeniem nowego?"
            )
            if result == Qt.QMessageBox.StandardButton.Yes:
                self.save_scenario()
        self.clear_everything()
        self.update_three_tabs()

    def save_scenario(self):
        """Save the scenario to a text file"""
        # Not enough data
        if len(self.chosen_SOR) == 0 or len(self.chosen_ZRM) == 0 or len(self.chosen_profiles) == 0:
            Qt.QMessageBox(
                Qt.QMessageBox.Icon.Warning, "Błąd",
                "Nie wszystkie elementy uwzględnione w scenariuszu zostały wybrane",
                Qt.QMessageBox.StandardButton.Ok, self
            ).exec()
            return

        # Filling up the profiles and their counts, based on chosen values in spin_boxes
        i: int = 0
        for k in self.chosen_profiles.keys():
            self.chosen_profiles[k] = self.tab3_spin_boxes[i].value()
            i += 1
        # The last spin_box corresponds to the total number of victims
        self.victims_number = self.tab3_spin_boxes[-1].value()
        n_victims_known: int = sum(self.chosen_profiles.values())
        if n_victims_known >= self.victims_number:  # If the number of victims wasn't updated
            self.victims_number = n_victims_known
        else:  # If the total number of victims is greater, so have to distribute the rest among the profiles randomly
            random_profile: str
            for _ in range(self.victims_number - n_victims_known):
                random_profile = random.choice(list(self.chosen_profiles.keys()))
                self.chosen_profiles[random_profile] += 1

        # File choice
        if self.current_file == "":
            self.current_file, _ = Qt.QFileDialog.getSaveFileName(
                self, "Zapisz scenariusz", "Scenariusze", "Pliki tekstowe (*.txt)"
            )
            if self.current_file == "":  # Cancelled
                return

        # SOR
        saved_contents: str = "Oddziały - liczba miejsc\n"
        i: int = 0
        v: int
        for k in self.chosen_SOR.keys():
            v = self.tab1_spin_boxes[i].value()  # The updated value is in the spin_box
            saved_contents += f"{k} {v}\n"
            i += 1

        # ZRM
        saved_contents += f"\nZRM: {', '.join([str(team_id) for team_id in self.chosen_ZRM])}\n"

        # Profiles
        saved_contents += "\nProfile - liczba poszkodowanych\n"
        for k, v in self.chosen_profiles.items():
            saved_contents += f"{k} {v}\n"
        saved_contents += f"\nCałkowita liczba poszkodowanych\n{self.victims_number}"

        # Saving
        with open(self.current_file, "w") as f:
            f.write(saved_contents)
        Qt.QMessageBox(
            Qt.QMessageBox.Icon.Information, "Sukces", "Scenariusz zapisany prawidłowo",
            Qt.QMessageBox.StandardButton.Ok, self
        ).exec()
        self.set_window_title()
        self.is_saved = True
        return

    def open_existing_scenario(self):
        """Open an existing scenario"""
        print("Not yet implemented")


def load_SOR() -> pd.DataFrame:
    return pd.read_csv("Dane/SOR.tsv", encoding="cp1250", delimiter="\t")


def load_ZRM() -> pd.DataFrame:
    return pd.read_csv("Dane/ZRM.tsv", encoding="cp1250", delimiter="\t")


def load_profiles() -> List[str]:
    data_profiles: List[str] = []
    # To get profiles from all 3 colours
    for folder in os.listdir(PROFILES_PATH):
        # To get each profile
        for profile in os.listdir(PROFILES_PATH + "/" + folder):
            profile = profile[:-4]  # -= ".txt"
            data_profiles.append(f"{folder}/{profile}")  # To indicate the colour too
    return data_profiles


if __name__ == '__main__':
    window = MainApp()
    window.show()
    app.exec()
