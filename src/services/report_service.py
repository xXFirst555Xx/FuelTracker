"""บริการสร้างรายงานอย่างง่ายจากข้อมูลที่บันทึกไว้"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List

import pandas as pd
from fpdf import FPDF
import matplotlib

# Use a non-interactive backend for headless environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..models import FuelEntry, Vehicle
from .storage_service import StorageService
from ..constants import FUEL_TYPE_TH


class ReportService:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

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
        print("Generated report:")
        for key, value in stats.items():
            print(f"{key}: {value}")

    # ------------------------------------------------------------------
    # New functionality for exporting monthly reports
    # ------------------------------------------------------------------

    def _filter_entries(self, month: date, vehicle_id: int) -> List[FuelEntry]:
        """ดึงรายการของยานพาหนะในเดือนที่กำหนด"""
        return self.storage.list_entries_for_month(vehicle_id, month.year, month.month)

    def _monthly_df(self, month: date, vehicle_id: int) -> pd.DataFrame:
        """คืนค่า DataFrame ของรายการประจำเดือน"""
        entries = self._filter_entries(month, vehicle_id)
        vehicles: Dict[int, Vehicle] = {}
        data = []
        for e in entries:
            if e.vehicle_id not in vehicles:
                vehicles[e.vehicle_id] = self.storage.get_vehicle(e.vehicle_id)  # type: ignore[assignment]
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
            return pd.DataFrame(
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
                ]
            )

        df = pd.DataFrame(data)
        df.sort_values("date", inplace=True)
        return df

    def get_monthly_stats(self, month: date, vehicle_id: int) -> Dict[str, float]:
        """คำนวณผลรวมและค่าเฉลี่ยของเดือนสำหรับยานพาหนะ"""
        df = self._monthly_df(month, vehicle_id)
        if df.empty:
            return {
                "total_distance": 0.0,
                "total_liters": 0.0,
                "total_price": 0.0,
                "avg_consumption": 0.0,
                "cost_per_km": 0.0,
            }

        total_distance = float(df["distance"].fillna(0).sum())
        total_liters = float(df["liters"].fillna(0).sum())
        total_price = float(df["amount_spent"].sum())
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

    def export_csv(self, month: date, vehicle_id: int, path: Path) -> None:
        """ส่งออกรายการประจำเดือนเป็นไฟล์ CSV"""
        df = self._monthly_df(month, vehicle_id)
        df.to_csv(path, index=False)

    def export_pdf(self, month: date, vehicle_id: int, path: Path) -> None:
        """สร้างรายงาน PDF พร้อมกราฟอย่างง่าย"""
        df = self._monthly_df(month, vehicle_id)

        # Create a line chart showing distance and amount spent per day
        if not df.empty:
            fig, ax1 = plt.subplots()
            ax1.plot(df["date"], df["distance"], marker="o", label="Distance (km)")
            ax1.plot(df["date"], df["amount_spent"], marker="x", label="THB")
            ax1.set_xlabel("Date")
            ax1.legend()
            fig.tight_layout()
            chart_file = path.with_suffix(".png")
            fig.savefig(chart_file)
            plt.close(fig)
        else:
            chart_file = None

        stats = self.get_monthly_stats(month, vehicle_id)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        title = f"Fuel report {month.strftime('%Y-%m')} vehicle {vehicle_id}"
        pdf.cell(0, 10, title, ln=1)

        pdf.set_font("Helvetica", size=12)
        for key, value in stats.items():
            pdf.cell(0, 10, f"{key}: {value}", ln=1)

        if chart_file and chart_file.exists():
            pdf.image(str(chart_file), w=170)

        try:
            pdf.output(str(path))
        finally:
            if chart_file and chart_file.exists():
                chart_file.unlink()

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

    def last_year_summary(self) -> pd.DataFrame:
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

    def monthly_summary(self) -> pd.DataFrame:
        """คืนข้อมูลสรุปรวมต่อเดือนจากทุกข้อมูลที่มี"""
        rows = self.storage.monthly_totals()
        if not rows:
            return pd.DataFrame(columns=["month", "distance", "liters", "km_per_l"])

        df = pd.DataFrame(rows, columns=["month", "distance", "liters", "amount_spent"])
        df["month"] = pd.PeriodIndex(df["month"], freq="M")
        df = df[["month", "distance", "liters"]]
        df["km_per_l"] = df["distance"] / df["liters"]
        return df.reset_index(drop=True)

    def liters_by_type(self) -> pd.Series:
        """รวมปริมาณเชื้อเพลิงตามประเภท"""
        data = {
            FUEL_TYPE_TH.get(ft or "", ft or ""): liters
            for ft, liters in self.storage.liters_by_fuel_type().items()
        }
        return pd.Series(data)
