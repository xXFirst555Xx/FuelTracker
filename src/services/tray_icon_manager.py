"""Manage the application's system tray icon and menu."""

from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QWidget
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QObject


class TrayIconManager(QObject):
    """Handle creation and interaction of the system tray icon."""

    def __init__(
        self,
        parent: QWidget | None,
        show_action: Callable[[], None],
        add_entry_action: Callable[[], None],
        quit_action: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._show_action = show_action
        self._add_entry_action = add_entry_action
        self._quit_action = quit_action

        icon = QIcon("icons:home.svg")
        self.tray_icon = QSystemTrayIcon(icon, parent)

        menu = QMenu(parent)
        add_act = QAction("เพิ่มรายการใหม่", parent)
        add_act.triggered.connect(self._add_entry_action)
        menu.addAction(add_act)

        show_act = QAction("เปิดหน้าต่างหลัก", parent)
        show_act.triggered.connect(self._show_action)
        menu.addAction(show_act)

        quit_act = QAction("ออก", parent)
        quit_act.triggered.connect(self._quit_action)
        menu.addAction(quit_act)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_activated)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def show(self) -> None:
        self.tray_icon.show()

    def hide(self) -> None:
        self.tray_icon.hide()

    def is_visible(self) -> bool:
        return self.tray_icon.isVisible()

    def set_tooltip(self, text: str) -> None:
        self.tray_icon.setToolTip(text)

    def show_message(self, title: str, message: str, msecs: int = 10000) -> None:
        self.tray_icon.showMessage(
            title, message, QSystemTrayIcon.MessageIcon.NoIcon, msecs
        )

    # ------------------------------------------------------------------
    # Internal callbacks
    # ------------------------------------------------------------------
    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_action()
