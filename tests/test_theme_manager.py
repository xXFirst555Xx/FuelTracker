from src.services import ThemeManager


def test_palette_changed_emitted(qtbot, qapp):
    manager = ThemeManager(qapp)
    with qtbot.waitSignal(manager.palette_changed, timeout=1000):
        qapp.paletteChanged.emit(qapp.palette())

