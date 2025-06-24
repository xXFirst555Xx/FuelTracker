from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ["ToastNotifier"]

# #############################################################################
# ########## Libraries #############
# ##################################
# standard library
import logging
import threading
from typing import Optional
from os import path
from time import sleep
from pathlib import Path

# 3rd party modules
from win32api import GetModuleHandle
from win32api import PostQuitMessage
from win32con import CW_USEDEFAULT
from win32con import IDI_APPLICATION
from win32con import IMAGE_ICON
from win32con import LR_DEFAULTSIZE
from win32con import LR_LOADFROMFILE
from win32con import WM_DESTROY
from win32con import WM_USER
from win32con import WS_OVERLAPPED
from win32con import WS_SYSMENU
from win32gui import CreateWindow
from win32gui import DestroyWindow
from win32gui import LoadIcon
from win32gui import LoadImage
from win32gui import NIF_ICON
from win32gui import NIF_INFO
from win32gui import NIF_MESSAGE
from win32gui import NIF_TIP
from win32gui import NIM_ADD
from win32gui import NIM_DELETE
from win32gui import NIM_MODIFY
from win32gui import RegisterClass
from win32gui import UnregisterClass
from win32gui import Shell_NotifyIcon
from win32gui import UpdateWindow
from win32gui import WNDCLASS

# ############################################################################
# ########### Classes ##############
# ##################################


class ToastNotifier(object):
    """Create a Windows 10  toast notification.

    from: https://github.com/jithurjacob/Windows-10-Toast-Notifications
    """

    def __init__(self) -> None:
        """Initialize."""
        self._thread: Optional[threading.Thread] = None

    def _show_toast(
        self,
        title: str,
        msg: str,
        icon_path: str | None,
        duration: int,
    ) -> None:
        """Notification settings.

        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction
        """
        message_map = {
            WM_DESTROY: self.on_destroy,
        }

        # Register the window class.
        self.wc = WNDCLASS()
        self.hinst = self.wc.hInstance = GetModuleHandle(None)
        self.wc.lpszClassName = str("PythonTaskbar")  # must be a string
        self.wc.lpfnWndProc = message_map  # could also specify a wndproc.
        try:
            self.classAtom = RegisterClass(self.wc)
        except Exception as exc:
            # RegisterClass can fail if the class is already registered.
            logging.debug("RegisterClass failed: %s", exc)
            self.classAtom = self.wc.lpszClassName
        style = WS_OVERLAPPED | WS_SYSMENU
        self.hwnd = CreateWindow(
            self.classAtom,
            "Taskbar",
            style,
            0,
            0,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            0,
            0,
            self.hinst,
            None,
        )
        UpdateWindow(self.hwnd)

        # icon
        if icon_path is not None:
            icon_path = path.realpath(icon_path)
        else:
            icon_path = str(Path(__file__).resolve().parent / "data" / "python.ico")
        icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
        try:
            hicon = LoadImage(self.hinst, icon_path, IMAGE_ICON, 0, 0, icon_flags)
        except Exception as e:
            logging.error("Some trouble with the icon ({}): {}".format(icon_path, e))
            hicon = LoadIcon(0, IDI_APPLICATION)

        # Taskbar icon
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, WM_USER + 20, hicon, "Tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(
            NIM_MODIFY,
            (
                self.hwnd,
                0,
                NIF_INFO,
                WM_USER + 20,
                hicon,
                "Balloon Tooltip",
                msg,
                200,
                title,
            ),
        )
        # take a rest then destroy
        sleep(duration)
        DestroyWindow(self.hwnd)
        UnregisterClass(self.wc.lpszClassName, None)
        return None

    def show_toast(
        self,
        title: str = "Notification",
        msg: str = "Here comes the message",
        icon_path: str | None = None,
        duration: int = 5,
        threaded: bool = False,
    ) -> bool | threading.Thread:
        """Notification settings.

        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction
        """
        if not threaded:
            self._show_toast(title, msg, icon_path, duration)
            return True

        if self.notification_active():
            # We have an active notification, let it finish so we don't spam them
            return False

        t = threading.Thread(
            target=self._show_toast,
            args=(title, msg, icon_path, duration),
        )
        self._thread = t
        t.start()
        return t

    def notification_active(self) -> bool:
        """See if we have an active notification showing"""
        if self._thread is not None and self._thread.is_alive():
            # We have an active notification, let is finish we don't spam them
            return True
        return False

    def on_destroy(
        self,
        hwnd: int,
        msg: int,
        wparam: int,
        lparam: int,
    ) -> int:
        """Clean after notification ended.

        :hwnd:
        :msg:
        :wparam:
        :lparam:
        """
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)

        return 0
