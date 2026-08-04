"""Logger service providing logging infrastructure for application and execution logs."""

import logging
import sys
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class QtLogHandler(logging.Handler):
    """Custom Python logging Handler that emits logs via a PyQt Signal."""

    def __init__(self, signal: pyqtSignal) -> None:
        super().__init__()
        self.signal = signal

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.signal.emit(msg)


class LoggerService(QObject):
    """Manages application logs, file handlers, and GUI log signal emissions."""

    log_emitted = pyqtSignal(str)

    def __init__(self, log_dir: str = "logs") -> None:
        super().__init__()
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("OpenModelicaManager")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Sets up file and console log handlers."""
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File Handler (app.log)
        app_log_file = self.log_dir / "app.log"
        file_handler = logging.FileHandler(app_log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Execution Log Handler (execution.log)
        exec_log_file = self.log_dir / "execution.log"
        exec_handler = logging.FileHandler(exec_log_file, encoding="utf-8")
        exec_handler.setLevel(logging.DEBUG)
        exec_handler.setFormatter(formatter)
        self.logger.addHandler(exec_handler)

        # Qt Signal Handler for GUI Streaming
        qt_handler = QtLogHandler(self.log_emitted)
        qt_handler.setLevel(logging.INFO)
        qt_handler.setFormatter(formatter)
        self.logger.addHandler(qt_handler)

        # Console Handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)
