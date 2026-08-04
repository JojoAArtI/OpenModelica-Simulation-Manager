"""Status bar controller managing status text, execution duration, and indicators."""

from typing import Optional
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout

from src.utils.helpers import format_duration
from src.utils.constants import COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, COLOR_INFO


class StatusBarController:
    """Manages main window status bar states and live elapsed execution timer."""

    def __init__(self, status_bar: QStatusBar) -> None:
        self.status_bar = status_bar
        self._timer = QTimer()
        self._start_time_stamp = 0.0

        self._init_ui()
        self._timer.timeout.connect(self._update_live_duration)

    def _init_ui(self) -> None:
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; padding-left: 5px;")

        self.duration_label = QLabel("")
        self.duration_label.setStyleSheet("color: #8b949e; padding-right: 15px;")

        self.info_label = QLabel("OpenModelica Simulation Engine")
        self.info_label.setStyleSheet("color: #8b949e; font-size: 11px;")

        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.duration_label)
        self.status_bar.addPermanentWidget(self.info_label)

    def set_ready(self) -> None:
        """Sets status bar to Ready state."""
        self._timer.stop()
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet(f"color: {COLOR_INFO}; font-weight: bold;")
        self.duration_label.setText("")

    def set_running(self) -> None:
        """Sets status bar to Running... state and starts live duration timer."""
        import time
        self._start_time_stamp = time.perf_counter()
        self.status_label.setText("⚡ Running simulation...")
        self.status_label.setStyleSheet(f"color: {COLOR_WARNING}; font-weight: bold;")
        self.duration_label.setText("Duration: 0.00s")
        self._timer.start(100)  # Update every 100ms

    def set_completed_success(self, duration_sec: float) -> None:
        """Sets status bar to Completed Successfully state."""
        self._timer.stop()
        formatted = format_duration(duration_sec)
        self.status_label.setText("✔ Completed Successfully")
        self.status_label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: bold;")
        self.duration_label.setText(f"Duration: {formatted}")

    def set_execution_failed(self, duration_sec: float, message: str = "Execution Failed") -> None:
        """Sets status bar to Execution Failed state."""
        self._timer.stop()
        formatted = format_duration(duration_sec)
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: bold;")
        self.duration_label.setText(f"Duration: {formatted}")

    def _update_live_duration(self) -> None:
        import time
        elapsed = time.perf_counter() - self._start_time_stamp
        self.duration_label.setText(f"Duration: {format_duration(elapsed)}")
