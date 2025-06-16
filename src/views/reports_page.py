from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget,
    QSplitter,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QGraphicsDropShadowEffect,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from ..services import ReportService


class SummaryCard(QWidget):
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
        self.setStyleSheet("background:white;border-radius:12px;padding:8px;")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        self.setGraphicsEffect(shadow)

    def set_value(self, text: str) -> None:
        self.value_label.setText(text)


class _Worker(QThread):
    data_ready = Signal(object, object, object, object, object)

    def __init__(self, service: ReportService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service

    def run(self) -> None:  # type: ignore[override]
        yearly = self._service.last_year_summary()
        pie = self._service.liters_by_type()
        monthly = self._service.monthly_summary()
        table = self._service._monthly_df(date.today(), 1)
        # Build charts
        fig1 = Figure(figsize=(4, 3))
        ax1 = fig1.add_subplot(111)
        if not yearly.empty:
            ax1.plot(yearly["month"].astype(str), yearly["km_per_l"], marker="o")
        ax1.set_ylabel("km/L")

        fig2 = Figure(figsize=(4, 3))
        ax2 = fig2.add_subplot(111)
        if not yearly.empty:
            ax2.bar(yearly["month"].astype(str), yearly["amount_spent"])
        ax2.set_ylabel("บาท")

        fig3 = Figure(figsize=(4, 3))
        ax3 = fig3.add_subplot(111)
        if not pie.empty:
            ax3.pie(pie, labels=pie.index)

        fig4 = Figure(figsize=(6, 4))
        ax4_1 = fig4.add_subplot(311)
        if not monthly.empty:
            ax4_1.bar(monthly["month"].astype(str), monthly["distance"])
        ax4_1.set_ylabel("km")

        ax4_2 = fig4.add_subplot(312)
        if not monthly.empty:
            ax4_2.bar(monthly["month"].astype(str), monthly["liters"])
        ax4_2.set_ylabel("L")

        ax4_3 = fig4.add_subplot(313)
        if not monthly.empty:
            ax4_3.plot(monthly["month"].astype(str), monthly["km_per_l"], marker="o")
        ax4_3.set_ylabel("km/L")
        fig4.tight_layout()

        self.data_ready.emit(fig1, fig2, fig3, fig4, table)


class ReportsPage(QWidget):
    refresh_requested = Signal()

    def __init__(self, service: ReportService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._worker: _Worker | None = None

        self.splitter = QSplitter(Qt.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.cards = {
            "distance": SummaryCard(self.tr("ระยะทางรวม")),
            "liters": SummaryCard(self.tr("ลิตรทั้งหมด")),
            "price": SummaryCard(self.tr("ค่าใช้จ่ายรวม")),
            "kmpl": SummaryCard(self.tr("กม./ลิตรเฉลี่ย")),
        }
        for card in self.cards.values():
            left_layout.addWidget(card)
        self.splitter.addWidget(left)

        self.tabs = QTabWidget()
        self.chart_container = QWidget()
        self.charts_layout = QVBoxLayout(self.chart_container)
        self.tabs.addTab(self.chart_container, self.tr("กราฟ"))
        self.table_container = QWidget()
        self.tabs.addTab(self.table_container, self.tr("ตาราง"))
        self.monthly_container = QWidget()
        self.monthly_layout = QVBoxLayout(self.monthly_container)
        self.tabs.addTab(self.monthly_container, self.tr("รายเดือน"))
        self.splitter.addWidget(self.tabs)

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        btn_layout = QHBoxLayout()
        self.export_button = QPushButton(self.tr("ส่งออก PDF/CSV"))
        self.refresh_button = QPushButton(self.tr("รีเฟรชข้อมูล"))
        btn_layout.addWidget(self.export_button)
        btn_layout.addWidget(self.refresh_button)
        layout.addLayout(btn_layout)

        self.refresh_button.clicked.connect(self.refresh)

    def refresh(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._worker = _Worker(self._service, self)
        self._worker.data_ready.connect(self._apply_data)
        self._worker.start()

    def _apply_data(self, fig1: Figure, fig2: Figure, fig3: Figure, fig4: Figure, table) -> None:
        for i in reversed(range(self.charts_layout.count())):
            item = self.charts_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        for fig in (fig1, fig2, fig3):
            canvas = FigureCanvasQTAgg(fig)
            self.charts_layout.addWidget(canvas)
        for i in reversed(range(self.monthly_layout.count())):
            item = self.monthly_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        canvas = FigureCanvasQTAgg(fig4)
        self.monthly_layout.addWidget(canvas)
        stats = self._service.calc_overall_stats()
        self.cards["distance"].set_value(f"{stats['total_distance']:.0f} km")
        self.cards["liters"].set_value(f"{stats['total_liters']:.0f} L")
        self.cards["price"].set_value(f"{stats['total_price']:.0f} ฿")
        self.cards["kmpl"].set_value(f"{stats['avg_consumption']:.2f}")
        self.refresh_requested.emit()
