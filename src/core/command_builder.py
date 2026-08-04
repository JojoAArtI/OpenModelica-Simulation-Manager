"""Command generator for OpenModelica simulation binary execution."""

import sys
from pathlib import Path
from typing import List
from src.models.simulation_config import SimulationConfig


class CommandBuilder:
    """Constructs command arguments and display strings for OpenModelica executables."""

    @staticmethod
    def build_command_args(config: SimulationConfig) -> List[str]:
        """Generates list of command line arguments for subprocess execution.

        Args:
            config: SimulationConfig instance containing executable path and parameters.

        Returns:
            List of command tokens e.g. ["TwoConnectedTanks.exe", "-override=startTime=0,stopTime=4"].
        """
        if not config or not config.executable_path:
            return []

        exe_path = str(Path(config.executable_path).resolve())
        override_flag = config.to_override_flag()

        # Check if running inside a PyInstaller frozen binary
        is_frozen = getattr(sys, "frozen", False)

        if exe_path.lower().endswith(".py"):
            # Use 'python' executable instead of sys.executable when frozen to prevent re-launching self
            python_bin = "python" if is_frozen else sys.executable
            args = [python_bin, exe_path, override_flag]
        else:
            # Standalone binaries (.exe, .bat, etc.) run directly
            args = [exe_path, override_flag]

        if config.custom_args:
            args.extend(config.custom_args)

        return args

    @classmethod
    def build_preview_string(cls, config: SimulationConfig, relative: bool = True) -> str:
        """Generates clean human-readable command string preview for GUI display.

        Example output (relative=True):
            TwoConnectedTanks.exe -override=startTime=0,stopTime=4

        Example output (relative=False):
            "C:/path/to/TwoConnectedTanks.exe" -override=startTime=0,stopTime=4

        Args:
            config: SimulationConfig instance.
            relative: If True, uses clean executable basename for compact UI preview.

        Returns:
            Formatted CLI command string preview.
        """
        if not config or not config.executable_path:
            return "(Select executable to view command preview)"

        override_flag = config.to_override_flag()

        if relative:
            exe_display = config.executable_name
            if exe_display.lower().endswith(".py"):
                tokens = ["python", exe_display, override_flag]
            else:
                tokens = [exe_display, override_flag]
        else:
            tokens = cls.build_command_args(config)

        formatted_tokens = []
        for token in tokens:
            if " " in token:
                formatted_tokens.append(f'"{token}"')
            else:
                formatted_tokens.append(token)

        return " ".join(formatted_tokens)
