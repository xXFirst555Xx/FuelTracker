from PySide6.QtWidgets import QSystemTrayIcon

from src.services.tray_icon_manager import TrayIconManager


def _manager(qapp):
    show_called = []
    tim = TrayIconManager(
        None, lambda: show_called.append(True), lambda: None, lambda: None
    )
    return tim, show_called


def test_show_hide_and_tooltip(qapp):
    tim, _ = _manager(qapp)
    assert not tim.is_visible()
    tim.show()
    assert tim.is_visible()
    tim.set_tooltip("hello")
    assert tim.tray_icon.toolTip() == "hello"
    tim.hide()
    assert not tim.is_visible()


def test_show_message(qapp, monkeypatch):
    tim, _ = _manager(qapp)
    captured = {}

    def fake_show_message(title, message, icon, msecs):
        captured["title"] = title
        captured["message"] = message
        captured["icon"] = icon
        captured["msecs"] = msecs

    monkeypatch.setattr(tim.tray_icon, "showMessage", fake_show_message)
    tim.show_message("Title", "Body", msecs=500)
    assert captured == {
        "title": "Title",
        "message": "Body",
        "icon": QSystemTrayIcon.MessageIcon.NoIcon,
        "msecs": 500,
    }


def test_activation_triggers_show_action(qapp):
    tim, show_called = _manager(qapp)
    tim.tray_icon.activated.emit(QSystemTrayIcon.ActivationReason.Trigger)
    assert show_called
