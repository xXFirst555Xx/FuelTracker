"""Export utilities for generating monthly reports."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import logging

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

from ..models import FuelEntry
from .storage_service import StorageService

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting monthly reports."""

    def __init__(self, storage: StorageService) -> None:
        self.storage = storage
        self._tmpdirs: list[TemporaryDirectory[str]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def export_monthly_pdf(self, month: str, vehicle_id: int | None) -> Path:
        """Create a monthly PDF report and return the output path."""
        year, mon = (int(x) for x in month.split("-"))
        entries = self.storage.list_entries_for_month(year, mon, vehicle_id)
        df = self._entries_to_df(entries)
        tmp = TemporaryDirectory()
        self._tmpdirs.append(tmp)
        out_path = Path(tmp.name) / f"report_{month}.pdf"
        self._build_pdf(out_path, df, month, vehicle_id)
        return out_path

    def export_monthly_xlsx(self, month: str) -> Path:
        """Create a monthly Excel report and return the output path."""
        year, mon = (int(x) for x in month.split("-"))
        entries = self.storage.list_entries_for_month(year, mon)
        df = self._entries_to_df(entries)
        tmp = TemporaryDirectory()
        self._tmpdirs.append(tmp)
        out_path = Path(tmp.name) / f"report_{month}.xlsx"
        self._write_excel(out_path, df)
        return out_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _entries_to_df(self, entries: list[FuelEntry]) -> pd.DataFrame:
        data = []
        for e in entries:
            dist = None
            if e.odo_after is not None:
                dist = e.odo_after - e.odo_before
            data.append(
                {
                    "date": e.entry_date,
                    "fuel_type": e.fuel_type,
                    "odo_before": e.odo_before,
                    "odo_after": e.odo_after,
                    "distance": dist,
                    "liters": e.liters,
                    "amount_spent": e.amount_spent,
                }
            )
        df = pd.DataFrame(data)
        if not df.empty:
            df.sort_values("date", inplace=True)
        return df

    def _get_font(self) -> str:
        font_file = Path(__file__).resolve().parents[2] / "fonts" / "NotoSansThai-Regular.ttf"
        if not font_file.exists():
            url = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansthai/NotoSansThai-Regular.ttf"
            try:
                import requests

                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                font_file.parent.mkdir(parents=True, exist_ok=True)
                font_file.write_bytes(resp.content)
            except Exception as exc:  # pragma: no cover - network failure
                logger.warning("failed to download font: %s", exc)
                return "Helvetica"
        try:
            pdfmetrics.registerFont(TTFont("NotoSansThai", str(font_file), subsetting=True))
            return "NotoSansThai"
        except Exception as exc:  # pragma: no cover - bad font
            logger.warning("failed to register font: %s", exc)
            return "Helvetica"

    def _plot_dual_axis(self, df: pd.DataFrame, path: Path) -> None:
        if df.empty:
            fig, _ = plt.subplots()
            fig.savefig(path, format="png")
            plt.close(fig)
            return

        dates = df["date"].astype("datetime64[ns]")
        dist = df["distance"].fillna(0)
        amount = df["amount_spent"].fillna(0)

        fig, ax1 = plt.subplots()
        ax2: Axes = ax1.twinx()
        ax1.plot(dates, dist, color="tab:blue", marker="o", label="Distance (km)")
        ax2.plot(dates, amount, color="tab:red", marker="x", label="THB")
        ax1.set_ylabel("Distance (km)")
        ax2.set_ylabel("THB")
        ax1.set_xlabel("Date")
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(path, format="png")
        plt.close(fig)

    def _build_pdf(self, path: Path, df: pd.DataFrame, month: str, vehicle_id: int | None) -> None:
        font_name = self._get_font()
        chart = path.with_suffix(".png")
        try:
            self._plot_dual_axis(df, chart)
            canvas = Canvas(str(path), pagesize=A4)
            canvas.setFont(font_name, 16)
            title = f"รายงานประจำเดือน {month}"
            if vehicle_id is not None:
                title += f" ยานพาหนะ {vehicle_id}"
            canvas.drawString(40, 800, title)
            canvas.setFont(font_name, 12)
            y = 780
            for _, row in df.iterrows():
                line = (
                    f"{row['date']:%Y-%m-%d} "
                    f"{row['distance'] or ''} km "
                    f"{row['liters'] or ''} L "
                    f"{row['amount_spent'] or ''} THB"
                )
                canvas.drawString(40, y, line)
                y -= 18
                if y < 100:
                    canvas.showPage()
                    canvas.setFont(font_name, 12)
                    y = 800
            canvas.drawImage(ImageReader(str(chart)), 40, max(100, y - 260), width=500, preserveAspectRatio=True)
            canvas.save()
        finally:
            if chart.exists():
                chart.unlink()

    def _write_excel(self, path: Path, df: pd.DataFrame) -> None:
        with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, index=False)
