"""บริการสร้างรายงานอย่างง่ายจากข้อมูลที่บันทึกไว้"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List

from pandas import DataFrame, Series

import pandas as pd
from fpdf import FPDF
import matplotlib
from matplotlib import font_manager
from typing import Any, Callable, cast
from io import BytesIO
import logging

# Use a non-interactive backend for headless environments
matplotlib.use("Agg")
fm = cast(Any, font_manager.fontManager)
if any(f.name == "Noto Sans Thai" for f in fm.ttflist):
    matplotlib.rcParams["font.family"] = "Noto Sans Thai"
else:
    matplotlib.rcParams["font.family"] = "Tahoma"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import dates as mdates  # noqa: E402

from ..models import FuelEntry, Vehicle  # noqa: E402
from .storage_service import StorageService  # noqa: E402
from ..constants import FUEL_TYPE_TH  # noqa: E402

logger = logging.getLogger(__name__)

date2num = cast(Callable[[date], float], mdates.date2num)


class ReportService:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage
        self._monthly_cache: dict[tuple[str, int | None], DataFrame] = {}
        self._monthly_cache_ts: float | None = None

    def calc_overall_stats(self) -> Dict[str, float]:
        total_distance, total_liters, total_price = self.storage.get_overall_totals()

        avg_consumption = (
            (total_liters / total_distance * 100) if total_distance else 0.0
        )
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
        logger.info("สร้างรายงานแล้ว:")
        for key, value in stats.items():
            logger.info("%s: %s", key, value)

    # ------------------------------------------------------------------
    # New functionality for exporting monthly reports
    # ------------------------------------------------------------------

    def _filter_entries(self, month: date, vehicle_id: int | None) -> List[FuelEntry]:
        """ดึงรายการของยานพาหนะในเดือนที่กำหนด"""
        return self.storage.list_entries_for_month(month.year, month.month, vehicle_id)

    # FIX: mypy clean
    def _monthly_df(self, month: date, vehicle_id: int | None) -> DataFrame:
        """Return monthly entries as a :class:`pandas.DataFrame`."""
        key = (month.strftime("%Y-%m"), vehicle_id)
        ts = getattr(self.storage, "last_modified", None)
        if key in self._monthly_cache and self._monthly_cache_ts == ts:
            return self._monthly_cache[key].copy()

        entries = self._filter_entries(month, vehicle_id)
        vehicles: Dict[int, Vehicle | None] = {}
        data = []
        for e in entries:
            if e.vehicle_id not in vehicles:
                vehicle = self.storage.get_vehicle(e.vehicle_id)
                vehicles[e.vehicle_id] = vehicle
            v = vehicles[e.vehicle_id]
            dist = None if e.odo_after is None else e.odo_after - e.odo_before
            kmpl = dist / e.liters if dist and e.liters else None
            cpk = e.amount_spent / dist if dist and e.amount_spent else None
            data.append(
                {
                    "date": e.entry_date,
                    "vehicle": v.name if v else "",
                    "vehicle_type": v.vehicle_type if v else "",
                    "fuel_type": FUEL_TYPE_TH.get(e.fuel_type or "", e.fuel_type or ""),
                    "distance": dist,
                    "liters": e.liters,
                    "amount_spent": e.amount_spent,
                    "km_per_l": kmpl,
                    "thb_per_km": cpk,
                }
            )

        if not data:
            df = pd.DataFrame(
                columns=[
                    "date",
                    "vehicle",
                    "vehicle_type",
                    "fuel_type",
                    "distance",
                    "liters",
                    "amount_spent",
                    "km_per_l",
                    "thb_per_km",
                    "weekday",
                ]
            )
            self._monthly_cache[key] = df
            self._monthly_cache_ts = ts
            return df.copy()

        df = pd.DataFrame(data)
        df.sort_values("date", inplace=True)
        df["weekday"] = pd.to_datetime(df["date"]).dt.day_name().str[:3]
        self._monthly_cache[key] = df
        self._monthly_cache_ts = ts
        return df.copy()

    def get_monthly_stats(self, month: date, vehicle_id: int) -> Dict[str, float]:
        """คำนวณผลรวมและค่าเฉลี่ยของเดือนสำหรับยานพาหนะ"""
        total_distance, total_liters, total_price = self.storage.vehicle_monthly_stats(
            vehicle_id, month.year, month.month
        )
        fills_count = len(
            self.storage.list_entries_for_month(month.year, month.month, vehicle_id)
        )

        avg_consumption = (
            (total_liters / total_distance * 100) if total_distance else 0.0
        )
        cost_per_km = (total_price / total_distance) if total_distance else 0.0
        avg_price_per_liter = (total_price / total_liters) if total_liters else 0.0

        return {
            "total_distance": total_distance,
            "total_liters": total_liters,
            "total_price": total_price,
            "avg_consumption": avg_consumption,
            "cost_per_km": cost_per_km,
            "fills_count": fills_count,
            "avg_price_per_liter": avg_price_per_liter,
        }

    def export_csv(self, month: date, vehicle_id: int, path: Path) -> None:
        """ส่งออกรายการประจำเดือนเป็นไฟล์ CSV"""
        df = self._monthly_df(month, vehicle_id)
        df.to_csv(path, index=False)

    def export_pdf(self, month: date, vehicle_id: int, path: Path) -> None:
        """สร้างรายงาน PDF พร้อมกราฟอย่างง่าย"""
        df = self._monthly_df(month, vehicle_id)

        # FIX: mypy clean
        # Create a line chart showing distance and amount spent per day
        if not df.empty:
            dates_num: list[float] = [date2num(d) for d in df["date"]]
            distances: list[float] = df["distance"].astype(float).tolist()
            amounts: list[float] = df["amount_spent"].astype(float).tolist()
            fig, ax1 = plt.subplots()
            ax1.plot(dates_num, distances, marker="o", label="Distance (km)")
            ax1.plot(dates_num, amounts, marker="x", label="THB")
            ax1.set_xlabel("Date")
            ax1.legend()
            fig.tight_layout()
            chart_buffer = BytesIO()
            fig.savefig(chart_buffer, format="png")
            chart_buffer.seek(0)
            plt.close(fig)
        else:
            chart_buffer = None

        stats = self.get_monthly_stats(month, vehicle_id)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        title = f"Fuel report {month.strftime('%Y-%m')}"
        if vehicle_id is not None:
            vehicle = self.storage.get_vehicle(vehicle_id)
            if vehicle is not None:
                title += f" - {vehicle.name}"
            else:
                title += f" - ID {vehicle_id}"
        pdf.cell(0, 10, title, ln=1)

        pdf.set_font("Helvetica", size=12)
        for key, value in stats.items():
            pdf.cell(0, 10, f"{key}: {value}", ln=1)

        if chart_buffer:
            pdf.image(chart_buffer, w=170)

        pdf.output(str(path))

    def export_excel(self, month: date, vehicle_id: int, path: Path) -> None:
        """ส่งออกรายการประจำเดือนเป็นไฟล์ Excel พร้อมสรุปข้อมูล"""
        df = self._monthly_df(month, vehicle_id)
        stats = self.get_monthly_stats(month, vehicle_id)
        with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, index=False, sheet_name="entries")
            pd.DataFrame([stats]).to_excel(writer, index=False, sheet_name="summary")

    # ------------------------------------------------------------------
    # Data helpers for UI charts
    # ------------------------------------------------------------------

    # FIX: mypy clean
    def last_year_summary(self) -> DataFrame:
        """คืนข้อมูลสรุปรวมของ 12 เดือนล่าสุด"""
        rows = self.storage.monthly_totals()
        if not rows:
            return pd.DataFrame(
                columns=["month", "distance", "liters", "amount_spent", "km_per_l"]
            )

        df = pd.DataFrame(rows, columns=["month", "distance", "liters", "amount_spent"])
        df["month"] = pd.PeriodIndex(df["month"], freq="M")
        df["km_per_l"] = df["distance"] / df["liters"]
        return df.tail(12).reset_index(drop=True)

    # FIX: mypy clean
    def monthly_summary(self) -> DataFrame:
        """คืนข้อมูลสรุปรวมต่อเดือนจากทุกข้อมูลที่มี"""
        rows = self.storage.monthly_totals()
        if not rows:
            return pd.DataFrame(columns=["month", "distance", "liters", "km_per_l"])

        df = pd.DataFrame(rows, columns=["month", "distance", "liters", "amount_spent"])
        df["month"] = pd.PeriodIndex(df["month"], freq="M")
        df = df[["month", "distance", "liters"]]
        df["km_per_l"] = df["distance"] / df["liters"]
        return df.reset_index(drop=True)

    # FIX: mypy clean
    def liters_by_type(self) -> Series[float]:
        """รวมปริมาณเชื้อเพลิงตามประเภท"""
        data = {
            FUEL_TYPE_TH.get(ft or "", ft or ""): liters
            for ft, liters in self.storage.liters_by_fuel_type().items()
        }
        return pd.Series(data)

