import tomllib
from pathlib import Path


def test_console_script() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text())
    scripts = data["project"]["scripts"]
    assert scripts["fueltracker"] == "fueltracker.main:run"
    assert scripts["fueltracker-launcher"] == "launcher:main"
