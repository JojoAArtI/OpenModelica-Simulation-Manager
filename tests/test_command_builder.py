"""Unit tests for CommandBuilder component."""

from src.core.command_builder import CommandBuilder
from src.models.simulation_config import SimulationConfig


def test_command_builder_exe_override():
    config = SimulationConfig(
        executable_path="TwoConnectedTanks.exe",
        start_time=0,
        stop_time=4,
    )
    args = CommandBuilder.build_command_args(config)
    assert len(args) == 2
    assert args[1] == "-override=startTime=0,stopTime=4"


def test_command_builder_python_script():
    config = SimulationConfig(
        executable_path="TwoConnectedTanks.py",
        start_time=1,
        stop_time=3,
    )
    args = CommandBuilder.build_command_args(config)
    assert len(args) == 3
    assert args[2] == "-override=startTime=1,stopTime=3"


def test_command_builder_preview_string():
    config = SimulationConfig(
        executable_path="TwoConnectedTanks.exe",
        start_time=0,
        stop_time=4,
    )
    preview = CommandBuilder.build_preview_string(config)
    assert "TwoConnectedTanks.exe" in preview
    assert "-override=startTime=0,stopTime=4" in preview
