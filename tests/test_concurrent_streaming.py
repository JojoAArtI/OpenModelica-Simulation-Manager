"""Integration test verifying concurrent stdout and stderr streaming in SimulationRunner."""

import sys
import tempfile
from pathlib import Path
import pytest
from PyQt6.QtCore import QCoreApplication, QEventLoop, QTimer

from src.models.simulation_config import SimulationConfig
from src.core.simulation_runner import SimulationRunner


@pytest.fixture(autouse=True)
def init_qapp():
    if not QCoreApplication.instance():
        app = QCoreApplication([])
        yield app
    else:
        yield QCoreApplication.instance()


import textwrap

def test_concurrent_stdout_stderr_streaming(tmp_path):
    # Create a script that outputs to both stdout and stderr concurrently
    test_script = tmp_path / "stream_test.py"
    test_script.write_text(textwrap.dedent("""\
        import sys
        import time

        print("[STDOUT 1]")
        sys.stdout.flush()
        print("[STDERR 1]", file=sys.stderr)
        sys.stderr.flush()
        time.sleep(0.05)
        print("[STDOUT 2]")
        sys.stdout.flush()
        print("[STDERR 2]", file=sys.stderr)
        sys.stderr.flush()
    """), encoding="utf-8")


    config = SimulationConfig(
        executable_path=str(test_script),
        start_time=0,
        stop_time=4,
    )

    runner = SimulationRunner(config)
    stdout_lines = []
    stderr_lines = []
    result_holder = []

    def on_stdout(line):
        stdout_lines.append(line)

    def on_stderr(line):
        stderr_lines.append(line)

    def on_finished(res):
        result_holder.append(res)
        loop.quit()

    loop = QEventLoop()
    runner.stdout_line_emitted.connect(on_stdout)
    runner.stderr_line_emitted.connect(on_stderr)
    runner.execution_finished.connect(on_finished)

    QTimer.singleShot(10, runner.run)
    loop.exec()

    assert len(result_holder) == 1
    res = result_holder[0]
    assert res.is_success is True
    assert any("[STDOUT 1]" in line for line in stdout_lines)
    assert any("[STDOUT 2]" in line for line in stdout_lines)
    assert any("[STDERR 1]" in line for line in stderr_lines)
    assert any("[STDERR 2]" in line for line in stderr_lines)
