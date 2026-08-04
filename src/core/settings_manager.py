"""Settings management using QSettings for persisting user preferences and execution history."""

import json
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QSettings, QByteArray

from src.utils.constants import (
    ORGANIZATION_NAME,
    APP_NAME,
    SETTINGS_KEY_GEOMETRY,
    SETTINGS_KEY_SPLITTER_STATE,
    SETTINGS_KEY_THEME,
    SETTINGS_KEY_RECENT_EXECUTABLES,
    SETTINGS_KEY_LAST_START_TIME,
    SETTINGS_KEY_LAST_STOP_TIME,
    SETTINGS_KEY_EXECUTION_HISTORY,
    THEME_DARK,
    MAX_RECENT_FILES,
    MAX_HISTORY_RECORDS,
)


class SettingsManager:
    """Manages persistent application state, user preferences, and execution history."""

    def __init__(self) -> None:
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)

    # Window Geometry & Splitter
    def save_window_geometry(self, geometry: QByteArray) -> None:
        self.settings.setValue(SETTINGS_KEY_GEOMETRY, geometry)

    def load_window_geometry(self) -> Optional[QByteArray]:
        val = self.settings.value(SETTINGS_KEY_GEOMETRY)
        return val if isinstance(val, QByteArray) else None

    def save_splitter_state(self, state: QByteArray) -> None:
        self.settings.setValue(SETTINGS_KEY_SPLITTER_STATE, state)

    def load_splitter_state(self) -> Optional[QByteArray]:
        val = self.settings.value(SETTINGS_KEY_SPLITTER_STATE)
        return val if isinstance(val, QByteArray) else None

    # Theme
    def get_theme(self) -> str:
        return str(self.settings.value(SETTINGS_KEY_THEME, THEME_DARK))

    def set_theme(self, theme_name: str) -> None:
        self.settings.setValue(SETTINGS_KEY_THEME, theme_name)

    # Recent Executables
    def get_recent_executables(self) -> List[str]:
        val = self.settings.value(SETTINGS_KEY_RECENT_EXECUTABLES, [])
        if isinstance(val, list):
            return [str(item) for item in val if item]
        return []

    def add_recent_executable(self, path_str: str) -> None:
        if not path_str:
            return
        recents = self.get_recent_executables()
        # Remove if already present, insert at front
        recents = [p for p in recents if p != path_str]
        recents.insert(0, path_str)
        recents = recents[:MAX_RECENT_FILES]
        self.settings.setValue(SETTINGS_KEY_RECENT_EXECUTABLES, recents)

    # Simulation Defaults
    def get_last_start_time(self) -> int:
        return int(self.settings.value(SETTINGS_KEY_LAST_START_TIME, 0))

    def set_last_start_time(self, start_time: int) -> None:
        self.settings.setValue(SETTINGS_KEY_LAST_START_TIME, start_time)

    def get_last_stop_time(self) -> int:
        return int(self.settings.value(SETTINGS_KEY_LAST_STOP_TIME, 4))

    def set_last_stop_time(self, stop_time: int) -> None:
        self.settings.setValue(SETTINGS_KEY_LAST_STOP_TIME, stop_time)

    # Execution History
    def get_execution_history(self) -> List[Dict[str, Any]]:
        raw_json = self.settings.value(SETTINGS_KEY_EXECUTION_HISTORY, "[]")
        try:
            return json.loads(str(raw_json))
        except (json.JSONDecodeError, TypeError):
            return []

    def save_execution_record(self, record_dict: Dict[str, Any]) -> None:
        history = self.get_execution_history()
        history.insert(0, record_dict)
        history = history[:MAX_HISTORY_RECORDS]
        self.settings.setValue(SETTINGS_KEY_EXECUTION_HISTORY, json.dumps(history))

    def clear_execution_history(self) -> None:
        self.settings.setValue(SETTINGS_KEY_EXECUTION_HISTORY, "[]")
