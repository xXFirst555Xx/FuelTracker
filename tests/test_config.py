from src.config import AppConfig


def test_config_roundtrip(tmp_path):
    path = tmp_path / "conf.json"
    cfg = AppConfig(default_station="bcp", update_hours=12)
    cfg.save(path)
    loaded = AppConfig.load(path)
    assert loaded.default_station == "bcp"
    assert loaded.update_hours == 12
