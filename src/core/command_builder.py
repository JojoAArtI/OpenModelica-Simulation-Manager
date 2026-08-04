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

        # If it's a Python script, prefix with Python interpreter
        if exe_path.endswith(".py"):
            args = [sys.executable, exe_path, override_flag]
        else:
            args = [exe_path, override_flag]

        if config.custom_args:
            args.extend(config.custom_args)

        return args

    @classmethod
    def build_preview_string(cls, config: SimulationConfig) -> str:
        """Generates clean human-readable command string preview for GUI display.

        Example output:
            TwoConnectedTanks.exe -override=startTime=0,stopTime=4

        Args:
            config: SimulationConfig instance.

        Returns:
            Formatted CLI command string preview.
        """
        args = cls.build_command_args(config)
        if not args:
            return "(Select executable to view command preview)"

        formatted_tokens = []
        for token in args:
            if " " in token:
                formatted_tokens.append(f'"{token}"')
            else:
                formatted_tokens.append(token)

        return " ".join(formatted_tokens)
