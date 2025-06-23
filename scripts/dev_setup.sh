#!/usr/bin/env sh
# Simple setup script for development and testing
set -e

pip install -r requirements.lock
pip install -e .[dev]

