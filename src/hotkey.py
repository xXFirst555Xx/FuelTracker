from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from typing import Any

kb: Any | None
try:
    import keyboard as kb
except Exception:  # pragma: no cover - optional dependency
    kb = None
keyboard = kb  # FIX: mypy clean


class GlobalHotkey(QObject):
    triggered = Signal()

    def __init__(self, sequence: str) -> None:
        super().__init__()
        self.sequence = sequence
        self._registered = False

    def start(self) -> None:
        if keyboard is None or self._registered:
            return
        try:
            keyboard.add_hotkey(
                self._format(self.sequence),
                lambda: (self.triggered.emit() or False),
            )
        except Exception:  # pragma: no cover - ignore environments without input devices
            return
        self._registered = True

    def stop(self) -> None:
        if keyboard is not None and self._registered:
            keyboard.remove_hotkey(self._format(self.sequence))
            self._registered = False

    @staticmethod
    def _format(seq: str) -> str:
        """Normalize Qt style hotkey string to keyboard module format."""
        tokens = [t.strip().lower() for t in seq.split("+") if t.strip()]
        return "+".join(tokens)
