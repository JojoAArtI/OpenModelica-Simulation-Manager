"""Custom exceptions for OpenModelica Simulation Manager."""


class SimulationManagerError(Exception):
    """Base exception for all errors in OpenModelica Simulation Manager."""
    pass


class InvalidExecutableError(SimulationManagerError):
    """Raised when the specified file is not a valid executable."""
    pass


class ValidationError(SimulationManagerError):
    """Raised when runtime arguments or inputs fail validation rules."""
    pass


class SimulationExecutionError(SimulationManagerError):
    """Raised when the subprocess execution fails."""

    def __init__(self, message: str, exit_code: int = -1, stderr: str = "") -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


class SimulationTimeoutError(SimulationExecutionError):
    """Raised when simulation execution exceeds the maximum allowed timeout."""
    pass
