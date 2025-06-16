from __future__ import annotations

from PySide6.QtCore import QObject, Signal

try:
    from pynput import keyboard
except Exception:  # pragma: no cover - optional dependency
    keyboard = None  # type: ignore


class GlobalHotkey(QObject):
    triggered = Signal()

    def __init__(self, sequence: str) -> None:
        super().__init__()
        self.sequence = sequence
        self._listener: keyboard.GlobalHotKeys | None = None  # type: ignore

    def start(self) -> None:
        if keyboard is None:
            return
        self._listener = keyboard.GlobalHotKeys({self._format(self.sequence): self.triggered.emit})
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    @staticmethod
    def _format(seq: str) -> str:
        return seq.lower().replace("+", "+")
