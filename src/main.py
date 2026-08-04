"""Main entry point for OpenModelica Simulation Manager application."""

import sys
from pathlib import Path

# Add project root to sys.path to support src imports when launched from any CWD
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from src.core.logger import LoggerService
from src.ui.main_window import MainWindow
from src.utils.constants import APP_NAME, ORGANIZATION_NAME


def main() -> int:
    """Initializes and runs the PyQt6 OpenModelica Simulation Manager desktop application."""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)

    # Initialize Logger Service
    logger_service = LoggerService()
    logger_service.info(f"Starting {APP_NAME}...")

    # Instantiate Main Window
    window = MainWindow(logger_service)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
