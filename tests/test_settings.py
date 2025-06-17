from pathlib import Path
from src.settings import Settings


def test_env_loading(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "my.db"))
    monkeypatch.setenv("FT_THEME", "modern")
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    settings = Settings()
    assert settings.db_path == tmp_path / "my.db"
    assert settings.ft_theme == "modern"
    assert settings.appdata == tmp_path / "appdata"
