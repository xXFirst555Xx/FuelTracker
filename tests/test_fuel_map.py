from src.constants import FUEL_TYPE_TH


def test_fuel_type_map():
    assert FUEL_TYPE_TH["gasoline_95"] == "เบนซิน 95"
    assert "premium_diesel" in FUEL_TYPE_TH
