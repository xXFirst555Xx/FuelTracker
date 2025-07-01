from datetime import date
import pandas as pd
from PySide6.QtWidgets import QApplication
from src.views.reports_page import _Worker, ReportsPage
from src.services.report_service import ReportService
from src.models import Vehicle

class DummyStorage:
    def __init__(self):
        self.vehicles = []
        self.budgets = {}
        self.spent = {}
    def list_vehicles(self):
        return self.vehicles
    def get_budget(self, vid):
        return self.budgets.get(vid)
    def get_total_spent(self, vid, year, month):
        return self.spent.get((vid, year, month), 0.0)

class DummyService(ReportService):
    def __init__(self):
        self.storage = DummyStorage()


def test_weekly_pivot():
    df = pd.DataFrame({
        'date': [date(2024, 5, 1), date(2024, 5, 2)],
        'weekday': ['Wed', 'Thu'],
        'liters': [5, 10],
    })
    result = _Worker._weekly(df)
    week = f"{date(2024,5,1).isocalendar().year}-W{date(2024,5,1).isocalendar().week:02d}"
    assert week in result.index
    assert result.loc[week, 'Wed'] == 5
    assert result.loc[week, 'Thu'] == 10


def test_weekly_empty():
    df = pd.DataFrame(columns=['date','weekday','liters'])
    result = _Worker._weekly(df)
    assert result.empty
    assert list(result.columns) == ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']


def test_budget_remaining_specific(qtbot):
    service = DummyService()
    service.storage.vehicles = [Vehicle(id=1, name='v1', vehicle_type='t', license_plate='x', tank_capacity_liters=1)]
    service.storage.budgets[1] = 100.0
    service.storage.spent[(1,2024,5)] = 60.0
    page = ReportsPage(service)
    qtbot.addWidget(page)
    remain = page._budget_remaining(date(2024,5,1), 1)
    assert remain == 40.0


def test_budget_remaining_all(qtbot):
    service = DummyService()
    service.storage.vehicles = [
        Vehicle(id=1, name='v1', vehicle_type='t', license_plate='x', tank_capacity_liters=1),
        Vehicle(id=2, name='v2', vehicle_type='t', license_plate='y', tank_capacity_liters=1)
    ]
    service.storage.budgets = {1:100.0, 2:200.0}
    service.storage.spent = {(1,2024,5):80.0, (2,2024,5):20.0}
    page = ReportsPage(service)
    qtbot.addWidget(page)
    remain = page._budget_remaining(date(2024,5,1), None)
    assert remain == 200.0
