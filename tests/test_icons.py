def test_sidebar_icons(main_controller):
    controller = main_controller
    sidebar = controller.window.sidebarList
    assert sidebar.count() == 4
    for i in range(sidebar.count()):
        item = sidebar.item(i)
        assert not item.icon().isNull(), f"Icon missing for item {i}"
