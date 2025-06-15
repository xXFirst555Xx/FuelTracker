#!/usr/bin/env bash
set -euo pipefail

# Build FuelTracker using PyInstaller
pyinstaller --noconfirm --clean --onefile build.spec

# Optionally sign the binary when SIGNTOOL and CERT_PATH are provided
if [[ -n "${SIGNTOOL:-}" && -n "${CERT_PATH:-}" ]]; then
    "$SIGNTOOL" sign /f "$CERT_PATH" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist/FuelTracker.exe
fi
