import sys
import types
import threading


def test_no_wparam_crash(monkeypatch):
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    # Stub win32api module
    win32api = types.SimpleNamespace(
        GetModuleHandle=lambda arg=None: 1,
        PostQuitMessage=lambda code=0: None,
    )
    # Stub win32con constants
    win32con = types.SimpleNamespace(
        CW_USEDEFAULT=0,
        IDI_APPLICATION=0,
        IMAGE_ICON=0,
        LR_DEFAULTSIZE=0,
        LR_LOADFROMFILE=0,
        WM_DESTROY=2,
        WM_USER=1024,
        WS_OVERLAPPED=0,
        WS_SYSMENU=0,
    )

    class _WNDCLASS:
        def __init__(self):
            self.hInstance = None
            self.lpszClassName = ""
            self.lpfnWndProc = None

    win32gui = types.SimpleNamespace(
        CreateWindow=lambda *a, **k: 1,
        DestroyWindow=lambda *a, **k: None,
        LoadIcon=lambda *a, **k: 1,
        LoadImage=lambda *a, **k: 1,
        NIF_ICON=0,
        NIF_INFO=0,
        NIF_MESSAGE=0,
        NIF_TIP=0,
        NIM_ADD=0,
        NIM_DELETE=0,
        NIM_MODIFY=0,
        RegisterClass=lambda wc: 1,
        UnregisterClass=lambda *a, **k: None,
        Shell_NotifyIcon=lambda *a, **k: None,
        UpdateWindow=lambda *a, **k: None,
        WNDCLASS=_WNDCLASS,
    )

    monkeypatch.setitem(sys.modules, "win32api", win32api)
    monkeypatch.setitem(sys.modules, "win32con", win32con)
    monkeypatch.setitem(sys.modules, "win32gui", win32gui)

    stub_pkg_resources = types.SimpleNamespace(
        resource_filename=lambda *a, **k: "",
        Requirement=types.SimpleNamespace(parse=lambda *a, **k: None),
    )
    monkeypatch.setitem(sys.modules, "pkg_resources", stub_pkg_resources)

    from win10toast import ToastNotifier

    tn = ToastNotifier()
    thread = tn.show_toast("hi", "body", duration=0, threaded=True)
    assert isinstance(thread, threading.Thread)
    thread.join(timeout=1)
