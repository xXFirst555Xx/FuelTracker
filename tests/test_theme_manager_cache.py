import io
from pathlib import Path

from src.services import ThemeManager


def test_theme_manager_reads_qss_once(qapp, tmp_path, monkeypatch):
    # Create a temporary QSS file
    qss_file = tmp_path / "temp.qss"
    qss_file.write_text("QWidget { color: red; }")

    # Force ThemeManager to load from our temporary file
    monkeypatch.setattr(
        ThemeManager,
        "_theme_to_file",
        staticmethod(lambda _t: str(qss_file)),
    )

    # Track how many times Path.open is called for the QSS path
    open_calls = []
    original_open = Path.open

    def fake_open(self, *args, **kwargs):
        if self == qss_file:
            open_calls.append(self)
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)

    manager = ThemeManager(qapp)

    # Apply the same theme multiple times
    manager.apply_theme("light")
    manager.apply_theme("light")

    # The QSS file should only be read once
    assert len(open_calls) == 1

