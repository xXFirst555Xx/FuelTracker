#!/usr/bin/env python
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(cmd))
    return subprocess.run(cmd, text=True, capture_output=True, **kwargs)


def main() -> None:
    summary = []
    errors = []

    # 1. Editable install
    res = run([sys.executable, "-m", "pip", "install", "-e", "."])
    (REPORTS / "install.log").write_text(res.stdout + res.stderr)
    if res.returncode != 0:
        errors.append("pip install")

    # Install alembic for migrations
    res = run([sys.executable, "-m", "pip", "install", "alembic"])
    (REPORTS / "alembic_install.log").write_text(res.stdout + res.stderr)
    if res.returncode != 0:
        errors.append("alembic install")

    # 2. Import graph
    res = run(
        [
            "pydeps",
            "src/fueltracker/__init__.py",
            "--noshow",
            "--show-cycles",
            "--show-deps",
            "-o",
            str(REPORTS / "import_graph.svg"),
        ]
    )
    cycles_data = res.stdout.strip()
    cycles = len(json.loads(cycles_data or "{}")) if cycles_data else 0
    summary.append(f"Import cycles: {cycles}")
    if cycles > 0:
        errors.append("import cycles")

    # 3. Ruff
    res = run(
        ["ruff", "check", ".", "--select", "F401,F403,F841,PLC0414", "--statistics"]
    )
    (REPORTS / "ruff.txt").write_text(res.stdout + res.stderr)
    summary.append("Ruff exit: " + str(res.returncode))
    if res.returncode != 0:
        errors.append("ruff")

    # Dead code
    res = run(["vulture", "src/"])
    (REPORTS / "vulture.txt").write_text(res.stdout + res.stderr)
    for line in res.stdout.splitlines():
        if line.strip().startswith("Confidence"):
            break
    summary.append(f"Vulture exit: {res.returncode}")
    if res.returncode != 0:
        errors.append("vulture")

    # 4. Mypy
    res = run(["mypy", "src/", "--strict"])
    (REPORTS / "mypy.txt").write_text(res.stdout + res.stderr)
    summary.append("Mypy exit: " + str(res.returncode))
    if res.returncode != 0:
        errors.append("mypy")

    # Apply database migrations
    res = run([sys.executable, "-m", "fueltracker", "migrate"])
    (REPORTS / "migrate.log").write_text(res.stdout + res.stderr)
    if res.returncode != 0:
        errors.append("migrate")

    # 5. Pytest
    res = run(["pytest", "-q"])
    (REPORTS / "pytest.txt").write_text(res.stdout + res.stderr)
    summary.append("Pytest exit: " + str(res.returncode))
    if res.returncode != 0:
        errors.append("pytest")

    # 6. Runtime check
    res = run(
        [sys.executable, "-m", "fueltracker", "--check"],
        env={**dict(**os.environ), "QT_QPA_PLATFORM": "offscreen"},
    )
    (REPORTS / "runtime.txt").write_text(res.stdout + res.stderr)
    summary.append(res.stdout.strip())
    if b"MainWindow OK" not in res.stdout.encode():
        errors.append("runtime")

    # Write summary
    report = REPORTS / "connectivity_report.md"
    with report.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(summary) + "\n")
        if errors:
            fh.write("Errors: " + ", ".join(errors) + "\n")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
