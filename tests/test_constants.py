import src.constants as const


def test_fuel_type_mapping_contains_keys():
    assert const.FUEL_TYPE_TH["gasoline_95"] == "เบนซิน 95"
    assert const.FUEL_TYPE_TH["ngv"] == "เอ็นจีวี"
