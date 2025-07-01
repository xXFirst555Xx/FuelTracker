import json
from pathlib import Path
from runpy import run_path

import requests


def test_print_latest_oil_prices(monkeypatch, capsys):
    sample = {"status": "ok", "data": {"key": "value"}}

    class DummyResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self):
            return sample

    def fake_get(url: str, timeout: int | None = None):
        _ = timeout  # avoid unused variable warning
        assert url.endswith("thai-oil-api/latest")
        return DummyResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    globs = run_path(Path("scripts/print_latest_oil_prices.py"), run_name="not_main")
    globs["main"]()

    out = capsys.readouterr().out.strip()
    assert json.loads(out) == sample
