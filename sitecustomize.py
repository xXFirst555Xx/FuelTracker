import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import warnings

# Suppress deprecation warning emitted by importing ``pkg_resources``.
warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API",
    category=UserWarning,
)
