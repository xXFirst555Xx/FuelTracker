import subprocess, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
qrc = root / "resources.qrc"
out = root / "resources_rc.py"
subprocess.check_call(["pyside6-rcc", str(qrc), "-o", str(out)])
