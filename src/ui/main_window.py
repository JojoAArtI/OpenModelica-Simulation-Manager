"""Main application window for OpenModelica Simulation Manager."""

from pathlib import Path
from typing import Optional
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QShortcut, QKeySequence, QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QApplication,
)

from src.utils.constants import (
    APP_NAME,
    APP_VERSION,
    ORGANIZATION_NAME,
    ORGANIZATION_DOMAIN,
    THEME_DARK,
    THEME_LIGHT,
)
from src.utils.helpers import format_duration
from src.core.settings_manager import SettingsManager
from src.core.logger import LoggerService
from src.services.execution_service import ExecutionService
from src.services.storage_service import StorageService
from src.models.simulation_config import SimulationConfig
from src.models.simulation_result import SimulationResult
from src.ui.toolbar import MainToolBar
from src.ui.configuration_panel import ConfigurationPanel
from src.ui.console_panel import ConsolePanel
from src.ui.status_bar import StatusBarController


class HistoryDialog(QDialog):
    """Modal dialog displaying persistent simulation execution history records."""

    def __init__(self, storage_service: StorageService, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.storage_service = storage_service
        self.setWindowTitle("Simulation Execution History")
        self.resize(750, 400)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Executable", "Status", "Duration", "Command"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._load_history()

        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self._clear_history)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)

        layout.addWidget(self.table)
        layout.addLayout(btn_layout)

    def _load_history(self) -> None:
        results = self.storage_service.get_all_results()
        self.table.setRowCount(len(results))

        for row, res in enumerate(results):
            status_text = "✔ Success" if res.is_success else f"❌ Failed ({res.exit_code})"
            duration_str = format_duration(res.execution_time_seconds)

            self.table.setItem(row, 0, QTableWidgetItem(res.timestamp[:19].replace("T", " ")))
            self.table.setItem(row, 1, QTableWidgetItem(res.executable_name))
            self.table.setItem(row, 2, QTableWidgetItem(status_text))
            self.table.setItem(row, 3, QTableWidgetItem(duration_str))
            self.table.setItem(row, 4, QTableWidgetItem(res.command_executed))

    def _clear_history(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all simulation execution history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.storage_service.clear_history()
            self._load_history()


class MainWindow(QMainWindow):
    """Main window orchestrating Toolbar, ConfigurationPanel, ConsolePanel, and ExecutionService."""

    def __init__(self, logger_service: LoggerService) -> None:
        super().__init__()
        self.logger = logger_service
        self.settings_manager = SettingsManager()
        self.storage_service = StorageService(self.settings_manager)
        self.execution_service = ExecutionService()

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon("resources/icons/openmodelica.svg"))
        self.resize(1000, 750)

        self._init_ui()
        self._connect_signals()
        self._setup_shortcuts()
        self._load_settings()

        self.logger.info("OpenModelica Simulation Manager initialized successfully.")

    def _init_ui(self) -> None:
        # 1. Top Toolbar
        self.toolbar = MainToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # 2. Main Vertical Splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.config_panel = ConfigurationPanel(self)
        self.console_panel = ConsolePanel(self)

        self.splitter.addWidget(self.config_panel)
        self.splitter.addWidget(self.console_panel)
        self.splitter.setSizes([380, 370])
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        self.setCentralWidget(self.splitter)

        # 3. Status Bar Controller
        self.status_controller = StatusBarController(self.statusBar())

    def _connect_signals(self) -> None:
        # Toolbar signals
        self.toolbar.theme_toggle_clicked.connect(self._toggle_theme)
        self.toolbar.settings_clicked.connect(self._open_settings_dialog)
        self.toolbar.history_clicked.connect(self._open_history_dialog)
        self.toolbar.about_clicked.connect(self._open_about_dialog)

        # Config panel signals
        self.config_panel.run_requested.connect(self._start_simulation)
        self.config_panel.cancel_requested.connect(self._cancel_simulation)

        # Execution Service signals
        self.execution_service.simulation_started.connect(self._on_simulation_started)
        self.execution_service.stdout_streamed.connect(self.console_panel.append_stdout)
        self.execution_service.stderr_streamed.connect(self.console_panel.append_stderr)
        self.execution_service.status_changed.connect(self.console_panel.append_info)
        self.execution_service.simulation_finished.connect(self._on_simulation_finished)
        self.execution_service.execution_failed.connect(self._on_execution_failed)

        # Logger signal stream to console
        self.logger.log_emitted.connect(self.console_panel.append_info)

    def _setup_shortcuts(self) -> None:
        # Ctrl+O -> Browse executable
        self.shortcut_browse = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_browse.activated.connect(self.config_panel.browse_executable)

        # Ctrl+Return / Ctrl+Enter -> Run simulation
        self.shortcut_run_return = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut_run_return.activated.connect(self._on_shortcut_run)

        self.shortcut_run_enter = QShortcut(QKeySequence("Ctrl+Enter"), self)
        self.shortcut_run_enter.activated.connect(self._on_shortcut_run)

        # ESC -> Cancel simulation when running
        self.shortcut_esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.shortcut_esc.activated.connect(self._cancel_simulation)


    def _load_settings(self) -> None:
        # Window Geometry & Splitter state
        geom = self.settings_manager.load_window_geometry()
        if geom:
            self.restoreGeometry(geom)

        splitter_state = self.settings_manager.load_splitter_state()
        if splitter_state:
            self.splitter.restoreState(splitter_state)

        # Theme
        theme = self.settings_manager.get_theme()
        self._apply_theme(theme)

        # Recent files
        recents = self.settings_manager.get_recent_executables()
        self.config_panel.set_recent_executables(recents)

        # Last start/stop times
        last_start = self.settings_manager.get_last_start_time()
        last_stop = self.settings_manager.get_last_stop_time()
        self.config_panel.set_times(last_start, last_stop)

        # Auto-load latest recent executable if valid
        if recents:
            first_recent = recents[0]
            if Path(first_recent).exists():
                self.config_panel.set_executable_path(first_recent)

    def closeEvent(self, event) -> None:
        """Saves geometry and application state before closing."""
        if self.execution_service.is_running:
            reply = QMessageBox.question(
                self,
                "Simulation in Progress",
                "A simulation is currently running. Are you sure you want to stop it and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.execution_service.cancel_simulation()
            else:
                event.ignore()
                return

        self.settings_manager.save_window_geometry(self.saveGeometry())
        self.settings_manager.save_splitter_state(self.splitter.saveState())

        # Save last configured start/stop times
        config = self.config_panel.get_config()
        if config:
            self.settings_manager.set_last_start_time(config.start_time)
            self.settings_manager.set_last_stop_time(config.stop_time)

        event.accept()

    def _apply_theme(self, theme_name: str) -> None:
        style_file = "dark_theme.qss" if theme_name == THEME_DARK else "light_theme.qss"
        style_path = Path("resources/styles") / style_file

        if style_path.exists():
            qss_content = style_path.read_text(encoding="utf-8")
            QApplication.instance().setStyleSheet(qss_content)
            self.settings_manager.set_theme(theme_name)
        else:
            self.logger.warning(f"Stylesheet not found: {style_path}")

    def _toggle_theme(self) -> None:
        current_theme = self.settings_manager.get_theme()
        new_theme = THEME_LIGHT if current_theme == THEME_DARK else THEME_DARK
        self._apply_theme(new_theme)
        self.logger.info(f"Theme switched to: {new_theme.upper()}")

    def _on_shortcut_run(self) -> None:
        if not self.execution_service.is_running:
            self.config_panel._on_run_clicked()

    def _start_simulation(self, config: SimulationConfig) -> None:
        self.logger.info(f"Initiating simulation run for '{config.executable_name}'")
        self.settings_manager.add_recent_executable(config.executable_path)
        self.config_panel.set_recent_executables(self.settings_manager.get_recent_executables())

        self.execution_service.run_simulation(config)

    def _cancel_simulation(self) -> None:
        if self.execution_service.is_running:
            self.logger.warning("Cancellation requested by user.")
            self.execution_service.cancel_simulation()

    def _on_simulation_started(self) -> None:
        self.config_panel.set_running_state(True)
        self.status_controller.set_running()
        self.console_panel.append_info("=== SIMULATION STARTED ===\n")

    def _on_simulation_finished(self, result: SimulationResult) -> None:
        self.config_panel.set_running_state(False)
        self.storage_service.save_result(result)

        if result.is_success:
            self.status_controller.set_completed_success(result.execution_time_seconds)
            self.console_panel.append_info(
                f"\n=== SIMULATION COMPLETED SUCCESSFULLY (Duration: {format_duration(result.execution_time_seconds)}) ===\n"
            )
            self.logger.info(f"Simulation completed successfully in {format_duration(result.execution_time_seconds)}.")
        else:
            self.status_controller.set_execution_failed(result.execution_time_seconds, f"Failed (Exit Code {result.exit_code})")
            self.console_panel.append_stderr(
                f"\n=== SIMULATION EXECUTION FAILED (Exit Code: {result.exit_code}) ===\n"
            )
            self.logger.error(f"Simulation failed with exit code {result.exit_code}.")

    def _on_execution_failed(self, error_msg: str) -> None:
        self.config_panel.set_running_state(False)
        self.status_controller.set_execution_failed(0.0, "Execution Error")
        self.console_panel.append_stderr(f"[ERROR] {error_msg}\n")
        self.logger.error(f"Execution error: {error_msg}")

    def _open_history_dialog(self) -> None:
        dlg = HistoryDialog(self.storage_service, self)
        dlg.exec()

    def _open_settings_dialog(self) -> None:
        QMessageBox.information(
            self,
            "Settings",
            f"<b>OpenModelica Simulation Manager</b><br><br>"
            f"Preferences are automatically saved to QSettings.<br>"
            f"<b>Theme:</b> {self.settings_manager.get_theme().upper()}<br>"
            f"<b>Log Directory:</b> {Path('logs').resolve()}",
        )

    def _open_about_dialog(self) -> None:
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME} v{APP_VERSION}</h3>"
            f"<p>Professional Simulation Launcher GUI for OpenModelica Executables.</p>"
            f"<p>Developed for the <b>{ORGANIZATION_NAME}</b> Screening Assignment.</p>"
            f"<p>Website: <a href='https://{ORGANIZATION_DOMAIN}'>{ORGANIZATION_DOMAIN}</a></p>"
            f"<p><b>Features:</b><br>"
            f"- Non-blocking asynchronous execution<br>"
            f"- Drag and Drop executable loading<br>"
            f"- Live simulation time validation (0 &lt;= start &lt; stop &lt; 5)<br>"
            f"- Dark & Light engineering themes<br>"
            f"- Monospace streaming console log viewer</p>",
        )
