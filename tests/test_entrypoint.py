import tomllib
from pathlib import Path


def test_console_script() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text())
    assert data["project"]["scripts"]["fueltracker"] == "fueltracker.main:run"
