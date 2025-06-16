from src.config import AppConfig


def test_config_roundtrip(tmp_path):
    path = tmp_path / "conf.json"
    cfg = AppConfig(
        default_station="bcp",
        update_hours=12,
        theme="modern",
        hide_on_close=False,
        global_hotkey_enabled=False,
        hotkey="Ctrl+Shift+N",
    )
    cfg.save(path)
    loaded = AppConfig.load(path)
    assert loaded.default_station == "bcp"
    assert loaded.update_hours == 12
    assert loaded.theme == "modern"
    assert loaded.hide_on_close is False
    assert loaded.global_hotkey_enabled is False
    assert loaded.hotkey == "Ctrl+Shift+N"
