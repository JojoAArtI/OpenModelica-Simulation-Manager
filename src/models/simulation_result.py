"""Data model encapsulating the outcome of an OpenModelica simulation execution."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SimulationResult:
    """Encapsulates process execution results including stdout, stderr, exit code, and execution timing.

    Attributes:
        executable_name: Basename of executable executed.
        command_executed: Full command string executed.
        exit_code: Subprocess exit code (0 indicates success).
        stdout: Accumulated standard output string.
        stderr: Accumulated standard error string.
        execution_time_seconds: Total duration of simulation run in seconds.
        timestamp: ISO format string of when execution completed.
        error_message: Friendly error description if execution failed.
    """
    executable_name: str
    command_executed: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    execution_time_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Returns True if process completed with exit code 0."""
        return self.exit_code == 0

    def to_dict(self) -> dict:
        """Serializes result object to dictionary for JSON persistence."""
        return {
            "executable_name": self.executable_name,
            "command_executed": self.command_executed,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp,
            "error_message": self.error_message,
            "is_success": self.is_success,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SimulationResult":
        """Deserializes dictionary back into SimulationResult instance."""
        return cls(
            executable_name=data.get("executable_name", ""),
            command_executed=data.get("command_executed", ""),
            exit_code=data.get("exit_code", -1),
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            execution_time_seconds=data.get("execution_time_seconds", 0.0),
            timestamp=data.get("timestamp", ""),
            error_message=data.get("error_message"),
        )
