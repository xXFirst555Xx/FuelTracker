# -*- mode: python ; coding: utf-8 -*-
import base64
import os
import certifi

block_cipher = None

ICON_B64 = (
    "AAABAAMAEBAAAABoAwAAGgAAACAgAAAAPgAAACABAAIAAAAMAAABYwAAAAAEAAAAEAAAAAAAAAAAAAAA"  # small blank icon
)
ICON_PATH = os.path.join('assets', 'icon.ico')
os.makedirs('assets', exist_ok=True)
if not os.path.exists(ICON_PATH):
    with open(ICON_PATH, 'wb') as f:
        f.write(base64.b64decode(ICON_B64))

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[(certifi.where(), 'cacert.pem')],
    hiddenimports=['certifi'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FuelTrackerLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FuelTrackerLauncher',
)
