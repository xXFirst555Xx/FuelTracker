# -*- mode: python ; coding: utf-8 -*-

import os
import base64

block_cipher = None

# icon data stored in base64 to avoid committing binary files
ICON_B64 = (
    "AAABAAMAEBAAAAAAIABLAAAANgAAABgYAAAAACAAUQAAAIEAAAAgIAAAAAAgAFMAAADSAAAAiVBO"
    "Rw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAEklEQVR4nGNgGAWjYBSMAggAAAQQAAFV"
    "N1rQAAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAGElEQVR4"
    "nO3BAQEAAACAkP6v7ggKAICqAQkYAAHVDmlyAAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAA"
    "ACAAAAAgCAYAAABzenr0AAAAGklEQVR4nO3BAQEAAACCIP+vbkhAAQAAAO8GECAAARlDNO4AAAAA"
    "SUVORK5CYII="
)

ICON_PATH = os.path.join("assets", "app.ico")

# ensure icon file exists when running pyinstaller
os.makedirs("assets", exist_ok=True)
if not os.path.exists(ICON_PATH):
    with open(ICON_PATH, "wb") as fh:
        fh.write(base64.b64decode(ICON_B64))


a = Analysis(
    ['src/fueltracker/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/views/*.ui', 'views'),
        ('src/views/dialogs/*.ui', 'views/dialogs'),
        ('assets/*', 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FuelTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='assets/app.ico',
)
