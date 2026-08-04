"""Interactive simulation result plotting panel embedded in PyQt6 using Matplotlib."""

import re
import csv
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QMessageBox,
)

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.ui.widgets import CardWidget
from src.utils.constants import COLOR_INFO, COLOR_SUCCESS, COLOR_WARNING, THEME_DARK


def parse_simulation_output(stdout_text: str) -> Dict[str, List[float]]:
    """Parses simulation stdout stream to extract time-series data.

    Matches lines e.g.:
    "Time:  0.00s | Step: 00 | Tank1_Height: 2.500 m | Tank2_Height: 1.000 m"

    Args:
        stdout_text: Accumulated stdout text from simulation run.

    Returns:
        Dict mapping variable names to lists of float values e.g.
        {'Time': [...], 'Tank1_Height': [...], 'Tank2_Height': [...]}
    """
    data: Dict[str, List[float]] = {
        "Time": [],
        "Tank1_Height": [],
        "Tank2_Height": [],
    }

    pattern = re.compile(
        r"Time:\s*([\d\.]+)\s*s?\s*\|\s*Step:\s*\d+\s*\|\s*Tank1_Height:\s*([\d\.]+)\s*m?\s*\|\s*Tank2_Height:\s*([\d\.]+)\s*m?"
    )

    for line in stdout_text.splitlines():
        match = pattern.search(line)
        if match:
            try:
                t = float(match.group(1))
                h1 = float(match.group(2))
                h2 = float(match.group(3))
                data["Time"].append(t)
                data["Tank1_Height"].append(h1)
                data["Tank2_Height"].append(h2)
            except ValueError:
                continue

    return data


class ResultsPanel(QWidget):
    """Interactive tab view displaying simulation time-series plots and export actions."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_data: Dict[str, List[float]] = {}
        self._theme = THEME_DARK

        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 6, 12, 12)
        main_layout.setSpacing(8)

        self.card = CardWidget("Simulation Results & Analysis Plotter")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)

        # Toolbar controls (Variable selector, Export PNG, Export CSV)
        toolbar_layout = QHBoxLayout()

        var_label = QLabel("Plot Variables:")
        self.var_combo = QComboBox()
        self.var_combo.addItems(["All Variables", "Tank 1 Height (m)", "Tank 2 Height (m)"])
        self.var_combo.currentIndexChanged.connect(self._replot)

        self.export_png_btn = QPushButton("Export Plot (PNG)...")
        self.export_png_btn.setToolTip("Save chart as high-resolution PNG image")
        self.export_png_btn.clicked.connect(self.export_png)

        self.export_csv_btn = QPushButton("Export Data (CSV)...")
        self.export_csv_btn.setToolTip("Export parsed simulation time-series to CSV file")
        self.export_csv_btn.clicked.connect(self.export_csv)

        toolbar_layout.addWidget(var_label)
        toolbar_layout.addWidget(self.var_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.export_png_btn)
        toolbar_layout.addWidget(self.export_csv_btn)

        # Matplotlib Figure & Canvas Widget
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setObjectName("PlotCanvas")

        content_layout.addLayout(toolbar_layout)
        content_layout.addWidget(self.canvas)

        self.card.set_content_layout(content_layout)
        main_layout.addWidget(self.card)

        # Initial Empty Plot State
        self.clear_plot()

    def set_theme(self, theme_name: str) -> None:
        """Updates plot color scheme to match dark/light application theme."""
        self._theme = theme_name
        self._replot()

    def load_stdout_data(self, stdout_text: str) -> None:
        """Parses stdout log text and updates plot canvas."""
        parsed = parse_simulation_output(stdout_text)
        if parsed and parsed["Time"]:
            self._current_data = parsed
            self._replot()

    def clear_plot(self) -> None:
        """Clears plot and displays placeholder message."""
        self._current_data = {}
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        bg_color = "#0d1117" if self._theme == THEME_DARK else "#ffffff"
        text_color = "#8b949e" if self._theme == THEME_DARK else "#57606a"

        ax.set_facecolor(bg_color)
        self.figure.patch.set_facecolor(bg_color)
        ax.text(
            0.5,
            0.5,
            "Run simulation to view interactive output plots",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            color=text_color,
            fontsize=12,
            fontweight="bold",
        )
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()

    def _replot(self) -> None:
        """Redraws plot lines based on current data and selected variable filter."""
        if not self._current_data or not self._current_data.get("Time"):
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Theme Colors
        is_dark = self._theme == THEME_DARK
        bg_color = "#0d1117" if is_dark else "#ffffff"
        text_color = "#c9d1d9" if is_dark else "#24292f"
        grid_color = "#21262d" if is_dark else "#e1e4e8"

        ax.set_facecolor(bg_color)
        self.figure.patch.set_facecolor(bg_color)

        times = self._current_data["Time"]
        selected_var = self.var_combo.currentText()

        # Plot lines
        if selected_var in ("All Variables", "Tank 1 Height (m)"):
            ax.plot(
                times,
                self._current_data["Tank1_Height"],
                label="Tank 1 Height (m)",
                color="#58a6ff",
                linewidth=2.2,
                marker="o",
                markersize=4,
            )

        if selected_var in ("All Variables", "Tank 2 Height (m)"):
            ax.plot(
                times,
                self._current_data["Tank2_Height"],
                label="Tank 2 Height (m)",
                color="#2ea44f",
                linewidth=2.2,
                marker="s",
                markersize=4,
            )

        # Styling
        ax.set_title("OpenModelica TwoConnectedTanks Simulation Output", color=text_color, fontsize=11, fontweight="bold")
        ax.set_xlabel("Time (s)", color=text_color, fontsize=10)
        ax.set_ylabel("Fluid Level (m)", color=text_color, fontsize=10)

        ax.tick_params(colors=text_color, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(grid_color)

        ax.grid(True, linestyle="--", alpha=0.5, color=grid_color)
        legend = ax.legend(facecolor=bg_color, edgecolor=grid_color)
        for text in legend.get_texts():
            text.set_color(text_color)

        self.figure.tight_layout()
        self.canvas.draw()

    def export_png(self) -> None:
        """Saves current plot to a PNG image file."""
        if not self._current_data:
            QMessageBox.information(self, "No Data", "No simulation result data available to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Plot Image",
            "simulation_results.png",
            "PNG Images (*.png);;All Files (*)",
        )
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches="tight")
                QMessageBox.information(self, "Export Success", f"Plot image saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save plot image: {e}")

    def export_csv(self) -> None:
        """Exports time-series data to a CSV spreadsheet."""
        if not self._current_data or not self._current_data.get("Time"):
            QMessageBox.information(self, "No Data", "No simulation result data available to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results CSV",
            "simulation_results.csv",
            "CSV Files (*.csv);;All Files (*)",
        )
        if file_path:
            try:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Time (s)", "Tank1_Height (m)", "Tank2_Height (m)"])
                    times = self._current_data["Time"]
                    t1 = self._current_data["Tank1_Height"]
                    t2 = self._current_data["Tank2_Height"]
                    for i in range(len(times)):
                        writer.writerow([times[i], t1[i], t2[i]])
                QMessageBox.information(self, "Export Success", f"CSV data exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export CSV: {e}")
