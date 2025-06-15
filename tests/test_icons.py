from src.controllers.main_controller import MainController


def test_sidebar_icons(qapp, tmp_path):
    controller = MainController(db_path=tmp_path / "db.sqlite")
    sidebar = controller.window.sidebarList
    assert sidebar.count() == 4
    for i in range(sidebar.count()):
        item = sidebar.item(i)
        assert not item.icon().isNull(), f"Icon missing for item {i}"
