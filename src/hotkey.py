from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from typing import Any

try:
    import keyboard as kb_module
except Exception:  # pragma: no cover - optional dependency
    kb_module = None

# Optional keyboard module, may be ``None`` when dependency is missing
keyboard: Any | None = kb_module


class GlobalHotkey(QObject):
    triggered = Signal()

    def __init__(self, sequence: str) -> None:
        super().__init__()
        self.sequence = sequence
        self._registered = False
        self._listener: Any | None = None

    # FIX: return int to avoid WPARAM crash
    def _wrapped_callback(self) -> int:
        try:
            self.triggered.emit()
        except Exception as e:  # pragma: no cover - defensive
            print("Hotkey error:", e)
        return 1

    def start(self) -> None:
        if keyboard is None or self._registered:
            return
        try:
            if hasattr(keyboard, "GlobalHotKeys"):
                # Support for pynput
                self._listener = keyboard.GlobalHotKeys(
                    {self._format(self.sequence): self._wrapped_callback}
                )
                self._listener.start()
            else:
                keyboard.add_hotkey(
                    self._format(self.sequence),
                    self._wrapped_callback,
                )
        except Exception:  # pragma: no cover - ignore environments without input devices
            return
        self._registered = True

    def stop(self) -> None:
        if keyboard is not None and self._registered:
            if hasattr(keyboard, "GlobalHotKeys"):
                if self._listener is not None:
                    self._listener.stop()
                    self._listener = None
            else:
                keyboard.remove_hotkey(self._format(self.sequence))
            self._registered = False

    @staticmethod
    def _format(seq: str) -> str:
        """Normalize Qt style hotkey string to keyboard module format."""
        tokens = [t.strip().lower() for t in seq.split("+") if t.strip()]
        return "+".join(tokens)
