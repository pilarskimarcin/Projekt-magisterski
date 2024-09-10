import PyQt6.QtCore as Qc
import PyQt6.QtGui as Qg
import PyQt6.QtWidgets as Qt
import sys
import traceback
from typing import List, Optional, TextIO

# Parametry Qt
FONT_SIZE: int = 13
MIN_HEIGHT: int = 600
MIN_WIDTH: int = 700
TITLE = "Edytor tabeli - "

# Parametry tabeli
COLUMNS_NUMBER: int = 3
COLUMNS_HEADERS: List[str] = ["Parametr", "Jednostka", "Wartość"]
DEFAULT_TABLE: List[List[str]] = [
    ["Czy pacjent chodzi?", "(tak/nie)", ""],
    ["Częstość oddechu", "([1/min] / nieobecna)", ""],
    ["Tętno obwodowe", "([1/min] / nieobecne)", ""],
    ["Czy pacjent spełnia polecenia?", "(tak/nie)", ""],
    ["Kolor segregacji", "(nazwa koloru)", ""],
    ["Jednostka chorobowa", "(identyfikator/y)", ""]
]
ROWS_NUMBER: int = len(DEFAULT_TABLE)

# Inne stałe
N_FIRST_COLUMNS_TO_OMIT: int = 1
N_FIRST_LINES_TO_OMIT: int = 2
DESCRIPTION_START: str = "Opis: "
PARENT_START_STRING: str = "Rodzic: "
PROFILES_DIRECTORY: str = "Profile pacjentów"
STATE_TITLE: str = "Stan "
TIME_UNIT: str = "min"

# Włączenie Qt
app = Qt.QApplication(sys.argv)
sys.excepthook = lambda *args: (traceback.print_exception(*args, file=sys.stdout))
app.setFont(Qg.QFont("Arial", FONT_SIZE))


class MainApp(Qt.QMainWindow):
    """Klasa odpowiadająca głównej aplikacji"""
    # Layout
    main_layout: Qt.QVBoxLayout
    table: Qt.QTableWidget
    description: Qt.QTextEdit
    add_row_button: Qt.QPushButton
    delete_selected_rows_button: Qt.QPushButton
    save_current_table_button: Qt.QPushButton
    add_new_state_button: Qt.QPushButton
    new_patient_button: Qt.QPushButton
    open_existing_state_button: Qt.QPushButton

    # Inne pola
    current_file: str
    current_state_number: int
    next_state_number: int  # Not always current + 1
    current_state_parent_number: Optional[int]
    current_state_parent_transition_intervention: Optional[str]
    current_state_parent_transition_time: Optional[int]
    is_saved: bool
    max_size: Qc.QSize

    def __init__(self):
        super(MainApp, self).__init__()
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.SetupVariables()
        self.SetWindowTitle()
        self.MoveToMiddleOfScreen()
        self.Layout()
        self.ConnectMainSignals()

    def SetupVariables(self):
        self.current_file = ""
        self.current_state_number = 1
        self.next_state_number = 2
        self.current_state_parent_number = None
        self.current_state_parent_transition_time = self.current_state_parent_transition_intervention = None
        self.is_saved = False

    def SetWindowTitle(self):
        if self.current_file == "":
            self.setWindowTitle(TITLE + "nowy*")
        else:
            self.setWindowTitle(TITLE + self.current_file.split("/")[-1] + f" {STATE_TITLE}{self.current_state_number}")

    def MoveToMiddleOfScreen(self):
        self.max_size = self.screen().availableSize()
        self.move((self.max_size.width() - MIN_WIDTH) // 2, (self.max_size.height() - MIN_HEIGHT) // 2)

    def Layout(self):
        self.CreateMainLayout()
        self.CreateTableWithDefaultValues()
        self.CreateDescription()
        self.CreateButtons()

    def CreateMainLayout(self):
        self.main_layout = Qt.QVBoxLayout()
        widget = Qt.QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def CreateTableWithDefaultValues(self):
        self.main_layout.addWidget(Qt.QLabel("Tabela", self))
        self.table = Qt.QTableWidget(ROWS_NUMBER, COLUMNS_NUMBER, self)
        self.table.setHorizontalHeaderLabels(COLUMNS_HEADERS)
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                self.table.setItem(i, j, Qt.QTableWidgetItem(DEFAULT_TABLE[i][j]))
        self.table.resizeColumnsToContents()
        self.main_layout.addWidget(self.table)

    def CreateDescription(self):
        self.main_layout.addWidget(Qt.QLabel("Opis", self))
        self.description = Qt.QTextEdit(self)
        self.main_layout.addWidget(self.description)

    def CreateButtons(self):
        self.add_row_button = Qt.QPushButton("Dodaj wiersz")
        self.delete_selected_rows_button = Qt.QPushButton("Usuń zaznaczone wiersze")
        self.save_current_table_button = Qt.QPushButton("Zapisz")
        buttons: Qt.QHBoxLayout = Qt.QHBoxLayout()
        buttons.addWidget(self.add_row_button, 1)
        buttons.addWidget(self.delete_selected_rows_button, 2)
        buttons.addWidget(self.save_current_table_button, 1)
        self.main_layout.addLayout(buttons)

        self.add_new_state_button = Qt.QPushButton("Nowy stan pacjenta")
        self.new_patient_button = Qt.QPushButton("Nowy pacjent")
        self.open_existing_state_button = Qt.QPushButton("Otwórz istniejący stan")
        buttons: Qt.QHBoxLayout = Qt.QHBoxLayout()
        buttons.addWidget(self.add_new_state_button, 2)
        buttons.addWidget(self.new_patient_button, 1)
        buttons.addWidget(self.open_existing_state_button, 2)
        self.main_layout.addLayout(buttons)

    def ConnectMainSignals(self):
        self.add_row_button.clicked.connect(self.AddNewRow)
        self.delete_selected_rows_button.clicked.connect(self.DeleteSelectedRows)
        self.save_current_table_button.clicked.connect(self.SaveCurrentState)
        self.add_new_state_button.clicked.connect(self.AddNewStateToCurrentProfile)
        self.new_patient_button.clicked.connect(self.CreateNewProfile)
        self.open_existing_state_button.clicked.connect(self.OpenExistingProfile)

    def AddNewRow(self):
        self.table.insertRow(self.table.rowCount())

    def DeleteSelectedRows(self):
        rows_to_remove: List[int] = list({qmodelindex.row() for qmodelindex in self.table.selectedIndexes()})
        rows_to_remove.sort(reverse=True)
        for row in rows_to_remove:
            self.table.removeRow(row)

    def SaveCurrentState(self):
        if self.is_saved:
            self.MessageBoxInformation("Stan już zapisany")
            return
        self.SaveFileChoice()
        if self.current_file == "":
            return
        saved_contents: str = f"{STATE_TITLE}{self.current_state_number}\n"
        saved_contents += self.GetDataFromTable()
        saved_contents += f"{DESCRIPTION_START}{self.description.toPlainText()}\n"
        if self.current_state_number != 1:
            saved_contents += self.GetDataFromParent()
        saved_contents += "\n"
        self.SaveContentsIntoFile(saved_contents)
        self.MessageBoxInformation("Stan zapisany prawidłowo")
        self.SetWindowTitle()

    def MessageBoxInformation(self, text: str):
        Qt.QMessageBox(
            Qt.QMessageBox.Icon.Information, " ", text, Qt.QMessageBox.StandardButton.Ok, self
        ).exec()

    def SaveFileChoice(self):
        if self.current_file == "":
            self.current_file, _ = Qt.QFileDialog.getSaveFileName(
                self, "Zapisz tabelę", PROFILES_DIRECTORY, "Pliki tekstowe (*.txt)"
            )

    def GetDataFromTable(self) -> str:
        saved_contents: str = f" ; {'; '.join(COLUMNS_HEADERS)}\n"
        for i in range(self.table.rowCount()):
            saved_contents += f"{i + 1}; "
            for j in range(self.table.columnCount()):
                saved_contents += f"{self.table.item(i, j).text()}; "
            saved_contents = saved_contents[:-2]
            saved_contents += "\n"
        return saved_contents

    def GetDataFromParent(self) -> str:
        saved_contents: str = f"{PARENT_START_STRING}{STATE_TITLE}{str(self.current_state_parent_number)}, przejście: "
        if self.current_state_parent_transition_time:
            saved_contents += f"czas - {str(self.current_state_parent_transition_time)}min\n"
        else:  # Interwencja
            saved_contents += f"interwencja - {self.current_state_parent_transition_intervention[2]}\n"
        return saved_contents

    def SaveContentsIntoFile(self, saved_contents: str):
        with open(self.current_file, "a") as f:
            f.write(saved_contents)
        self.is_saved = True

    def AddNewStateToCurrentProfile(self):
        if not self.is_saved:
            self.MessageBoxInformation("Nie zapisano stanu")
            return
        self.GetTransitionTypeAndDetails()
        self.current_state_number = self.next_state_number
        self.next_state_number += 1
        self.ClearTableContents()
        self.SetWindowTitle()

    def GetTransitionTypeAndDetails(self):
        choice_dialog: Qt.QInputDialog = self.CreateInputDialog()
        transition_type: Optional[str] = self.ChooseTransitionType(choice_dialog)
        if not transition_type:  # Anulowano
            return
        choice_finished_successfully: bool
        if transition_type == "Czas":
            choice_finished_successfully = self.ChooseTransitionTime(choice_dialog)
            if not choice_finished_successfully:
                return
        else:  # Interwencja
            choice_finished_successfully = self.ChooseTransitionIntervention(choice_dialog)
            if not choice_finished_successfully:
                return
        self.current_state_parent_number = self.current_state_number

    def CreateInputDialog(self) -> Qt.QInputDialog:
        choice = Qt.QInputDialog(self)
        choice.setCancelButtonText("Anuluj")
        return choice

    def ChooseTransitionType(self, choice_dialog: Qt.QInputDialog) -> Optional[str]:
        chosen_item, ok = choice_dialog.getItem(
            self, "Wybór warunku", "Wybierz warunek przejścia między stanami", ["Czas", "Interwencja"]
        )
        if not ok:
            return None
        return chosen_item

    def ChooseTransitionTime(self, choice_dialog: Qt.QInputDialog) -> bool:
        transition_time, ok = choice_dialog.getInt(
            self, "Czas", "Liczba minut, po której nastąpi przejście do kolejnego stanu:", min=0
        )
        if not ok:
            return False
        self.current_state_parent_transition_time = transition_time
        return True

    def ChooseTransitionIntervention(self, choice_dialog: Qt.QInputDialog) -> bool:
        transition_intervention, ok = choice_dialog.getText(
            self, "Interwencja", "Interwencja, powodująca przejście do kolejnego stanu"
        )
        if not ok:
            return False
        self.current_state_parent_transition_intervention = transition_intervention
        return True

    def ClearTableContents(self):
        for i in range(self.table.rowCount()):
            self.table.setItem(i, 2, Qt.QTableWidgetItem(""))
        self.description.setText("")
        self.is_saved = False

    def CreateNewProfile(self):
        if not self.is_saved:  # Bez zapisu stanu, utraciłby się postęp
            self.MessageBoxInformation("Nie zapisano stanu")
            return
        self.current_state_number = 1
        self.next_state_number = self.current_state_number + 1
        self.current_file = ""
        self.ClearTableContents()
        self.SetWindowTitle()

    def OpenExistingProfile(self):
        self.current_file = self.OpenFileChoice()
        if self.current_file == "":  # Anulowano
            return
        chosen_state: Optional[str] = self.ChooseStateFromOpenedProfile()
        if not chosen_state:
            return
        self.ParseChosenStateIntoCurrentState(chosen_state)
        self.SetWindowTitle()
        self.MessageBoxInformation("Stan pacjenta otwarty.\nNależy go zapisać po wprowadzeniu zmian")

    def OpenFileChoice(self) -> str:
        filename, _ = Qt.QFileDialog.getOpenFileName(
            self, "Open the table", PROFILES_DIRECTORY, "Text files (*.txt)"
        )
        return filename

    def ChooseStateFromOpenedProfile(self) -> Optional[str]:
        with open(self.current_file, "r+") as profile_file:
            states: List[str] = self.GetStatesFromProfileFile(profile_file)
            state_numbers: List[str] = self.GetNumbersOfStates(states)
            chosen_state_number: Optional[int] = self.ChooseStateNumber(state_numbers)
            if not chosen_state_number:  # Anulowano
                return None
            self.next_state_number = self.GetNextStateNumber(state_numbers)
            self.current_state_number = chosen_state_number
            for state in states:
                if not self.IsStateChosen(state, chosen_state_number):
                    continue
                states.remove(state)
                self.WriteRemainingStatesToFile(states, profile_file)
                return state

    @staticmethod
    def GetStatesFromProfileFile(profile_file: TextIO) -> List[str]:
        states: List[str] = profile_file.read().split("\n\n")
        states.remove("")
        return states

    @staticmethod
    def GetNumbersOfStates(states: List[str]) -> List[str]:
        states_numbers: List[str] = []
        for state in states:
            state_title_line: str = state.split("\n")[0]
            state_number: str = state_title_line[len(STATE_TITLE):]
            states_numbers.append(state_number)
        return states_numbers

    def ChooseStateNumber(self, states_numbers: List[str]) -> Optional[int]:
        choice: Qt.QInputDialog = self.CreateInputDialog()
        chosen_number, ok = choice.getItem(
            self, "Wybór stanu", "Wybierz jeden ze stanów tego pacjenta", states_numbers
        )
        if not ok:
            return None
        else:
            return int(chosen_number)

    @staticmethod
    def GetNextStateNumber(states_numbers: List[str]) -> int:
        return max([int(number) for number in states_numbers]) + 1

    @staticmethod
    def IsStateChosen(state: str, chosen_state_number: int) -> bool:
        return state.startswith(STATE_TITLE + str(chosen_state_number))

    @staticmethod
    def WriteRemainingStatesToFile(states: List[str], profile_file: TextIO):
        profile_file.truncate(0)
        profile_file.seek(0)
        states.append("")
        profile_file.write("\n\n".join(states))

    def ParseChosenStateIntoCurrentState(self, chosen_state: str):
        lines: List[str] = chosen_state.split("\n")[N_FIRST_LINES_TO_OMIT:]
        line_index = self.PutDataIntoTable(lines)
        line_index = self.PutDataIntoDescription(lines, line_index)
        self.ParseDataIntoParent(lines, line_index)

    def PutDataIntoTable(self, lines: List[str]) -> int:
        line_index: int = 0
        for line_index in range(self.table.rowCount()):
            line: List[str] = lines[line_index].split("; ")[N_FIRST_COLUMNS_TO_OMIT:]
            for column_index in range(self.table.columnCount()):
                self.table.setItem(line_index, column_index, Qt.QTableWidgetItem(line[column_index]))
        return line_index + 1

    def PutDataIntoDescription(self, lines: List[str], line_index: int) -> int:
        description: str = ""
        while line_index < len(lines) and not lines[line_index].startswith(PARENT_START_STRING):
            line: str = lines[line_index]
            if line.startswith(DESCRIPTION_START):
                line = line[len(DESCRIPTION_START):]
            else:  # Cały kolejny wiersz to dalej opis
                description += "\n"
            description += line
            line_index += 1
        self.description.setText(description)
        return line_index

    def ParseDataIntoParent(self, lines: List[str], line_index: int):
        if line_index < len(lines):
            last_line: str = lines[line_index]
            parent_state, transition = last_line.split(", ")
            _, _, parent_state_number = parent_state.split()
            _, transition_type, _, transition_condition = transition.split()
            if transition_type == "czas":
                self.current_state_parent_transition_time = int(transition_condition[:-len(TIME_UNIT)])
            else:  # interwencja
                self.current_state_parent_transition_intervention = transition_condition
            self.current_state_parent_number = int(parent_state_number)


if __name__ == '__main__':
    window = MainApp()
    window.show()
    app.exec()
