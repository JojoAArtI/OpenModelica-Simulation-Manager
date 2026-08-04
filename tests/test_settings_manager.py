"""Unit tests for SettingsManager component."""

import pytest
from PyQt6.QtCore import QCoreApplication
from src.core.settings_manager import SettingsManager


@pytest.fixture(autouse=True)
def init_qapp():
    if not QCoreApplication.instance():
        app = QCoreApplication([])
        yield app
    else:
        yield QCoreApplication.instance()


def test_settings_manager_theme():
    sm = SettingsManager()
    sm.set_theme("dark")
    assert sm.get_theme() == "dark"

    sm.set_theme("light")
    assert sm.get_theme() == "light"


def test_settings_manager_start_stop_times():
    sm = SettingsManager()
    sm.set_last_start_time(1)
    assert sm.get_last_start_time() == 1

    sm.set_last_stop_time(3)
    assert sm.get_last_stop_time() == 3


def test_settings_manager_recents():
    sm = SettingsManager()
    sm.add_recent_executable("model_a.exe")
    sm.add_recent_executable("model_b.exe")
    recents = sm.get_recent_executables()
    assert recents[0] == "model_b.exe"
    assert "model_a.exe" in recents
