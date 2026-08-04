"""Utility helper functions for paths, formatting, and OS interaction."""

import os
import sys
from pathlib import Path
from typing import Union


def get_resource_path(relative_path: str) -> Path:
    """Gets absolute path to resource file, supporting PyInstaller frozen bundle directory (sys._MEIPASS).

    Args:
        relative_path: Relative path string e.g. "resources/styles/dark_theme.qss".

    Returns:
        Path object pointing to existing resource file.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        # src/utils/helpers.py -> project root
        base_path = Path(__file__).resolve().parent.parent.parent

    target = base_path / relative_path
    if target.exists():
        return target

    # Fallback to CWD
    cwd_target = Path.cwd() / relative_path
    if cwd_target.exists():
        return cwd_target

    return target


def format_duration(seconds: float) -> str:
    """Format duration seconds into human-readable string.

    Args:
        seconds: Elapsed time in seconds.

    Returns:
        Formatted string e.g. "0.45s", "12.30s", "1m 05s".
    """
    if seconds < 0:
        return "0.00s"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}m {rem_seconds:05.2f}s"


def is_executable_file(path: Union[str, Path]) -> bool:
    """Check if the given path exists and is executable.

    On Windows, also accepts Python scripts (.py) or Windows binaries (.exe, .bat, .cmd).
    On Unix/Linux, checks os.access(path, os.X_OK).

    Args:
        path: Absolute or relative path string or Path object.

    Returns:
        True if valid executable path, False otherwise.
    """
    if not path:
        return False
    
    p = Path(path).resolve()
    if not p.is_file():
        return False

    if sys.platform == "win32":
        executable_extensions = {".exe", ".bat", ".cmd", ".ps1", ".py"}
        return p.suffix.lower() in executable_extensions or os.access(str(p), os.X_OK)
    
    return os.access(str(p), os.X_OK) or p.suffix == ".py"


def shorten_path(path_str: str, max_chars: int = 50) -> str:
    """Truncate long file paths with ellipsis for clean UI display.

    Args:
        path_str: Path string.
        max_chars: Maximum character length.

    Returns:
        Shortened path string.
    """
    if len(path_str) <= max_chars:
        return path_str
    
    p = Path(path_str)
    filename = p.name
    parent = str(p.parent)
    
    if len(filename) >= max_chars - 5:
        return filename[:max_chars - 5] + "..."
    
    available = max_chars - len(filename) - 5
    return f"{parent[:available]}...{os.sep}{filename}"
