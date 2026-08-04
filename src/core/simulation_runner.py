"""Asynchronous worker executing OpenModelica simulation subprocess."""

import os
import sys
import subprocess
import threading
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
                time.sleep(0.2)
                if self._process.poll() is None:
                    self._process.kill()
            except Exception as e:
                self.execution_error.emit(f"Error while terminating process: {e}")

    def _read_pipe(self, pipe, signal_emitter, chunk_list):
        """Reads pipe line-by-line concurrently until EOF."""
        if not pipe:
            return
        for line in iter(pipe.readline, ""):
            if self._is_cancelled:
                break
            chunk_list.append(line)
            signal_emitter.emit(line)
        pipe.close()

    def run(self) -> None:
        """Executes the simulation subprocess with concurrent stdout/stderr streaming."""
        command_args = CommandBuilder.build_command_args(self.config)
        command_str = CommandBuilder.build_preview_string(self.config, relative=False)

        if not command_args:
            self.execution_error.emit("Invalid command: Empty argument list.")
            return

        stdout_chunks: List[str] = []
        stderr_chunks: List[str] = []

        start_time_stamp = time.perf_counter()
        self.status_updated.emit("Starting simulation executable...")
        self.stdout_line_emitted.emit(f"[INFO] Executing command: {command_str}\n")

        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

            self._process = subprocess.Popen(
                command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                creationflags=creation_flags,
            )


            # Spawn concurrent reader threads for stdout and stderr to prevent deadlocks
            t_stdout = threading.Thread(
                target=self._read_pipe,
                args=(self._process.stdout, self.stdout_line_emitted, stdout_chunks),
                daemon=True,
            )
            t_stderr = threading.Thread(
                target=self._read_pipe,
                args=(self._process.stderr, self.stderr_line_emitted, stderr_chunks),
                daemon=True,
            )

            t_stdout.start()
            t_stderr.start()

            # Wait for process and reader threads to finish
            self._process.wait()
            t_stdout.join()
            t_stderr.join()

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

