"""Service for generating simple reports based on stored entries."""

from typing import Dict

from ..models import FuelEntry
from .storage_service import StorageService


class ReportService:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def calc_overall_stats(self) -> Dict[str, float]:
        entries = self.storage.list_entries()
        total_distance = 0.0
        total_liters = 0.0
        total_price = 0.0

        for e in entries:
            distance = e.odo_after - e.odo_before
            total_distance += distance
            if e.liters:
                total_liters += e.liters
            total_price += e.amount_spent

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
