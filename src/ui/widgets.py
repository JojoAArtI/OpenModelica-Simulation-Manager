"""Reusable custom PyQt6 widgets for OpenModelica Simulation Manager UI."""

from pathlib import Path
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QColor
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QTextEdit,
    QPushButton,
    QApplication,
)

from src.utils.constants import COLOR_SUCCESS, COLOR_ERROR, COLOR_TEXT_MUTED


class DropLineEdit(QLineEdit):
    """Custom QLineEdit supporting file drag-and-drop from OS file explorer."""

    file_dropped = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText("Select executable or drag & drop file here...")

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path:
                self.setText(file_path)
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()


class StatusBadge(QLabel):
    """Status badge displaying executable validation state (✔ Executable Loaded / ❌ Invalid executable)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.set_badge(False, "❌ Invalid executable")

    def set_badge(self, is_valid: bool, text: str) -> None:
        """Updates text and background indicator color based on validation status."""
        self.setText(text)
        if is_valid:
            self.setStyleSheet(
                f"color: {COLOR_SUCCESS}; font-weight: bold; font-size: 13px; padding: 2px 6px;"
            )
        else:
            self.setStyleSheet(
                f"color: {COLOR_ERROR}; font-weight: bold; font-size: 13px; padding: 2px 6px;"
            )


class CardWidget(QFrame):
    """Modern engineering card container with title header, border, and rounded corners."""

    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("CardWidget")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 14, 16, 16)
        self.main_layout.setSpacing(12)

        # Title Label
        self.title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName("CardTitle")

        self.main_layout.addWidget(self.title_label)

    def set_content_layout(self, layout: QVBoxLayout) -> None:
        """Attaches a child content layout below the title header."""
        self.main_layout.addLayout(layout)


class CommandPreviewWidget(QFrame):
    """Styled monospace widget showing live generated command preview with Copy button."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("CommandPreviewCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        header_layout = QHBoxLayout()
        header_label = QLabel("Command Preview")
        header_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #8b949e;")
        
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFixedSize(50, 22)
        self.copy_btn.setToolTip("Copy command to clipboard")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.copy_btn)

        self.preview_text = QLabel("(Select executable to view command preview)")
        self.preview_text.setWordWrap(True)
        self.preview_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.preview_text.setFont(font)
        self.preview_text.setStyleSheet("color: #58a6ff; font-weight: bold;")

        layout.addLayout(header_layout)
        layout.addWidget(self.preview_text)

    def set_command_text(self, text: str) -> None:
        self.preview_text.setText(text)

    def _copy_to_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.preview_text.text())
            self.copy_btn.setText("Copied!")
            QApplication.processEvents()
            # Reset text after brief moment
            self.copy_btn.setText("Copy")
