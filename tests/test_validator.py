"""Unit tests for Validator component."""

import pytest
from pathlib import Path
from src.core.validator import Validator
from src.models.simulation_config import SimulationConfig


def test_validate_times_valid():
    is_valid, msg = Validator.validate_times(0, 4)
    assert is_valid is True

    is_valid, msg = Validator.validate_times(1, 3)
    assert is_valid is True


def test_validate_times_invalid_negative_start():
    is_valid, msg = Validator.validate_times(-1, 4)
    assert is_valid is False
    assert "Start time must be >=" in msg


def test_validate_times_invalid_start_ge_stop():
    is_valid, msg = Validator.validate_times(3, 3)
    assert is_valid is False
    assert "strictly less than" in msg

    is_valid, msg = Validator.validate_times(4, 2)
    assert is_valid is False


def test_validate_times_invalid_stop_ge_5():
    is_valid, msg = Validator.validate_times(0, 5)
    assert is_valid is False
    assert "Stop time must be <=" in msg


def test_validate_executable_nonexistent():
    is_valid, msg = Validator.validate_executable("non_existent_file.exe")
    assert is_valid is False
    assert "File does not exist" in msg


def test_validate_executable_valid(tmp_path):
    exe_file = tmp_path / "mock_model.exe"
    exe_file.write_text("mock binary data")
    
    is_valid, msg = Validator.validate_executable(str(exe_file))
    assert is_valid is True


def test_validate_config_neutral_initial_state():
    res = Validator.validate_config(None)
    assert res.is_valid is False
    assert res.badge_state == "neutral"
    assert res.badge_text == "ℹ No executable selected"
    assert "Please select or drag & drop" in res.message

    empty_config = SimulationConfig(executable_path="", start_time=0, stop_time=4)
    res_empty = Validator.validate_config(empty_config)
    assert res_empty.is_valid is False
    assert res_empty.badge_state == "neutral"
    assert res_empty.badge_text == "ℹ No executable selected"

