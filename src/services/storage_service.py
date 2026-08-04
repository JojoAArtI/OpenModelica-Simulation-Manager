"""Storage service for persisting and querying simulation execution history."""

from typing import List
from src.core.settings_manager import SettingsManager
from src.models.simulation_result import SimulationResult


class StorageService:
    """Handles execution record storage, history persistence, and retrieval."""

    def __init__(self, settings_manager: SettingsManager) -> None:
        self.settings_manager = settings_manager

    def save_result(self, result: SimulationResult) -> None:
        """Saves a simulation result into persistent storage."""
        self.settings_manager.save_execution_record(result.to_dict())

    def get_all_results(self) -> List[SimulationResult]:
        """Retrieves all stored simulation history records as SimulationResult objects."""
        raw_history = self.settings_manager.get_execution_history()
        results: List[SimulationResult] = []
        for item in raw_history:
            try:
                results.append(SimulationResult.from_dict(item))
            except Exception:
                continue
        return results

    def clear_history(self) -> None:
        """Clears all stored execution history."""
        self.settings_manager.clear_execution_history()
