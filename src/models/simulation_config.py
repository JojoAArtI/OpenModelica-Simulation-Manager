"""Data model representing OpenModelica simulation execution parameters."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SimulationConfig:
    """Encapsulates executable path and time parameters for an OpenModelica simulation run.

    Attributes:
        executable_path: Path to the OpenModelica generated executable.
        start_time: Simulation start time (integer, 0 <= start_time).
        stop_time: Simulation stop time (integer, start_time < stop_time < 5).
        custom_args: Optional additional command line override flags.
    """
    executable_path: str
    start_time: int
    stop_time: int
    custom_args: List[str] = field(default_factory=list)

    def to_override_flag(self) -> str:
        """Generates OpenModelica override flag string.

        Example: `-override=startTime=0,stopTime=4`

        Returns:
            Formatted override CLI flag string.
        """
        return f"-override=startTime={self.start_time},stopTime={self.stop_time}"

    @property
    def executable_name(self) -> str:
        """Extracts executable file basename."""
        if not self.executable_path:
            return "UnknownExecutable"
        return Path(self.executable_path).name
