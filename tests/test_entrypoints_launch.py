import subprocess
import sys
from importlib.metadata import entry_points

import pytest


def test_entrypoints_launch():
    eps = {ep.name for ep in entry_points(group="console_scripts")}
    if "fueltracker" not in eps:
        pytest.skip(
            "fueltracker entry point not found. Did you forget to `pip install -e .`?"
        )

    code = subprocess.check_output([sys.executable, "-m", "fueltracker", "--check"])
    assert "หน้าต่างหลักทำงานได้".encode() in code
