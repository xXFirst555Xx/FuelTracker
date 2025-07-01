from src.services import ThemeManager


def test_palette_changed_emitted(qtbot, qapp):
    manager = ThemeManager(qapp)
    with qtbot.waitSignal(manager.palette_changed, timeout=1000):
        qapp.paletteChanged.emit(qapp.palette())


def test_theme_to_file_mapping():
    assert ThemeManager._theme_to_file("light") == "light.qss"
    assert ThemeManager._theme_to_file("dark") == "dark.qss"
    assert ThemeManager._theme_to_file("modern") == "modern.qss"
    assert ThemeManager._theme_to_file("vivid") == "vivid.qss"
    assert ThemeManager._theme_to_file("unknown") is None


def test_apply_theme_invalid_does_nothing(qapp, monkeypatch):
    manager = ThemeManager(qapp)
    qapp.setStyleSheet("")
    monkeypatch.setattr(
        ThemeManager, "_theme_to_file", staticmethod(lambda _t: None)
    )
    manager.apply_theme("missing")
    assert qapp.styleSheet() == ""

