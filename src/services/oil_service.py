from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional

import requests
from sqlmodel import Session, select

from ..models import FuelPrice

# Reusable HTTP session for API requests
_HTTP_SESSION = requests.Session()

API_BASE = "https://api.chnwt.dev/thai-oil-api"

# Mapping of Thai month names to numbers for API date parsing
_THAI_MONTHS = {
    "มกราคม": 1,
    "กุมภาพันธ์": 2,
    "มีนาคม": 3,
    "เมษายน": 4,
    "พฤษภาคม": 5,
    "มิถุนายน": 6,
    "กรกฎาคม": 7,
    "สิงหาคม": 8,
    "กันยายน": 9,
    "ตุลาคม": 10,
    "พฤศจิกายน": 11,
    "ธันวาคม": 12,
}


def _parse_thai_date(text: str) -> date:
    """แปลงวันที่ภาษาไทยจาก API เป็น :class:`~datetime.date`"""

    day_str, month_name, year_str = text.split()
    year = int(year_str) - 543  # convert Buddhist Era to Gregorian
    month = _THAI_MONTHS[month_name]
    return date(year, month, int(day_str))


def _parse_prices(data: Dict[str, Any], day: date, session: Session) -> None:
    for station, fuels in data.items():
        for ftype, info in fuels.items():
            exists = session.exec(
                select(FuelPrice).where(
                    FuelPrice.date == day,
                    FuelPrice.station == station,
                    FuelPrice.fuel_type == ftype,
                )
            ).first()
            if exists is not None:
                continue
            price = Decimal(str(info["price"]))
            session.add(
                FuelPrice(
                    date=day,
                    station=station,
                    fuel_type=ftype,
                    name_th=str(info.get("name_th") or info.get("name", "")),
                    price=price,
                )
            )
    session.commit()


def fetch_latest(session: Session, station: str = "ptt") -> None:
    """ดึงและบันทึกราคาน้ำมันล่าสุดจาก Thai Oil API"""

    resp = _HTTP_SESSION.get(f"{API_BASE}/latest", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    thai_date = data["response"]["date"]
    day = _parse_thai_date(thai_date)
    stations = data["response"]["stations"]
    _parse_prices(stations, day, session)


def get_price(
    session: Session, fuel_type: str, station: str, day: date
) -> Optional[Decimal]:
    row = session.exec(
        select(FuelPrice.price).where(
            FuelPrice.date == day,
            FuelPrice.station == station,
            FuelPrice.fuel_type == fuel_type,
        )
    ).first()
    if row is None:
        return None
    return Decimal(row)
