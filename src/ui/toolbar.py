"""Application main toolbar featuring branding, quick controls, theme toggle, and settings."""

from typing import Optional
from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QToolBar,
    QLabel,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QToolButton,
)

from src.utils.constants import APP_NAME


class MainToolBar(QToolBar):
    """Top toolbar for OpenModelica Simulation Manager."""

    theme_toggle_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    history_clicked = pyqtSignal()
    about_clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(20, 20))
        self.setObjectName("MainToolBar")

        self._build_toolbar()

    def _build_toolbar(self) -> None:
        # Container widget for spacing
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        from src.utils.helpers import get_resource_path

        # Branding Label (small OpenModelica icon + Application Title)
        brand_icon = QIcon(str(get_resource_path("resources/icons/openmodelica.svg")))
        brand_pixmap = brand_icon.pixmap(20, 20)
        brand_icon_label = QLabel()
        if not brand_pixmap.isNull():
            brand_icon_label.setPixmap(brand_pixmap)

        brand_label = QLabel(f"<b>OpenModelica</b> | {APP_NAME}")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        brand_label.setFont(font)
        brand_label.setObjectName("ToolbarBrandLabel")

        # Control Buttons with QIcon
        self.history_btn = QPushButton(QIcon(str(get_resource_path("resources/icons/history.svg"))), "Execution History")
        self.history_btn.setToolTip("View recent simulation execution history")
        self.history_btn.clicked.connect(self.history_clicked.emit)

        self.theme_btn = QPushButton(QIcon(str(get_resource_path("resources/icons/theme.svg"))), "Toggle Theme")
        self.theme_btn.setToolTip("Switch between Dark and Light engineering themes")
        self.theme_btn.clicked.connect(self.theme_toggle_clicked.emit)

        self.settings_btn = QPushButton(QIcon(str(get_resource_path("resources/icons/settings.svg"))), "Settings")
        self.settings_btn.setToolTip("Configure application preferences")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)

        self.about_btn = QPushButton(QIcon(str(get_resource_path("resources/icons/info.svg"))), "About")
        self.about_btn.setToolTip("About OpenModelica Simulation Manager")
        self.about_btn.clicked.connect(self.about_clicked.emit)


        # Assemble layout
        if not brand_pixmap.isNull():
            layout.addWidget(brand_icon_label)
        layout.addWidget(brand_label)
        layout.addStretch()
        layout.addWidget(self.history_btn)
        layout.addWidget(self.theme_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.about_btn)


        self.addWidget(container)
