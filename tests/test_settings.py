from src.settings import Settings


def test_env_loading(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "my.db"))
    monkeypatch.setenv("FT_THEME", "modern")
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    settings = Settings()
    assert settings.db_path == tmp_path / "my.db"
    assert settings.ft_theme == "modern"
    assert settings.appdata == tmp_path / "appdata"


def test_default_db_location(monkeypatch, tmp_path):
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.setattr(
        "src.settings.user_data_dir",
        lambda *_args, **_kwargs: str(tmp_path / "data"),
    )
    settings = Settings()
    assert settings.db_path == tmp_path / "data" / "fuel.db"
