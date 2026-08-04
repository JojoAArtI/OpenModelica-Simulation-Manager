"""Validation engine for OpenModelica simulation inputs and executable paths."""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional

from src.models.simulation_config import SimulationConfig
from src.utils.constants import (
    MIN_START_TIME,
    MAX_START_TIME,
    MIN_STOP_TIME,
    MAX_STOP_TIME,
    MAX_SIMULATION_TIME_UPPER_BOUND,
)
from src.utils.helpers import is_executable_file


@dataclass
class ValidationResult:
    """Encapsulates validation result status, feedback message, and badge UI state.

    Attributes:
        is_valid: Boolean indicating whether inputs meet all criteria.
        message: Human-readable feedback message describing validation status.
        badge_text: Short status text e.g. "✔ Executable Loaded", "❌ Invalid executable", "ℹ No executable selected".
        badge_state: Visual state category e.g. "valid", "invalid", "neutral".
    """
    is_valid: bool
    message: str
    badge_text: str
    badge_state: str = "neutral"


class Validator:
    """Validates OpenModelica simulation inputs, file paths, and time boundaries."""

    @staticmethod
    def validate_executable(path_str: str) -> Tuple[bool, str]:
        """Validates the target executable path.

        Args:
            path_str: Target executable path string.

        Returns:
            Tuple of (is_valid: bool, status_message: str).
        """
        if not path_str or not path_str.strip():
            return False, "Please select or drag & drop an OpenModelica simulation executable."

        p = Path(path_str.strip())
        if not p.exists():
            return False, f"File does not exist: '{p.name}'"

        if not p.is_file():
            return False, "Selected path is a directory, not an executable file."

        if p.suffix.lower() in {".log", ".txt", ".json", ".qss", ".md"}:
            return False, f"Selected file '{p.name}' is a document/log file, not an executable binary."

        if not is_executable_file(p):
            return False, f"File exists but is not executable: '{p.name}'"


        return True, "Executable loaded successfully."

    @staticmethod
    def validate_times(start_time: int, stop_time: int) -> Tuple[bool, str]:
        """Validates simulation start time and stop time against screening rules.

        Rules:
        - 0 <= start_time
        - start_time < stop_time
        - stop_time < 5

        Args:
            start_time: Integer start time.
            stop_time: Integer stop time.

        Returns:
            Tuple of (is_valid: bool, validation_message: str).
        """
        if start_time < MIN_START_TIME:
            return False, f"Start time must be >= {MIN_START_TIME}."

        if start_time > MAX_START_TIME:
            return False, f"Start time must be <= {MAX_START_TIME}."

        if stop_time < MIN_STOP_TIME:
            return False, f"Stop time must be >= {MIN_STOP_TIME}."

        if stop_time > MAX_STOP_TIME:
            return False, f"Stop time must be <= {MAX_STOP_TIME}."

        if start_time >= stop_time:
            return False, f"Start time ({start_time}) must be strictly less than Stop time ({stop_time})."

        if stop_time >= MAX_SIMULATION_TIME_UPPER_BOUND:
            return False, f"Stop time ({stop_time}) must be strictly less than {MAX_SIMULATION_TIME_UPPER_BOUND}."

        return True, "Simulation parameters are valid."

    @classmethod
    def validate_config(cls, config: Optional[SimulationConfig]) -> ValidationResult:
        """Performs full combined validation on a SimulationConfig instance.

        Args:
            config: SimulationConfig instance to validate.

        Returns:
            ValidationResult containing status, message, badge text, and state.
        """
        if config is None or not config.executable_path.strip():
            return ValidationResult(
                is_valid=False,
                message="Please select or drag & drop an OpenModelica simulation executable.",
                badge_text="ℹ No executable selected",
                badge_state="neutral",
            )

        # 1. Check Executable
        exe_valid, exe_msg = cls.validate_executable(config.executable_path)
        if not exe_valid:
            return ValidationResult(
                is_valid=False,
                message=exe_msg,
                badge_text="❌ Invalid executable",
                badge_state="invalid",
            )

        # 2. Check Time Bounds
        time_valid, time_msg = cls.validate_times(config.start_time, config.stop_time)
        if not time_valid:
            return ValidationResult(
                is_valid=False,
                message=time_msg,
                badge_text="✔ Executable Loaded",  # Executable itself is valid, but times need fixing
                badge_state="valid",
            )

        return ValidationResult(
            is_valid=True,
            message="Configuration valid. Ready to simulate.",
            badge_text="✔ Executable Loaded",
            badge_state="valid",
        )
