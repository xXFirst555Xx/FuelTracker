"""Compatibility wrapper for running as a top-level package."""
from importlib import import_module
import sys
_module = import_module('src.fueltracker')
sys.modules[__name__] = _module
