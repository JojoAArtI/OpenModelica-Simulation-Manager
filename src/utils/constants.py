"""Application constants and configuration defaults for OpenModelica Simulation Manager."""

from pathlib import Path

# Application Metadata
APP_NAME = "OpenModelica Simulation Manager"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "FOSSEE"
ORGANIZATION_DOMAIN = "openmodelica.org"

# Validation Constraints (per screening specification)
MIN_START_TIME = 0
MAX_START_TIME = 4
MIN_STOP_TIME = 1
MAX_STOP_TIME = 4
MAX_SIMULATION_TIME_UPPER_BOUND = 5

# QSettings Keys
SETTINGS_KEY_GEOMETRY = "window/geometry"
SETTINGS_KEY_SPLITTER_STATE = "window/splitter_state"
SETTINGS_KEY_THEME = "ui/theme"
SETTINGS_KEY_RECENT_EXECUTABLES = "history/recent_executables"
SETTINGS_KEY_LAST_START_TIME = "simulation/last_start_time"
SETTINGS_KEY_LAST_STOP_TIME = "simulation/last_stop_time"
SETTINGS_KEY_EXECUTION_HISTORY = "history/execution_records"

MAX_RECENT_FILES = 10
MAX_HISTORY_RECORDS = 50

# Themes
THEME_DARK = "dark"
THEME_LIGHT = "light"

# Color Palette (Dark Theme engineering accents)
COLOR_SUCCESS = "#2ea44f"
COLOR_SUCCESS_HOVER = "#3fb950"
COLOR_ERROR = "#f85149"
COLOR_WARNING = "#d29922"
COLOR_INFO = "#58a6ff"
COLOR_BG_DARK = "#0d1117"
COLOR_CARD_DARK = "#161b22"
COLOR_BORDER_DARK = "#30363d"
COLOR_TEXT_MAIN = "#c9d1d9"
COLOR_TEXT_MUTED = "#8b949e"
