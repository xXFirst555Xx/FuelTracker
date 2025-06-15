from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional

import requests
from sqlmodel import Session, select

from ..models import FuelPrice

API_BASE = "https://api.chnwt.dev/thai-oil-api"


def _parse_prices(data: Dict[str, Any], day: date, session: Session) -> None:
    for station, fuels in data.items():
        if station == "date":
            continue
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
                    name_th=str(info.get("name_th", "")),
                    price=price,
                )
            )
    session.commit()


def fetch_latest(session: Session, station: str = "ptt") -> None:
    resp = requests.get(f"{API_BASE}/latest")
    resp.raise_for_status()
    data = resp.json()
    day = date.fromisoformat(data["date"])
    _parse_prices(data, day, session)


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
