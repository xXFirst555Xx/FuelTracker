from src.controllers.main_controller import MainController

def test_switch_page_changes_index(qtbot, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
    window = ctrl.window
    qtbot.addWidget(window)
    stack = window.stackedWidget
    assert stack.currentIndex() == 0
    with qtbot.waitSignal(stack.currentChanged, timeout=2000):
        ctrl._switch_page(1)
    assert stack.currentIndex() == 1
