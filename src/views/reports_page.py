from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QSplitter,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QGraphicsDropShadowEffect,
    QComboBox,
    QTableView,
    QAbstractItemView,
    QHeaderView,
    QStandardItemModel,
    QStandardItem,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from typing import Callable, cast
import pandas as pd

from ..services import ReportService
from . import supports_shadow

FigureCanvas = cast(Callable[[Figure], QWidget], FigureCanvasQTAgg)


class SummaryCard(QWidget):
    """Small card widget displaying a single numeric value."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.title_label = QLabel(title)
        self.value_label = QLabel("-")
        font = self.title_label.font()
        font.setPointSize(14)
        self.title_label.setFont(font)
        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setStyleSheet(
            "background:#1E1E1E;border:1px solid #555555;"
            "border-radius:12px;padding:8px;"
        )
        if supports_shadow():
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(8)
            self.setGraphicsEffect(shadow)

    def set_value(self, text: str) -> None:
        self.value_label.setText(text)


class WeeklyReportTab(QWidget):
    """Tab showing weekly breakdown table and bar chart."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)
        layout.addWidget(self.table)
        layout.addWidget(self.chart_container)

    def update(self, df: pd.DataFrame, fig: Figure) -> None:  # type: ignore[override]
        model = QStandardItemModel(df.shape[0], df.shape[1])
        model.setHorizontalHeaderLabels(df.columns.tolist())
        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                model.setItem(r, c, QStandardItem(str(df.iat[r, c])))
        self.table.setModel(model)
        for i in reversed(range(self.chart_layout.count())):
            item = self.chart_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        canvas = FigureCanvas(fig)
        self.chart_layout.addWidget(canvas)


class _Worker(QThread):
    """Background worker to build figures and tables."""

    data_ready = Signal(object, object, object, object, object, object, object, object)

    def __init__(
        self,
        service: ReportService,
        vehicle_id: int | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._vehicle_id = vehicle_id

    def run(self) -> None:
        today = date.today()
        yearly = self._service.last_year_summary()
        pie = self._service.liters_by_type()
        monthly = self._service.monthly_summary()
        table = self._service._monthly_df(today, self._vehicle_id)

        # Weekly breakdown by ISO week
        weekly = self._weekly(table)

        # Chart for weekly liters
        week_fig = Figure(figsize=(4, 3))
        w_ax = week_fig.add_subplot(111)
        if not table.empty:
            order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            daily = (
                table.groupby("weekday")["liters"].sum().reindex(order, fill_value=0)
            )
            w_ax.bar(order, daily)
        w_ax.set_ylabel("ลิตร")

        month_fig = self._monthly_chart(monthly, self._vehicle_id)

        # Build charts
        fig1 = Figure(figsize=(4, 3))
        ax1 = fig1.add_subplot(111)
        if not yearly.empty:
            ax1.plot(yearly["month"].astype(str), yearly["km_per_l"], marker="o")
        ax1.set_ylabel("กม./ลิตร")

        fig2 = Figure(figsize=(4, 3))
        ax2 = fig2.add_subplot(111)
        if not yearly.empty:
            ax2.bar(yearly["month"].astype(str), yearly["amount_spent"])
        ax2.set_ylabel("บาท")

        fig3 = Figure(figsize=(4, 3))
        ax3 = fig3.add_subplot(111)
        if not pie.empty:
            ax3.pie(pie, labels=pie.index.tolist())

        self.data_ready.emit(
            fig1, fig2, fig3, month_fig, week_fig, table, weekly, today
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _weekly(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            cols = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            return pd.DataFrame(columns=cols, index=pd.Index([], name="week"))

        df = df.copy()
        df["week"] = df["date"].apply(
            lambda d: f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
        )
        pivot = df.pivot_table(
            index="week", columns="weekday", values="liters", aggfunc="sum"
        ).fillna(0)
        order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col in order:
            if col not in pivot.columns:
                pivot[col] = 0
        return pivot[order]

    def _monthly_chart(self, df: pd.DataFrame, vehicle_id: int | None) -> Figure:
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        if not df.empty:
            ax.bar(df["month"].astype(str), df["liters"], color="tab:blue", alpha=0.5)
        ax.set_ylabel("ลิตร")
        ax2 = ax.twinx()
        if vehicle_id is None:
            vehicles = self._service.storage.list_vehicles()
            for v in vehicles:
                entries = self._service.storage.get_entries_by_vehicle(v.id)
                data = []
                for e in entries:
                    if e.odo_after is None or e.liters is None:
                        continue
                    m = e.entry_date.strftime("%Y-%m")
                    data.append(
                        {
                            "month": m,
                            "dist": e.odo_after - e.odo_before,
                            "liters": e.liters,
                        }
                    )
                if not data:
                    continue
                vdf = pd.DataFrame(data)
                summ = vdf.groupby("month")[["dist", "liters"]].sum()
                summ["kml"] = summ["dist"] / summ["liters"]
                ax2.plot(summ.index.astype(str), summ["kml"], marker="o", label=v.name)
        else:
            if not df.empty:
                ax2.plot(
                    df["month"].astype(str),
                    df["km_per_l"],
                    color="orange",
                    marker="o",
                    label="km/L",
                )
        ax2.set_ylabel("กม./ลิตร")
        # Add legends only when something is labeled to avoid noisy warnings
        if ax.get_legend_handles_labels()[0]:
            ax.legend(loc="upper left")

        if ax2.get_legend_handles_labels()[0]:
            ax2.legend(loc="upper right")
        fig.tight_layout()
        return fig


class ReportsPage(QWidget):
    refresh_requested = Signal()

    def __init__(self, service: ReportService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._worker: _Worker | None = None
        self._current_vid: int | None = None
        self._last_ts = getattr(self._service.storage, "last_modified", None)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.cards = {
            "distance": SummaryCard(self.tr("ระยะทางเดือนนี้ (km)")),
            "fills": SummaryCard(self.tr("จำนวนครั้งเติม/เดือน")),
            "budget": SummaryCard(self.tr("งบคงเหลือ/เดือน")),
        }
        for card in self.cards.values():
            left_layout.addWidget(card)
        self.splitter.addWidget(left)

        self.tabs = QTabWidget()
        self.chart_container = QWidget()
        self.charts_layout = QVBoxLayout(self.chart_container)
        self.tabs.addTab(self.chart_container, self.tr("กราฟ"))
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_view = QTableView()
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_layout.addWidget(self.table_view)
        self.tabs.addTab(self.table_container, self.tr("ตาราง"))
        self.weekly_tab = WeeklyReportTab()
        self.tabs.addTab(self.weekly_tab, self.tr("รายสัปดาห์"))
        self.monthly_container = QWidget()
        self.monthly_layout = QVBoxLayout(self.monthly_container)
        self.tabs.addTab(self.monthly_container, self.tr("รายเดือน"))
        self.splitter.addWidget(self.tabs)

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        btn_layout = QHBoxLayout()
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.addItem(self.tr("(ทุกคัน)"), None)
        for v in self._service.storage.list_vehicles():
            self.vehicle_combo.addItem(v.name, v.id)
        btn_layout.addWidget(self.vehicle_combo)
        self.export_button = QPushButton(self.tr("ส่งออก PDF/CSV"))
        self.refresh_button = QPushButton(self.tr("รีเฟรชข้อมูล"))
        btn_layout.addWidget(self.export_button)
        btn_layout.addWidget(self.refresh_button)
        layout.addLayout(btn_layout)

        self.vehicle_combo.currentIndexChanged.connect(self.refresh)
        self.refresh_button.clicked.connect(self.refresh)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._check_updates)
        self._timer.start()

    def _check_updates(self) -> None:
        ts = getattr(self._service.storage, "last_modified", None)
        if ts != self._last_ts:
            self._last_ts = ts
            self.refresh()

    def refresh(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._current_vid = self.vehicle_combo.currentData()
        self._worker = _Worker(self._service, self._current_vid, self)
        self._worker.data_ready.connect(self._apply_data)

        def _cleanup() -> None:
            self._worker = None

        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.finished.connect(_cleanup)
        self._worker.start()

    def _apply_data(
        self,
        fig1: Figure,
        fig2: Figure,
        fig3: Figure,
        fig_month: Figure,
        fig_week: Figure,
        table: pd.DataFrame,
        weekly: pd.DataFrame,
        month: date,
    ) -> None:
        for i in reversed(range(self.charts_layout.count())):
            item = self.charts_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        for fig in (fig1, fig2, fig3):
            canvas = FigureCanvas(fig)
            self.charts_layout.addWidget(canvas)
        for i in reversed(range(self.monthly_layout.count())):
            item = self.monthly_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        canvas = FigureCanvas(fig_month)
        self.monthly_layout.addWidget(canvas)
        self.weekly_tab.update(weekly, fig_week)
        self._set_table(table)
        distance = float(table["distance"].fillna(0).sum()) if not table.empty else 0.0
        fills = len(table)
        budget_remain = self._budget_remaining(month, self._current_vid)
        self.cards["distance"].set_value(f"{distance:.0f} km")
        self.cards["fills"].set_value(str(fills))
        if budget_remain is None:
            self.cards["budget"].set_value("-")
        else:
            self.cards["budget"].set_value(f"{budget_remain:.0f} ฿")
        self.refresh_requested.emit()

    # ------------------------------------------------------------------
    # Helpers for UI updates
    # ------------------------------------------------------------------
    def _set_table(self, df: pd.DataFrame) -> None:
        model = QStandardItemModel(df.shape[0], df.shape[1])
        model.setHorizontalHeaderLabels(df.columns.tolist())
        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                model.setItem(r, c, QStandardItem(str(df.iat[r, c])))
        self.table_view.setModel(model)

    def _budget_remaining(self, month: date, vid: int | None) -> float | None:
        if vid is None:
            total_budget = 0.0
            has_budget = False
            for v in self._service.storage.list_vehicles():
                b = self._service.storage.get_budget(v.id)
                if b is not None:
                    total_budget += b
                    has_budget = True
            if not has_budget:
                return None
            spent = 0.0
            for v in self._service.storage.list_vehicles():
                spent += self._service.storage.get_total_spent(
                    v.id, month.year, month.month
                )
            return total_budget - spent
        budget = self._service.storage.get_budget(vid)
        if budget is None:
            return None
        spent = self._service.storage.get_total_spent(vid, month.year, month.month)
        return budget - spent
