import pytest
from PySide6.QtCore import Qt

from src.controllers import MainController
from src.config import AppConfig

@pytest.mark.parametrize(
    "env_theme, cli_arg, dark_flag, expected_colors",
    [
        (None, None, False, ["#FAFAFA"]),
        (None, None, True, ["#101010", "#121212"]),
        ("modern", None, None, ["#f5f7fa"]),
        (None, "--theme=modern", None, ["#f5f7fa"]),
        ("vivid", None, None, ["#FF9800"]),
    ],
)
def test_theme_colors(qapp, tmp_path, monkeypatch, env_theme, cli_arg, dark_flag, expected_colors):
    if env_theme is not None:
        monkeypatch.setenv("FT_THEME", env_theme)
    else:
        monkeypatch.delenv("FT_THEME", raising=False)

    if cli_arg is not None:
        monkeypatch.setattr(qapp, "arguments", lambda: ["prog", cli_arg])
    else:
        monkeypatch.setattr(qapp, "arguments", lambda: ["prog"])

    qapp.setStyleSheet("")
    MainController(db_path=tmp_path / "t.db", dark_mode=dark_flag)
    style = qapp.styleSheet()
    assert any(c in style for c in expected_colors)


def test_theme_persisted(qapp, tmp_path):
    cfg_path = tmp_path / "conf.json"
    AppConfig().save(cfg_path)

    ctrl = MainController(db_path=tmp_path / "t.db", config_path=cfg_path)
    ctrl._theme_changed("dark")

    loaded = AppConfig.load(cfg_path)
    assert loaded.theme == "dark"

    ctrl2 = MainController(db_path=tmp_path / "t2.db", config_path=cfg_path)
    assert ctrl2.config.theme == "dark"


@pytest.mark.parametrize(
    "scheme,expected_colors",
    [
        (Qt.ColorScheme.Light, ["#FAFAFA"]),
        (Qt.ColorScheme.Dark, ["#101010", "#121212"]),
    ],
)
def test_system_theme(qapp, tmp_path, monkeypatch, scheme, expected_colors):
    monkeypatch.delenv("FT_THEME", raising=False)

    class DummyHints:
        def colorScheme(self):
            return scheme

    monkeypatch.setattr(qapp, "styleHints", lambda: DummyHints())
    qapp.setStyleSheet("")

    ctrl = MainController(db_path=tmp_path / "t.db")
    ctrl._theme_changed("system")

    style = qapp.styleSheet()
    assert any(c in style for c in expected_colors)


def test_palette_signal_updates_stylesheet(qapp, tmp_path, monkeypatch):
    monkeypatch.delenv("FT_THEME", raising=False)
    orig_setup = MainController._setup_style
    calls: list[MainController] = []

    def wrapper(self: MainController) -> None:
        calls.append(self)
        orig_setup(self)

    monkeypatch.setattr(MainController, "_setup_style", wrapper)
    ctrl = MainController(db_path=tmp_path / "t.db")
    qapp.setStyleSheet("dummy")
    calls.clear()
    qapp.paletteChanged.emit(qapp.palette())
    assert ctrl in calls
    assert qapp.styleSheet() != "dummy"
