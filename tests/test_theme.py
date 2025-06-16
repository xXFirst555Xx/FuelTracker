import pytest
from PySide6.QtCore import Qt

from src.controllers import MainController
from src.config import AppConfig


def test_light_theme(qapp, tmp_path, monkeypatch):
    monkeypatch.delenv("FT_THEME", raising=False)
    qapp.setStyleSheet("")
    MainController(db_path=tmp_path / "t.db", dark_mode=False)
    assert "#FAFAFA" in qapp.styleSheet()


def test_dark_theme_flag(qapp, tmp_path, monkeypatch):
    monkeypatch.delenv("FT_THEME", raising=False)
    qapp.setStyleSheet("")
    MainController(db_path=tmp_path / "t.db", dark_mode=True)
    style = qapp.styleSheet()
    assert "#101010" in style or "#121212" in style


def test_modern_theme_env(qapp, tmp_path, monkeypatch):
    monkeypatch.setenv("FT_THEME", "modern")
    qapp.setStyleSheet("")
    MainController(db_path=tmp_path / "t.db")
    assert "#f5f7fa" in qapp.styleSheet()


def test_modern_theme_cli(qapp, tmp_path, monkeypatch):
    monkeypatch.delenv("FT_THEME", raising=False)
    monkeypatch.setattr(qapp, "arguments", lambda: ["prog", "--theme=modern"])
    qapp.setStyleSheet("")
    MainController(db_path=tmp_path / "t.db")
    assert "#f5f7fa" in qapp.styleSheet()


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
