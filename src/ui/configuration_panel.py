"""Simulation Configuration Panel containing executable input, drag-and-drop, spinboxes, and run controls."""

from pathlib import Path
from typing import Optional, List
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QComboBox,
    QFileDialog,
    QMessageBox,
)

from src.models.simulation_config import SimulationConfig
from src.core.validator import Validator, ValidationResult
from src.core.command_builder import CommandBuilder
from src.ui.widgets import CardWidget, DropLineEdit, StatusBadge, CommandPreviewWidget
from src.utils.constants import (
    MIN_START_TIME,
    MAX_START_TIME,
    MIN_STOP_TIME,
    MAX_STOP_TIME,
)


class ConfigurationPanel(QWidget):
    """Top panel for configuring executable path, start time, stop time, command preview, and run button."""

    run_requested = pyqtSignal(SimulationConfig)
    cancel_requested = pyqtSignal()
    config_changed = pyqtSignal(SimulationConfig)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._is_running = False

        self._init_ui()
        self._connect_signals()
        self._revalidate()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 6)
        main_layout.setSpacing(10)

        # Main Card Widget
        self.card = CardWidget("Simulation Configuration")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(12)

        # 1. Executable Selection Row
        exe_grid = QGridLayout()
        exe_grid.setSpacing(8)

        exe_label = QLabel("Executable Path:")
        exe_label.setToolTip("Path to the compiled OpenModelica model executable file.")
        
        self.exe_line_edit = DropLineEdit()
        self.exe_line_edit.setReadOnly(True)  # Per specification: read-only textbox

        self.browse_btn = QPushButton(QIcon("resources/icons/folder.svg"), "Browse...")
        self.browse_btn.setToolTip("Browse filesystem for OpenModelica executable (Ctrl+O)")

        self.recent_combo = QComboBox()
        self.recent_combo.setToolTip("Select from recently loaded model executables")
        self.recent_combo.setPlaceholderText("Recent Files...")

        self.validation_badge = StatusBadge()

        exe_grid.addWidget(exe_label, 0, 0)
        exe_grid.addWidget(self.exe_line_edit, 0, 1)
        exe_grid.addWidget(self.browse_btn, 0, 2)
        exe_grid.addWidget(self.recent_combo, 1, 1)
        exe_grid.addWidget(self.validation_badge, 1, 2)

        # 2. Time Parameters Row (Spinboxes)
        time_layout = QHBoxLayout()
        time_layout.setSpacing(20)

        start_time_label = QLabel("Start Time (s):")
        start_time_label.setToolTip(f"Integer start time. Range: {MIN_START_TIME} .. {MAX_START_TIME}")

        self.start_spin = QSpinBox()
        self.start_spin.setRange(MIN_START_TIME, MAX_START_TIME)
        self.start_spin.setValue(0)
        self.start_spin.setToolTip("Simulation start time integer.")

        stop_time_label = QLabel("Stop Time (s):")
        stop_time_label.setToolTip(f"Integer stop time. Range: {MIN_STOP_TIME} .. {MAX_STOP_TIME}")

        self.stop_spin = QSpinBox()
        self.stop_spin.setRange(MIN_STOP_TIME, MAX_STOP_TIME)
        self.stop_spin.setValue(4)
        self.stop_spin.setToolTip("Simulation stop time integer.")

        time_layout.addWidget(start_time_label)
        time_layout.addWidget(self.start_spin)
        time_layout.addSpacing(15)
        time_layout.addWidget(stop_time_label)
        time_layout.addWidget(self.stop_spin)
        time_layout.addStretch()

        # 3. Validation Feedback Label
        self.feedback_label = QLabel("")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setStyleSheet("color: #8b949e; font-size: 12px;")

        # 4. Command Preview Box
        self.command_preview = CommandPreviewWidget()

        # 5. Run Button Row
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton(QIcon("resources/icons/play.svg"), "Run Simulation")
        self.run_btn.setObjectName("RunButton")
        self.run_btn.setFixedHeight(42)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.run_btn.setFont(font)
        self.run_btn.setToolTip("Execute simulation with configured runtime parameters (Ctrl+Enter)")

        btn_layout.addStretch()
        btn_layout.addWidget(self.run_btn, 2)
        btn_layout.addStretch()

        # Assemble into Card Layout
        content_layout.addLayout(exe_grid)
        content_layout.addLayout(time_layout)
        content_layout.addWidget(self.feedback_label)
        content_layout.addWidget(self.command_preview)
        content_layout.addLayout(btn_layout)

        self.card.set_content_layout(content_layout)
        main_layout.addWidget(self.card)

    def _connect_signals(self) -> None:
        self.browse_btn.clicked.connect(self.browse_executable)
        self.exe_line_edit.file_dropped.connect(self._on_executable_changed)
        self.recent_combo.activated.connect(self._on_recent_selected)
        
        self.start_spin.valueChanged.connect(self._revalidate)
        self.stop_spin.valueChanged.connect(self._revalidate)
        self.run_btn.clicked.connect(self._on_run_clicked)

    def set_recent_executables(self, recents: List[str]) -> None:
        """Populates the recent files combobox."""
        self.recent_combo.blockSignals(True)
        self.recent_combo.clear()
        self.recent_combo.addItem("Select Recent Executable...")
        for r in recents:
            self.recent_combo.addItem(r)
        self.recent_combo.blockSignals(False)

    def set_executable_path(self, path_str: str) -> None:
        """Programmatically sets the executable line edit."""
        self.exe_line_edit.setText(path_str)
        self._on_executable_changed(path_str)

    def set_times(self, start: int, stop: int) -> None:
        """Sets the start and stop time spinbox values."""
        self.start_spin.setValue(start)
        self.stop_spin.setValue(stop)
        self._revalidate()

    def browse_executable(self) -> None:
        """Opens native file dialog to select simulation executable."""
        file_filter = "Executable Files (*.exe *.bat *.cmd *.py *);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select OpenModelica Simulation Executable",
            "",
            file_filter,
        )
        if file_path:
            self.set_executable_path(file_path)

    def _on_recent_selected(self, index: int) -> None:
        if index > 0:
            selected_path = self.recent_combo.currentText()
            self.set_executable_path(selected_path)

    def _on_executable_changed(self, path_str: str) -> None:
        self._revalidate()

    def get_config(self) -> Optional[SimulationConfig]:
        """Builds current SimulationConfig instance."""
        exe_path = self.exe_line_edit.text().strip()
        if not exe_path:
            return None
        return SimulationConfig(
            executable_path=exe_path,
            start_time=self.start_spin.value(),
            stop_time=self.stop_spin.value(),
        )

    def _revalidate(self) -> None:
        """Executes real-time validation and updates UI indicators, preview, and run button state."""
        config = self.get_config()
        val_result = Validator.validate_config(config)

        # Update Badge
        self.validation_badge.set_badge(val_result.badge_state, val_result.badge_text)

        # Update Feedback Message & Run Button Status
        if val_result.is_valid:
            self.feedback_label.setText(val_result.message)
            self.feedback_label.setStyleSheet("color: #2ea44f; font-weight: bold;")
            self.run_btn.setEnabled(not self._is_running)
        elif val_result.badge_state == "neutral":
            self.feedback_label.setText(val_result.message)
            self.feedback_label.setStyleSheet("color: #8b949e; font-weight: normal;")
            self.run_btn.setEnabled(False)
        else:
            self.feedback_label.setText(f"⚠ {val_result.message}")
            self.feedback_label.setStyleSheet("color: #f85149; font-weight: bold;")
            self.run_btn.setEnabled(False)

        # Update Live Command Preview with relative preview string and absolute tooltip
        if config and config.executable_path.strip():
            relative_str = CommandBuilder.build_preview_string(config, relative=True)
            full_str = CommandBuilder.build_preview_string(config, relative=False)
            self.command_preview.set_command_text(relative_str, tooltip_path=full_str)
            self.config_changed.emit(config)
        else:
            self.command_preview.set_command_text("(Select executable to view command preview)", tooltip_path=None)

    def _on_run_clicked(self) -> None:
        if self._is_running:
            self.cancel_requested.emit()
            return

        config = self.get_config()
        if not config:
            return

        val_result = Validator.validate_config(config)
        if not val_result.is_valid:
            QMessageBox.warning(
                self,
                "Invalid Simulation Parameters",
                val_result.message,
            )
            return

        self.run_requested.emit(config)

    def set_running_state(self, running: bool) -> None:
        """Disables/enables input controls and changes button appearance during execution."""
        self._is_running = running

        # Disable input controls while executing
        self.exe_line_edit.setEnabled(not running)
        self.browse_btn.setEnabled(not running)
        self.recent_combo.setEnabled(not running)
        self.start_spin.setEnabled(not running)
        self.stop_spin.setEnabled(not running)

        if running:
            self.run_btn.setIcon(QIcon("resources/icons/stop.svg"))
            self.run_btn.setText("Cancel Simulation")
            self.run_btn.setObjectName("CancelButton")
            self.run_btn.setStyleSheet("background-color: #da3633; color: white;")
            self.run_btn.setEnabled(True)
        else:
            self.run_btn.setIcon(QIcon("resources/icons/play.svg"))
            self.run_btn.setText("Run Simulation")
            self.run_btn.setObjectName("RunButton")
            self.run_btn.setStyleSheet("")
            self._revalidate()

