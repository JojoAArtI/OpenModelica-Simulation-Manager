"""Unit tests for SimulationConfig and SimulationResult data models."""

from src.models.simulation_config import SimulationConfig
from src.models.simulation_result import SimulationResult


def test_simulation_config_override_flag():
    config = SimulationConfig(
        executable_path="/models/TankModel.exe",
        start_time=2,
        stop_time=4,
    )
    assert config.to_override_flag() == "-override=startTime=2,stopTime=4"
    assert config.executable_name == "TankModel.exe"


def test_simulation_result_serialization():
    res = SimulationResult(
        executable_name="TankModel.exe",
        command_executed="TankModel.exe -override=startTime=0,stopTime=4",
        exit_code=0,
        stdout="Simulation completed.",
        stderr="",
        execution_time_seconds=1.25,
    )
    assert res.is_success is True

    serialized = res.to_dict()
    res_restored = SimulationResult.from_dict(serialized)
    assert res_restored.executable_name == "TankModel.exe"
    assert res_restored.exit_code == 0
    assert res_restored.execution_time_seconds == 1.25
