from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional, cast
import os

import requests  # type: ignore[import-untyped]
from sqlmodel import Session, select
from sqlalchemy import delete

from ..models import FuelPrice, FuelEntry

# Reusable HTTP session for API requests
_HTTP_SESSION = requests.Session()

API_BASE = "https://api.chnwt.dev/thai-oil-api"
DEFAULT_RETENTION_DAYS = 30
# Default number of days to look back when price for a specific day is missing
DEFAULT_FALLBACK_DAYS = 7

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


def purge_old_prices(session: Session, days: int | None = None) -> None:
    """Remove :class:`FuelPrice` rows older than ``days``.

    The number of days defaults to the ``OIL_PRICE_RETENTION_DAYS`` environment
    variable or :data:`DEFAULT_RETENTION_DAYS`.
    """

    if days is None:
        try:
            days = int(os.getenv("OIL_PRICE_RETENTION_DAYS", ""))
        except ValueError:
            days = DEFAULT_RETENTION_DAYS
        if not days:
            days = DEFAULT_RETENTION_DAYS
    # Use the most recent price date when available so tests remain
    # deterministic even if the current system date is far in the future.
    max_day = session.exec(
        select(cast(Any, FuelPrice.date)).order_by(cast(Any, FuelPrice.date).desc())
    ).first()
    base_day = max_day or date.today()
    cutoff = base_day - timedelta(days=days)
    session.execute(delete(FuelPrice).where(cast(Any, FuelPrice.date) < cutoff))
    session.commit()


def update_missing_liters(session: Session, station: str = "ptt") -> None:
    """Fill :class:`FuelEntry.liters` for rows missing the value."""

    stmt = select(FuelEntry).where(
        cast(Any, FuelEntry.liters).is_(None),
        cast(Any, FuelEntry.amount_spent).is_not(None),
    )
    entries = session.exec(stmt).all()

    prices: dict[tuple[str, date], Optional[Decimal]] = {}

    for entry in entries:
        ftype = entry.fuel_type or "e20"
        key = (ftype, entry.entry_date)
        if key not in prices:
            prices[key] = get_price(session, ftype, station, entry.entry_date)
        price = prices[key]

        if price is None or entry.amount_spent is None:
            continue

        entry.liters = float(
            (Decimal(str(entry.amount_spent)) / price).quantize(Decimal("0.01"))
        )
        session.add(entry)
    session.commit()


def fetch_latest(
    session: Session,
    station: str = "ptt",
    api_base: Optional[str] = None,
) -> None:
    """ดึงและบันทึกราคาน้ำมันล่าสุดจาก Thai Oil API

    สามารถกำหนดฐาน URL ได้ผ่านพารามิเตอร์ ``api_base``
    หรือผ่านตัวแปรสภาพแวดล้อม ``OIL_API_BASE``
    """

    base = api_base or os.getenv("OIL_API_BASE", API_BASE)
    resp = _HTTP_SESSION.get(f"{base}/latest", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    thai_date = data["response"]["date"]
    day = _parse_thai_date(thai_date)
    stations = data["response"]["stations"]
    _parse_prices(stations, day, session)
    update_missing_liters(session, station)
    purge_old_prices(session)


def get_price(
    session: Session,
    fuel_type: str,
    station: str,
    day: date,
    fallback_days: int = DEFAULT_FALLBACK_DAYS,
) -> Optional[Decimal]:
    row = session.exec(
        select(cast(Any, FuelPrice.price)).where(
            FuelPrice.date == day,
            FuelPrice.station == station,
            FuelPrice.fuel_type == fuel_type,
        )
    ).first()

    if row is None and fallback_days:
        cutoff = day - timedelta(days=fallback_days)
        row = session.exec(
            select(cast(Any, FuelPrice.price))
            .where(
                FuelPrice.date < day,
                FuelPrice.date >= cutoff,
                FuelPrice.station == station,
                FuelPrice.fuel_type == fuel_type,
            )
            .order_by(cast(Any, FuelPrice.date).desc())
        ).first()

    if row is None:
        return None
    return Decimal(row)
