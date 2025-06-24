import subprocess
import sys
from importlib.metadata import entry_points


def test_entrypoints_launch():
    assert "fueltracker" in {ep.name for ep in entry_points(group="console_scripts")}
    code = subprocess.check_output([sys.executable, "-m", "fueltracker", "--check"])
    assert "หน้าต่างหลักทำงานได้".encode() in code
