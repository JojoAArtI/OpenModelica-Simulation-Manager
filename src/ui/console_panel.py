"""Execution Console Panel for live streaming stdout, stderr, and application logs."""

from pathlib import Path
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QApplication,
)

from src.ui.widgets import CardWidget
from src.utils.constants import COLOR_SUCCESS, COLOR_ERROR, COLOR_INFO


class ConsolePanel(QWidget):
    """Bottom panel containing dark-themed monospace log console for live simulation output."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._auto_scroll = True

        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 6, 12, 12)
        main_layout.setSpacing(8)

        self.card = CardWidget("Execution Console")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)

        # Control Toolbar (Auto-scroll, Clear, Copy, Save)
        toolbar_layout = QHBoxLayout()

        self.autoscroll_checkbox = QCheckBox("Auto-scroll")
        self.autoscroll_checkbox.setChecked(True)
        self.autoscroll_checkbox.toggled.connect(self._on_autoscroll_toggled)

        self.clear_btn = QPushButton("Clear Console")
        self.clear_btn.setToolTip("Clear all console text")
        self.clear_btn.clicked.connect(self.clear_console)

        self.copy_btn = QPushButton("Copy All")
        self.copy_btn.setToolTip("Copy console contents to clipboard")
        self.copy_btn.clicked.connect(self._copy_all)

        self.save_btn = QPushButton("Save Log...")
        self.save_btn.setToolTip("Save console output to text log file")
        self.save_btn.clicked.connect(self._save_log)

        toolbar_layout.addWidget(self.autoscroll_checkbox)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.clear_btn)
        toolbar_layout.addWidget(self.copy_btn)
        toolbar_layout.addWidget(self.save_btn)

        # Monospace Text Edit
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setObjectName("ConsoleOutput")

        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.text_edit.setFont(font)

        content_layout.addLayout(toolbar_layout)
        content_layout.addWidget(self.text_edit)

        self.card.set_content_layout(content_layout)
        main_layout.addWidget(self.card)

    def append_stdout(self, text: str) -> None:
        """Appends stdout text line with standard terminal coloring."""
        self._append_formatted_text(text, "#c9d1d9")

    def append_stderr(self, text: str) -> None:
        """Appends stderr text line with error red terminal coloring."""
        self._append_formatted_text(text, COLOR_ERROR)

    def append_info(self, text: str) -> None:
        """Appends informational system log text with info cyan terminal coloring."""
        self._append_formatted_text(text, COLOR_INFO)

    def _append_formatted_text(self, text: str, color_hex: str) -> None:
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Escape HTML chars for safe formatting
        safe_text = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
            .replace(" ", "&nbsp;")
        )
        
        html_snippet = f'<span style="color: {color_hex};">{safe_text}</span>'
        cursor.insertHtml(html_snippet)

        if self._auto_scroll:
            self.text_edit.setTextCursor(cursor)
            self.text_edit.ensureCursorVisible()

    def clear_console(self) -> None:
        """Clears text edit output."""
        self.text_edit.clear()

    def _on_autoscroll_toggled(self, checked: bool) -> None:
        self._auto_scroll = checked

    def _copy_all(self) -> None:
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.text_edit.toPlainText())
            self.copy_btn.setText("Copied!")
            QApplication.processEvents()
            self.copy_btn.setText("Copy All")

    def _save_log(self) -> None:
        text = self.text_edit.toPlainText()
        if not text:
            QMessageBox.information(self, "Empty Console", "Console log is empty.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Execution Log",
            "simulation_execution.log",
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)",
        )
        if file_path:
            try:
                Path(file_path).write_text(text, encoding="utf-8")
                QMessageBox.information(
                    self,
                    "Log Saved",
                    f"Execution log saved to:\n{file_path}",
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Could not save log file: {e}",
                )
