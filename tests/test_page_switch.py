def test_switch_page_changes_index(qtbot, main_controller):
    ctrl = main_controller
    window = ctrl.window
    qtbot.addWidget(window)
    stack = window.stackedWidget
    assert stack.currentIndex() == 0
    with qtbot.waitSignal(stack.currentChanged, timeout=2000):
        ctrl._switch_page(1)
    assert stack.currentIndex() == 1
