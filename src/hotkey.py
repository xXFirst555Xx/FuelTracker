from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QObject, Signal
else:
    try:  # pragma: no cover - optional dependency
        from PySide6.QtCore import QObject, Signal
    except Exception:  # pragma: no cover - optional dependency

        class QObject:
            """Fallback QObject when PySide6 is unavailable."""

            pass

        class Signal:
            """Minimal Qt-like signal used for testing without PySide6."""

            def __init__(self) -> None:
                self._slots: list[Callable[..., Any]] = []

            def connect(self, slot: Callable[..., Any]) -> None:  # noqa: D401
                self._slots.append(slot)

            def emit(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
                for slot in list(self._slots):
                    slot(*args, **kwargs)


import logging

logger = logging.getLogger(__name__)

_NOT_LOADED = object()

# Optional keyboard module, initialized lazily to avoid import side effects
keyboard: Any | None = _NOT_LOADED


def _ensure_keyboard() -> None:
    """Load the optional ``keyboard`` module on demand."""
    global keyboard
    if keyboard is not _NOT_LOADED:
        return
    try:  # pragma: no cover - optional dependency
        from importlib import import_module

        keyboard = import_module("keyboard")
    except Exception:
        keyboard = None


class GlobalHotkey(QObject):
    triggered = Signal()

    def __init__(self, sequence: str) -> None:
        super().__init__()
        self.sequence = sequence
        self._registered = False
        self._listener: Any | None = None
        self._handle: Any | None = None
        # Guard flag used during shutdown to avoid race conditions when the
        # backend fires callbacks as we are tearing down.
        self._stopping = False

    def _callback_adapter(self, *args: object) -> int:
        """Invoke ``_wrapped_callback`` and always return ``1`` for Win32 hooks."""
        # Qt expects a Win32 hook callback to return an ``int``. Failing to do so
        # results in ``TypeError: WPARAM is simple, so must be an int object`` on
        # Windows.
        try:
            self._wrapped_callback(*args)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("ข้อผิดพลาดตัวแปลงฮอตคีย์: %s", exc)
        # Always return ``1`` to satisfy the Win32 hook requirement
        return 1

    def _wrapped_callback(self, *args: object) -> None:
        """Emit the hotkey signal."""
        if self._stopping:
            # Ignore callbacks that may fire while the listener is shutting down
            return
        try:
            self.triggered.emit()
        except Exception as e:  # pragma: no cover - defensive
            logger.exception("ข้อผิดพลาดฮอตคีย์: %s", e)

    def start(self) -> None:
        if keyboard is _NOT_LOADED:
            _ensure_keyboard()
        if keyboard is None or self._registered:
            return
        try:
            if hasattr(keyboard, "GlobalHotKeys"):
                # Support for pynput
                self._listener = keyboard.GlobalHotKeys(
                    {self._format(self.sequence): self._callback_adapter}
                )
                self._listener.start()
            else:
                self._handle = keyboard.add_hotkey(
                    self._format(self.sequence),
                    self._callback_adapter,
                )
        except (
            Exception
        ):  # pragma: no cover - ignore environments without input devices
            return
        self._registered = True

    def stop(self) -> None:
        if keyboard is _NOT_LOADED:
            _ensure_keyboard()
        if keyboard is None or not self._registered:
            return

        self._stopping = True
        try:
            if hasattr(keyboard, "GlobalHotKeys"):
                if self._listener is not None:
                    try:
                        self._listener.stop()
                        if hasattr(self._listener, "join"):
                            self._listener.join(timeout=1.0)
                    finally:
                        self._listener = None
            else:
                if self._handle is not None:
                    try:
                        keyboard.remove_hotkey(self._handle)
                    except Exception:
                        logger.exception("Failed to remove global hotkey")
                    finally:
                        self._handle = None
        except Exception as e:  # pragma: no cover - defensive
            logger.exception("ข้อผิดพลาดหยุดฮอตคีย์: %s", e)
        finally:
            self._registered = False
            self._stopping = False

    def __del__(self) -> None:  # pragma: no cover - defensive
        """Ensure any system hooks are released on object deletion."""
        try:
            self.stop()
        except Exception:
            # Avoid spurious errors during interpreter shutdown
            logger.exception("Error stopping hotkey during object deletion")

    @staticmethod
    def _format(seq: str) -> str:
        """Normalize Qt style hotkey string to keyboard module format."""
        tokens = [t.strip().lower() for t in seq.split("+") if t.strip()]
        return "+".join(tokens)
