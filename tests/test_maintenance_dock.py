def test_dock_buttons_exist(main_controller):
    ctrl = main_controller
    dock = ctrl.maint_dock
    assert dock.add_button.text()
    assert dock.edit_button.text()
    assert dock.done_button.text()
