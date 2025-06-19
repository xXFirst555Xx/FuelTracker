from datetime import date
from decimal import Decimal

from sqlmodel import Session
import pytest

from src.models import FuelEntry, Vehicle, FuelPrice
from src.services import StorageService


def test_first_fill(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(name="Car", vehicle_type="t", license_plate="x", tank_capacity_liters=40)
    storage.add_vehicle(vehicle)
    entry = FuelEntry(entry_date=date(2024, 1, 1), vehicle_id=vehicle.id, odo_before=1000.0, amount_spent=800.0)
    storage.add_entry(entry)
    fetched = storage.get_entry(entry.id)
    assert fetched.odo_after is None
    assert fetched.liters is None


def test_normal_flow_completes_previous(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(name="Car", vehicle_type="t", license_plate="x", tank_capacity_liters=40)
    storage.add_vehicle(vehicle)

    with Session(storage.engine) as s:
        s.add(FuelPrice(date=date(2024, 1, 1), station="ptt", fuel_type="e20", name_th="E20", price=Decimal("40")))
        s.commit()

    first = FuelEntry(entry_date=date(2024, 1, 1), vehicle_id=vehicle.id, fuel_type="e20", odo_before=1000.0, amount_spent=800.0)
    storage.add_entry(first)
    second = FuelEntry(entry_date=date(2024, 1, 5), vehicle_id=vehicle.id, fuel_type="e20", odo_before=1100.0, amount_spent=600.0)
    storage.add_entry(second)

    updated = storage.get_entry(first.id)
    assert updated.odo_after == 1100.0
    assert updated.liters == pytest.approx(20.0)
    metrics = updated.calc_metrics()
    assert metrics["distance"] == pytest.approx(100.0)
    assert metrics["fuel_efficiency_km_l"] == pytest.approx(5.0)


def test_missing_price_keeps_liters_none(in_memory_storage: StorageService) -> None:
    storage = in_memory_storage
    vehicle = Vehicle(name="Car", vehicle_type="t", license_plate="x", tank_capacity_liters=40)
    storage.add_vehicle(vehicle)

    first = FuelEntry(entry_date=date(2024, 1, 1), vehicle_id=vehicle.id, fuel_type="e20", odo_before=1000.0, amount_spent=800.0)
    storage.add_entry(first)
    second = FuelEntry(entry_date=date(2024, 1, 3), vehicle_id=vehicle.id, fuel_type="e20", odo_before=1100.0, amount_spent=500.0)
    storage.add_entry(second)

    updated = storage.get_entry(first.id)
    assert updated.odo_after == 1100.0
    assert updated.liters is None
