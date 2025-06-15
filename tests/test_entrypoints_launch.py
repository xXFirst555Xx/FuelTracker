import subprocess
import sys
import pkg_resources


def test_entrypoints_launch():
    assert "fueltracker" in {
        ep.name for ep in pkg_resources.iter_entry_points("console_scripts")
    }
    code = subprocess.check_output([sys.executable, "-m", "fueltracker", "--check"])
    assert b"MainWindow OK" in code
