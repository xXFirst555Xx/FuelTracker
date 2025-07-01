def test_toggle_sync(main_controller):
    ctrl = main_controller
    assert ctrl.sync_enabled is False
    ctrl._toggle_sync(True)
    assert ctrl.sync_enabled is True
    ctrl._toggle_sync(False)
    assert ctrl.sync_enabled is False

