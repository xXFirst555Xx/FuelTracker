from types import SimpleNamespace

from src.hotkey import GlobalHotkey


def test_format_basic():
    gh = GlobalHotkey("Ctrl+Shift+N")
    assert gh._format(gh.sequence) == "ctrl+shift+n"


def test_start_stop(monkeypatch):
    calls = {"add": 0, "remove": 0}

    def fake_add_hotkey(seq: str, cb):
        calls["add"] += 1
        cb()

    def fake_remove_hotkey(seq: str):
        calls["remove"] += 1

    stub = SimpleNamespace(add_hotkey=fake_add_hotkey, remove_hotkey=fake_remove_hotkey)
    monkeypatch.setattr("src.hotkey.keyboard", stub)

    gh = GlobalHotkey("Ctrl+Shift+N")
    triggered = []
    gh.triggered.connect(lambda: triggered.append(True))
    gh.start()
    assert calls["add"] == 1
    assert triggered == [True]
    gh.stop()
    assert calls["remove"] == 1
