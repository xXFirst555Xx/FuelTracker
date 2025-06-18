from types import SimpleNamespace

from src.hotkey import GlobalHotkey


def test_format_basic():
    gh = GlobalHotkey("Ctrl+Shift+N")
    assert gh._format(gh.sequence) == "ctrl+shift+n"


def test_start_stop(monkeypatch):
    calls: dict[str, int] = {
        "add": 0,
        "remove": 0,
        "listener_start": 0,
        "listener_stop": 0,
        "callback": 0,
    }

    def fake_add_hotkey(seq: str, cb) -> None:
        calls["add"] += 1
        cb()

    def fake_remove_hotkey(seq: str) -> None:
        calls["remove"] += 1

    class FakeListener:
        def __init__(self, mapping: dict[str, object]):
            self.mapping = mapping

        def start(self) -> None:
            calls["listener_start"] += 1
            for cb in self.mapping.values():
                cb()

        def stop(self) -> None:
            calls["listener_stop"] += 1

    stub = SimpleNamespace(
        add_hotkey=fake_add_hotkey,
        remove_hotkey=fake_remove_hotkey,
        GlobalHotKeys=lambda mapping: FakeListener(mapping),
    )
    monkeypatch.setattr("src.hotkey.keyboard", stub)

    original = GlobalHotkey._wrapped_callback

    def patched(self: GlobalHotkey) -> int:
        calls["callback"] += 1
        return original(self)

    monkeypatch.setattr(GlobalHotkey, "_wrapped_callback", patched)

    gh = GlobalHotkey("Ctrl+Shift+N")
    triggered: list[bool] = []
    gh.triggered.connect(lambda: triggered.append(True))
    gh.start()
    assert calls["listener_start"] == 1
    assert calls["callback"] == 1
    assert triggered == [True]
    gh.stop()
    assert calls["listener_stop"] == 1
