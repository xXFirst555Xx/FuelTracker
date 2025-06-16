from src.controllers.main_controller import MainController


def test_dock_buttons_exist(qapp, tmp_path):
    ctrl = MainController(db_path=tmp_path / "t.db")
    dock = ctrl.maint_dock
    assert dock.add_button.text()
    assert dock.edit_button.text()
    assert dock.done_button.text()
