"""Asynchronous worker executing OpenModelica simulation subprocess."""

import os
import subprocess
import time
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from src.models.simulation_config import SimulationConfig
from src.models.simulation_result import SimulationResult
from src.core.command_builder import CommandBuilder


class SimulationRunner(QObject):
    """Worker object that runs an OpenModelica simulation binary asynchronously in a separate QThread."""

    stdout_line_emitted = pyqtSignal(str)
    stderr_line_emitted = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    execution_finished = pyqtSignal(SimulationResult)
    execution_error = pyqtSignal(str)

    def __init__(self, config: SimulationConfig) -> None:
        super().__init__()
        self.config = config
        self._is_cancelled = False
        self._process: Optional[subprocess.Popen] = None

    def cancel(self) -> None:
        """Requests cancellation of the running subprocess."""
        self._is_cancelled = True
        if self._process and self._process.poll() is None:
            try:
                self.status_updated.emit("Cancelling simulation process...")
                self._process.terminate()
                # Give process a moment to terminate gracefully, else kill
                time.sleep(0.2)
                if self._process.poll() is None:
                    self._process.kill()
            except Exception as e:
                self.execution_error.emit(f"Error while terminating process: {e}")

    def run(self) -> None:
        """Executes the simulation subprocess and streams stdout/stderr live."""
        command_args = CommandBuilder.build_command_args(self.config)
        command_str = CommandBuilder.build_preview_string(self.config)

        if not command_args:
            self.execution_error.emit("Invalid command: Empty argument list.")
            return

        stdout_chunks: List[str] = []
        stderr_chunks: List[str] = []

        start_time_stamp = time.perf_counter()
        self.status_updated.emit("Starting simulation executable...")
        self.stdout_line_emitted.emit(f"[INFO] Executing command: {command_str}\n")

        try:
            # Set environment to unbuffered output if running python script mock
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            self._process = subprocess.Popen(
                command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
            )

            # Read stdout line by line
            if self._process.stdout:
                for line in iter(self._process.stdout.readline, ""):
                    if self._is_cancelled:
                        break
                    stdout_chunks.append(line)
                    self.stdout_line_emitted.emit(line)

            # Read stderr line by line
            if self._process.stderr:
                for line in iter(self._process.stderr.readline, ""):
                    stderr_chunks.append(line)
                    self.stderr_line_emitted.emit(line)

            self._process.wait()
            exit_code = self._process.returncode if not self._is_cancelled else -15

        except FileNotFoundError as e:
            duration = time.perf_counter() - start_time_stamp
            err_msg = f"Executable file not found: {e}"
            self.execution_error.emit(err_msg)
            result = SimulationResult(
                executable_name=self.config.executable_name,
                command_executed=command_str,
                exit_code=-1,
                stdout="".join(stdout_chunks),
                stderr=err_msg,
                execution_time_seconds=duration,
                error_message=err_msg,
            )
            self.execution_finished.emit(result)
            return

        except Exception as e:
            duration = time.perf_counter() - start_time_stamp
            err_msg = f"Unexpected execution failure: {str(e)}"
            self.execution_error.emit(err_msg)
            result = SimulationResult(
                executable_name=self.config.executable_name,
                command_executed=command_str,
                exit_code=-1,
                stdout="".join(stdout_chunks),
                stderr=err_msg,
                execution_time_seconds=duration,
                error_message=err_msg,
            )
            self.execution_finished.emit(result)
            return

        duration = time.perf_counter() - start_time_stamp
        stdout_full = "".join(stdout_chunks)
        stderr_full = "".join(stderr_chunks)

        if self._is_cancelled:
            result = SimulationResult(
                executable_name=self.config.executable_name,
                command_executed=command_str,
                exit_code=-15,
                stdout=stdout_full,
                stderr=stderr_full + "\n[CANCELLED] Simulation was terminated by user.",
                execution_time_seconds=duration,
                error_message="Simulation cancelled by user.",
            )
        else:
            result = SimulationResult(
                executable_name=self.config.executable_name,
                command_executed=command_str,
                exit_code=exit_code,
                stdout=stdout_full,
                stderr=stderr_full,
                execution_time_seconds=duration,
                error_message=None if exit_code == 0 else f"Process exited with non-zero exit code {exit_code}.",
            )

        self.execution_finished.emit(result)
