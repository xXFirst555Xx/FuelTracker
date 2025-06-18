#!/usr/bin/env python
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)


@dataclass
class Task:
    cmd: list[str]
    log_name: str
    label: str
    capture: bool = True
    env: dict[str, str] | None = None

    def execute(self) -> subprocess.CompletedProcess[str]:
        result = run(self.cmd, capture=self.capture, env=self.env)
        (REPORTS / self.log_name).write_text(
            (result.stdout or "") + (result.stderr or "")
        )
        return result


def run(
    cmd: list[str], *, capture: bool = True, env: dict[str, str] | None = None, **kwargs
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* and optionally capture output.

    Parameters
    ----------
    cmd: list[str]
        Command and arguments to run.
    capture: bool, optional
        Capture stdout/stderr if ``True`` (default) or inherit the current
        process streams if ``False``.
    """

    print("$", " ".join(cmd))
    if capture:
        return subprocess.run(cmd, text=True, capture_output=True, env=env, **kwargs)
    return subprocess.run(cmd, text=True, env=env, **kwargs)


def main() -> None:
    summary: list[str] = []
    errors: list[str] = []

    install_tasks = [
        Task(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            "install.log",
            "pip install",
        ),
        Task(
            [sys.executable, "-m", "pip", "install", "alembic"],
            "alembic_install.log",
            "alembic install",
        ),
    ]

    for task in install_tasks:
        res = task.execute()
        if res.returncode != 0:
            errors.append(task.label)

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

    # 3. Static analysis in parallel
    static_tasks = [
        Task(
            ["ruff", "check", ".", "--select", "F401,F403,F841,PLC0414", "--statistics"],
            "ruff.txt",
            "ruff",
        ),
        Task(["vulture", "src/"], "vulture.txt", "vulture"),
        Task(["mypy", "src/", "--strict"], "mypy.txt", "mypy"),
    ]

    with ThreadPoolExecutor() as ex:
        futures = {ex.submit(t.execute): t for t in static_tasks}
        for future in as_completed(futures):
            task = futures[future]
            res = future.result()
            summary.append(f"{task.label} exit: {res.returncode}")
            if task.label == "vulture":
                for line in res.stdout.splitlines():
                    if line.strip().startswith("Confidence"):
                        break
            if res.returncode != 0:
                errors.append(task.label)

    # Apply database migrations
    migrate_task = Task(
        [sys.executable, "-m", "fueltracker", "migrate"],
        "migrate.log",
        "migrate",
    )
    res = migrate_task.execute()
    if res.returncode != 0:
        errors.append(migrate_task.label)

    # 5. Pytest
    pytest_task = Task(["pytest", "-q"], "pytest.txt", "pytest", capture=False)
    res = pytest_task.execute()
    summary.append("Pytest exit: " + str(res.returncode))
    if res.returncode != 0:
        errors.append(pytest_task.label)

    # 6. Runtime check
    runtime_task = Task(
        [sys.executable, "-m", "fueltracker", "--check"],
        "runtime.txt",
        "runtime",
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )
    res = runtime_task.execute()
    summary.append(res.stdout.strip())
    if b"MainWindow OK" not in res.stdout.encode():
        errors.append(runtime_task.label)

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
