# -*- coding: utf-8 -*-
import sys
import traceback
from typing import List
import PyQt6.QtCore as Qc
import PyQt6.QtGui as Qg
import PyQt6.QtWidgets as Qt

from Skrypty import scenario_editor as sc_edit
from Skrypty import simulation as sim

# Parametry dla Qt
FONT_SIZE: int = 8
MIN_HEIGHT: int = 450
MIN_WIDTH: int = 550

# Inne stałe
DEAD_COUNT_TEXT: str = "Liczba zmarłych poszkodowanych"
AVERAGE_RPM_TEXT: str = "Średnia ocena RPM poszkodowanych"
TOTAL_SIM_TIME_TEXT: str = "Całkowity czas symulacji [min]"
AVERAGE_HELP_TIME_TEXT: str = "Średni czas pomocy poszkodowanemu [min]"

# Włączenie Qt
app = Qt.QApplication(sys.argv)
sys.excepthook = lambda *args: (traceback.print_exception(args[0], args[1], args[2], file=sys.stdout))
app.setFont(Qg.QFont("Arial", FONT_SIZE))


class MainApp(Qt.QMainWindow):
    """Klasa obejmująca główne okno aplikacji"""
    # Layout
    main_layout: Qt.QVBoxLayout
    scenario_layout: Qt.QVBoxLayout
    open_scenario_button: Qt.QPushButton
    dead_count_weight_spinbox: Qt.QDoubleSpinBox
    average_RPM_weight_spinbox: Qt.QDoubleSpinBox
    total_sim_time_weight_spinbox: Qt.QDoubleSpinBox
    average_help_time_weight_spinbox: Qt.QDoubleSpinBox
    simulate_button: Qt.QPushButton

    # Inne pola
    current_scenario: str

    def __init__(self):
        super(MainApp, self).__init__()
        self.setWindowTitle("Program do symulacji wypadku masowego")
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.MoveToMiddleOfScreen()
        self.ClearVariables()
        self.CreateAndConnectButtons()
        self.Layout()
        print("Program załadowany")

    def MoveToMiddleOfScreen(self):
        max_size: Qc.QSize = self.screen().availableSize()
        self.move((max_size.width() - MIN_WIDTH) // 2, (max_size.height() - MIN_HEIGHT) // 2)

    def ClearVariables(self):
        self.current_scenario = ""

    def CreateAndConnectButtons(self):
        self.open_scenario_button = Qt.QPushButton("Wybierz scenariusz")
        self.open_scenario_button.clicked.connect(self.OpenScenario)
        self.simulate_button = Qt.QPushButton("Wykonaj symulację")
        self.simulate_button.clicked.connect(self.Simulate)

    def OpenScenario(self):
        self.ClearVariables()
        self.current_scenario, _ = Qt.QFileDialog.getOpenFileName(
            self, "Otwórz scenariusz", "../Scenariusze", "Pliki tekstowe (*.txt)"
        )
        if self.current_scenario == "":  # Anulowano
            return
        self.ReloadScenario()

    def Simulate(self):
        simulation: sim.Simulation = sim.Simulation(self.current_scenario)
        simulation_results: sim.SimulationResults = simulation.PerformSimulation()
        results_window: Qt.QMessageBox = Qt.QMessageBox()
        results_window.setWindowTitle("Wyniki symulacji")
        weights = (
            self.dead_count_weight_spinbox.value(), self.average_RPM_weight_spinbox.value(),
            self.total_sim_time_weight_spinbox.value(), self.average_help_time_weight_spinbox.value()
        )
        message_lines: List[str] = [
            f"{DEAD_COUNT_TEXT}: {str(simulation_results.dead_victims_count)}, waga: {str(weights[0])}",
            f"{AVERAGE_RPM_TEXT}: {str(simulation_results.victims_average_RPM)}, waga: {str(weights[1])}",
            f"{TOTAL_SIM_TIME_TEXT}: {str(simulation_results.total_simulation_time_minutes)}, waga: {str(weights[2])}",
            f"{AVERAGE_HELP_TIME_TEXT}: {str(simulation_results.average_help_time_minutes)}, waga: {str(weights[3])}"
        ]
        objective_function_value: float = (
                simulation_results.dead_victims_count * weights[0] +
                simulation_results.victims_average_RPM * weights[1] +
                simulation_results.total_simulation_time_minutes * weights[2] +
                simulation_results.average_help_time_minutes * weights[3]
        )
        message_lines.append(f"Obliczona wartość funkcji celu: {objective_function_value:.2f}")
        results_window.setText("\n".join(message_lines))
        results_window.exec()

    def Layout(self):
        self.main_layout = Qt.QVBoxLayout()
        self.main_layout.addWidget(Qt.QLabel("Dane scenariusza"))
        scenario_area: Qt.QWidget = self.CreateScenarioScrollableArea()
        self.main_layout.addWidget(scenario_area)
        self.main_layout.addWidget(self.open_scenario_button)
        self.main_layout.addWidget(Qt.QLabel("Wagi funkcji celu"))
        weights_layout: Qt.QVBoxLayout = self.ObjectiveFunctionWeights()
        self.main_layout.addLayout(weights_layout)
        self.main_layout.addWidget(self.simulate_button)
        widget: Qt.QWidget = Qt.QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def CreateScenarioScrollableArea(self) -> Qt.QWidget:
        self.scenario_layout = Qt.QVBoxLayout()
        self.ReloadScenario()
        parent_widget: Qt.QWidget = Qt.QWidget()
        parent_widget.setLayout(self.scenario_layout)
        return parent_widget

    def ReloadScenario(self):
        sc_edit.ClearLayout(self.scenario_layout)
        self.simulate_button.setEnabled(False)
        scroll_widget = Qt.QScrollArea()
        if self.current_scenario:
            with open(self.current_scenario, "r", encoding="utf-8") as f:
                scenario_data_widget = Qt.QLabel(f.read())
            scroll_widget.setWidget(scenario_data_widget)
            self.simulate_button.setEnabled(True)
        self.scenario_layout.addWidget(scroll_widget)

    def ObjectiveFunctionWeights(self) -> Qt.QVBoxLayout:
        weights_layout: Qt.QVBoxLayout = Qt.QVBoxLayout()
        weights_layout_lower: Qt.QHBoxLayout = Qt.QHBoxLayout()
        weights_layout_upper: Qt.QHBoxLayout = Qt.QHBoxLayout()
        self.dead_count_weight_spinbox: Qt.QDoubleSpinBox = Qt.QDoubleSpinBox()
        self.AddWeightToLayout(
            weights_layout_lower, DEAD_COUNT_TEXT,
            self.dead_count_weight_spinbox, -1.0
        )
        self.average_RPM_weight_spinbox = Qt.QDoubleSpinBox()
        self.AddWeightToLayout(
            weights_layout_lower, AVERAGE_RPM_TEXT,
            self.average_RPM_weight_spinbox, 4.0
        )
        self.total_sim_time_weight_spinbox = Qt.QDoubleSpinBox()
        self.AddWeightToLayout(
            weights_layout_upper, TOTAL_SIM_TIME_TEXT,
            self.total_sim_time_weight_spinbox, -0.25
        )
        self.average_help_time_weight_spinbox = Qt.QDoubleSpinBox()
        self.AddWeightToLayout(
            weights_layout_upper, AVERAGE_HELP_TIME_TEXT,
            self.average_help_time_weight_spinbox, -0.3
        )
        weights_layout.addLayout(weights_layout_lower)
        weights_layout.addLayout(weights_layout_upper)
        return weights_layout

    @staticmethod
    def AddWeightToLayout(
            layout: Qt.QHBoxLayout, weight_label: str, weight_spinbox: Qt.QDoubleSpinBox, default_value: float
    ):
        layout.addWidget(Qt.QLabel(weight_label + ":"))
        weight_spinbox.setRange(-10.0, 10.0)
        weight_spinbox.setValue(default_value)
        layout.addWidget(weight_spinbox)


if __name__ == '__main__':
    window = MainApp()
    window.show()
    app.exec()
