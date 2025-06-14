"""Service for generating simple reports based on stored entries."""

from typing import Dict

from ..models import FuelEntry
from .storage_service import StorageService


class ReportService:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def calc_overall_stats(self) -> Dict[str, float]:
        entries = self.storage.list_entries()
        total_distance = sum(e.distance for e in entries)
        total_liters = sum(e.liters for e in entries)
        total_price = sum(e.price for e in entries)

        avg_consumption = (total_liters / total_distance * 100) if total_distance else 0.0
        cost_per_km = (total_price / total_distance) if total_distance else 0.0

        return {
            "total_distance": total_distance,
            "total_liters": total_liters,
            "total_price": total_price,
            "avg_consumption": avg_consumption,
            "cost_per_km": cost_per_km,
        }

    def generate_report(self) -> None:
        stats = self.calc_overall_stats()
        print("Generated report:")
        for key, value in stats.items():
            print(f"{key}: {value}")
