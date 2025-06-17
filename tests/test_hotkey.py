from src.hotkey import GlobalHotkey


def test_format_basic():
    gh = GlobalHotkey("Ctrl+Shift+N")
    assert gh._format(gh.sequence) == "<ctrl>+<shift>+n"
