"""Execution Service managing background QThread execution lifecycle."""

from typing import Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.models.simulation_config import SimulationConfig
from src.models.simulation_result import SimulationResult
from src.core.simulation_runner import SimulationRunner


class ExecutionService(QObject):
    """High-level service for triggering and controlling non-blocking simulation executions."""

    simulation_started = pyqtSignal()
    stdout_streamed = pyqtSignal(str)
    stderr_streamed = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    simulation_finished = pyqtSignal(SimulationResult)
    execution_failed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._thread: Optional[QThread] = None
        self._runner: Optional[SimulationRunner] = None

    @property
    def is_running(self) -> bool:
        """Returns True if a simulation thread is currently active."""
        return self._thread is not None and self._thread.isRunning()

    def run_simulation(self, config: SimulationConfig) -> bool:
        """Launches simulation execution in background QThread.

        Args:
            config: SimulationConfig instance.

        Returns:
            True if launch succeeded, False if already running.
        """
        if self.is_running:
            self.execution_failed.emit("A simulation is already in progress.")
            return False

        self._thread = QThread()
        self._runner = SimulationRunner(config)
        self._runner.moveToThread(self._thread)

        # Connect signals
        self._thread.started.connect(self._runner.run)
        self._runner.stdout_line_emitted.connect(self.stdout_streamed)
        self._runner.stderr_line_emitted.connect(self.stderr_streamed)
        self._runner.status_updated.connect(self.status_changed)
        self._runner.execution_finished.connect(self._on_finished)
        self._runner.execution_error.connect(self.execution_failed)

        # Thread cleanup
        self._runner.execution_finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()
        self.simulation_started.emit()
        return True

    def cancel_simulation(self) -> None:
        """Requests cancellation of active simulation worker."""
        if self._runner and self.is_running:
            self._runner.cancel()

    def _on_finished(self, result: SimulationResult) -> None:
        """Handles completion signal from runner and forwards to UI listeners."""
        self.simulation_finished.emit(result)
        self._cleanup()

    def _cleanup(self) -> None:
        """Resets thread and runner references."""
        self._runner = None
        self._thread = None
