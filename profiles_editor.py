import PyQt6.QtCore as Qc
import PyQt6.QtGui as Qg
import PyQt6.QtWidgets as Qt
import sys
import traceback
from typing import List, Optional, Tuple, Union

# Qt parameters
FONT_SIZE: int = 13
MIN_HEIGHT: int = 400
MIN_WIDTH: int = 700
TITLE = "Edytor tabeli - "

# Table parameters
COLUMNS_NUMBER: int = 3
COLUMNS_HEADERS: List[str] = ["Parametr", "Jednostka", "Wartość"]
DEFAULT_TABLE: List[List[str]] = [
    ["Czy pacjent chodzi?", "(tak/nie)", ""],
    ["Częstość oddechu", "([1/min] / nieobecna)", ""],
    ["Tętno obwodowe", "([1/min] / nieobecne)", ""],
    ["Czy pacjent spełnia polecenia?", "(tak/nie)", ""],
    ["Kolor segregacji", "(nazwa koloru)", ""]
]
ROWS_NUMBER: int = len(DEFAULT_TABLE)

# Starting Qt
app = Qt.QApplication(sys.argv)
sys.excepthook = lambda *args: (traceback.print_exception(*args, file=sys.stdout))
app.setFont(Qg.QFont("Arial", FONT_SIZE))


class MainApp(Qt.QMainWindow):
    """
    The class corresponding to the main window of the app
    """
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

    # Other attributes
    current_file: str
    current_state_number: int
    next_state_number: int  # Not always current + 1 !!!
    # parent number, isTime, time in minutes/intervention
    current_state_parent: Optional[Tuple[int, bool, Union[int, str]]]
    is_saved: bool
    max_size: Qc.QSize

    def __init__(self):
        super(MainApp, self).__init__()
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.current_file = ""
        self.current_state_number = 1
        self.next_state_number = 2
        self.is_saved = False
        self.set_window_title()

        # The main window
        self.main_layout = Qt.QVBoxLayout()
        widget = Qt.QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Size
        self.max_size = self.screen().availableSize()
        self.move((self.max_size.width() - MIN_WIDTH) // 2, (self.max_size.height() - MIN_HEIGHT) // 2)

        # Adding to the layout
        self.layout()

        # Connecting signals
        self.add_row_button.clicked.connect(self.add_new_row)
        self.delete_selected_rows_button.clicked.connect(self.delete_selected_rows)
        self.save_current_table_button.clicked.connect(self.save_current_table)
        self.add_new_state_button.clicked.connect(self.add_new_state)
        self.new_patient_button.clicked.connect(self.create_new_table)
        self.open_existing_state_button.clicked.connect(self.open_table)

    def set_window_title(self):
        """Sets the title depending on whether it's an already saved file or a new one"""
        if self.current_file == "":
            self.setWindowTitle(TITLE + "nowy*")
        else:
            self.setWindowTitle(TITLE + self.current_file.split("/")[-1] + f" Stan {self.current_state_number}")

    def layout(self):
        """Adds all elements to the layout"""
        self.main_layout.addWidget(Qt.QLabel("Tabela", self))
        self.table = Qt.QTableWidget(ROWS_NUMBER, COLUMNS_NUMBER, self)
        self.table.setHorizontalHeaderLabels(COLUMNS_HEADERS)
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                self.table.setItem(i, j, Qt.QTableWidgetItem(DEFAULT_TABLE[i][j]))
        self.table.resizeColumnsToContents()
        self.main_layout.addWidget(self.table)

        self.main_layout.addWidget(Qt.QLabel("Opis", self))
        self.description = Qt.QTextEdit(self)
        self.main_layout.addWidget(self.description)

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

    def clear_table_contents(self):
        for i in range(self.table.rowCount()):
            self.table.setItem(i, 2, Qt.QTableWidgetItem(""))
        self.description.setText("")

    def add_new_row(self):
        self.table.insertRow(self.table.rowCount())

    def delete_selected_rows(self):
        rows_to_remove: List[int] = list({qmodelindex.row() for qmodelindex in self.table.selectedIndexes()})
        rows_to_remove.sort(reverse=True)
        for row in rows_to_remove:
            self.table.removeRow(row)

    def save_current_table(self):
        # If it is saved, don't save again
        if self.is_saved:
            Qt.QMessageBox(
                Qt.QMessageBox.Icon.Information, " ", "Stan już zapisany", Qt.QMessageBox.StandardButton.Ok, self
            ).exec()
            return

        # Choosing a file to save into
        if self.current_file == "":
            self.current_file, _ = Qt.QFileDialog.getSaveFileName(
                self, "Zapisz tabelę", "Profile pacjentów", "Pliki tekstowe (*.txt)"
            )
            if self.current_file == "":
                return

        # Saving to a string
        saved_contents: str = f"Stan {self.current_state_number}\n"
        saved_contents += f" ; {'; '.join(COLUMNS_HEADERS)}\n"
        for i in range(self.table.rowCount()):
            saved_contents += f"{i + 1}; "
            for j in range(self.table.columnCount()):
                saved_contents += f"{self.table.item(i, j).text()}; "
            saved_contents = saved_contents[:-2]
            saved_contents += "\n"
        saved_contents += f"Opis: {self.description.toPlainText()}\n"
        if self.current_state_number != 1:
            saved_contents += f"Rodzic: Stan {str(self.current_state_parent[0])}, przejście: "
            if self.current_state_parent[1]:  # Czas
                saved_contents += f"czas - {str(self.current_state_parent[2])}min\n"
            else:  # Interwencja
                saved_contents += f"interwencja - {self.current_state_parent[2]}\n"
        saved_contents += "\n"

        # Saving to a file
        with open(self.current_file, "a") as f:
            f.write(saved_contents)
        self.is_saved = True
        self.set_window_title()
        Qt.QMessageBox(
            Qt.QMessageBox.Icon.Information, " ", "Stan zapisany!", Qt.QMessageBox.StandardButton.Ok, self
        ).exec()

    def open_table(self):
        # Choose a file to open
        self.current_file, _ = Qt.QFileDialog.getOpenFileName(
            self, "Open the table", "", "Text files (*.txt)"
        )
        if self.current_file == "":  # Cancelled
            return

        # Opening the file
        with open(self.current_file, "r+") as f:
            states: List[str] = f.read().split("\n\n")
            states.remove("")
            # Divide each state into lines, get the first line, remove "Stan " and get the remaining number
            state_numbers: List[str] = [state.split("\n")[0][5:] for state in states]
            choice = Qt.QInputDialog(self)
            choice.setCancelButtonText("Anuluj")
            # Choosing one of the states to edit
            results = choice.getItem(self, "Wybór stanu", "Wybierz jeden ze stanów tego pacjenta",
                                     state_numbers)
            if not results[1]:  # Cancelled
                return
            self.next_state_number = max([int(number) for number in state_numbers]) + 1
            self.current_state_number = int(results[0])

            # Writing the remaining states back into the file
            for state in states:
                if state.startswith("Stan " + results[0]):
                    states.remove(state)
                    f.truncate(0)
                    f.seek(0)
                    states.append("")
                    f.write("\n\n".join(states))
                    lines: List[str] = state.split("\n")[2:]  # Remove 2 first lines
                    for i in range(self.table.rowCount()):
                        line: List[str] = lines[i].split("; ")[1:]
                        for j in range(self.table.columnCount()):
                            self.table.setItem(i, j, Qt.QTableWidgetItem(line[j]))
                    i += 1
                    description: str = ""
                    while i < len(lines) and not lines[i].startswith("Rodzic: "):
                        if lines[i].startswith("Opis: "):
                            lines[i] = lines[i][6:]  # Remove "Opis: "
                        else:  # It's not the line with "Opis"
                            description += "\n"
                        description += lines[i]
                        i += 1
                    self.description.setText(description)

                    # Third element of the last line is the parent state's number, only the first character
                    if i < len(lines):
                        parent_num: int = int(lines[i].split()[2][0])
                        is_transition_time: bool
                        if lines[i].split()[4] == "czas":
                            is_transition_time = True
                            intervention_or_time_duration: int = int(lines[i].split()[6][:-3])
                        else:  # Transition is the intervention
                            is_transition_time = False
                            intervention_or_time_duration: str = lines[i].split()[6]
                        self.current_state_parent = (parent_num, is_transition_time, intervention_or_time_duration)
                    self.set_window_title()
                    Qt.QMessageBox(
                        Qt.QMessageBox.Icon.Information, " ",
                        "Stan pacjenta otwarty.\nNależy go zapisać po wprowadzeniu zmian",
                        Qt.QMessageBox.StandardButton.Ok, self
                    ).exec()

    def add_new_state(self):
        """Add a new state to the currently saved profile"""
        # If not saved, must be saved first
        if not self.is_saved:
            Qt.QMessageBox(
                Qt.QMessageBox.Icon.Information, " ", "Nie zapisano stanu", Qt.QMessageBox.StandardButton.Ok, self
            ).exec()
            return

        # Choosing whether the transition is by time or intervention
        choice = Qt.QInputDialog(self)
        choice.setCancelButtonText("Anuluj")
        results = choice.getItem(self, "Wybór warunku", "Wybierz warunek przejścia między stanami",
                                 ["Czas", "Interwencja"])
        if not results[1]:  # Cancelled
            return
        if results[0] == "Czas":
            results = choice.getInt(self, "Czas",
                                    "Liczba minut, po której nastąpi przejście do kolejnego stanu:", min=0)
            if not results[1]:
                return
            self.current_state_parent = (self.current_state_number, True, results[0])
        else:  # Interwencja
            results = choice.getText(self, "Interwencja",
                                     "Interwencja, powodująca przejście do kolejnego stanu")
            if not results[1]:  # Cancelled
                return
            self.current_state_parent = (self.current_state_number, False, results[0])
        self.current_state_number = self.next_state_number
        self.next_state_number += 1
        self.clear_table_contents()
        self.is_saved = False
        self.set_window_title()

    def create_new_table(self):
        """A brand-new profile"""
        if not self.is_saved:  # If not saved yet, progress would be lost
            Qt.QMessageBox(
                Qt.QMessageBox.Icon.Information, " ", "Nie zapisano stanu", Qt.QMessageBox.StandardButton.Ok, self
            ).exec()
            return
        self.current_state_number = 1
        self.current_file = ""
        self.clear_table_contents()
        self.is_saved = False
        self.set_window_title()


if __name__ == '__main__':
    window = MainApp()
    window.show()
    app.exec()
