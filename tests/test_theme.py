from src.controllers import MainController


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
