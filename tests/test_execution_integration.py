"""Integration test for SimulationRunner executing mock OpenModelica executable."""

import pytest
import time
from pathlib import Path
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


def test_simulation_runner_execution():
    mock_script = Path("mock_executable/TwoConnectedTanks.py").resolve()
    assert mock_script.exists()

    config = SimulationConfig(
        executable_path=str(mock_script),
        start_time=0,
        stop_time=4,
    )

    runner = SimulationRunner(config)
    result_holder = []
    stdout_lines = []

    def on_stdout(line):
        stdout_lines.append(line)

    def on_finished(res):
        result_holder.append(res)
        loop.quit()

    loop = QEventLoop()
    runner.stdout_line_emitted.connect(on_stdout)
    runner.execution_finished.connect(on_finished)

    # Run in event loop context
    QTimer.singleShot(10, runner.run)
    loop.exec()

    assert len(result_holder) == 1
    res = result_holder[0]
    assert res.is_success is True
    assert res.exit_code == 0
    assert "TwoConnectedTanks" in res.stdout
    assert "Simulation Integration Loop Started" in res.stdout
    assert res.execution_time_seconds > 0.0
