import os
import sys
import warnings

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYTEST_ADDOPTS", "-p no:unraisableexception")

# Suppress deprecation warning emitted by importing ``pkg_resources``.
warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API",
    category=UserWarning,
)

# Ignore ResourceWarnings emitted when ``TemporaryDirectory`` instances
# are implicitly cleaned up during test teardown.
warnings.filterwarnings(
    "ignore",
    message="Implicitly cleaning up",
    category=ResourceWarning,
    module="tempfile",
)

# Silence "unraisable exception" warnings triggered by such cleanup during
# interpreter shutdown. These warnings would otherwise surface in pytest's
# summary and fail the checks.


def _unraisable_hook(unraisable: object) -> None:
    exc = getattr(unraisable, "exc_value", None)
    if isinstance(exc, ResourceWarning) and str(exc).startswith("Implicitly"):
        return
    sys.__unraisablehook__(unraisable)


sys.unraisablehook = _unraisable_hook
