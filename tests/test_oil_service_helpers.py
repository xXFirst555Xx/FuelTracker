from datetime import date
from sqlmodel import Session, select

from src.services import oil_service
from src.models import FuelPrice


def test_parse_thai_date():
    day = oil_service._parse_thai_date("1 มกราคม 2567")
    assert day == date(2024, 1, 1)


def test_parse_prices_dedup(in_memory_storage):
    data = {
        "ptt": {
            "e20": {"name_th": "E20", "price": 40},
            "g91": {"name_th": "G91", "price": 44},
        },
        "bcp": {
            "e20": {"name_th": "E20", "price": 41},
        },
    }
    day = date(2024, 1, 1)
    with Session(in_memory_storage.engine) as s:
        oil_service._parse_prices(data, day, s)
        rows = s.exec(select(FuelPrice)).all()
        assert len(rows) == 3

        oil_service._parse_prices(data, day, s)
        rows_again = s.exec(select(FuelPrice)).all()
        assert len(rows_again) == 3
