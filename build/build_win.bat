@echo off
setlocal

rem Change to repository root
cd /d "%~dp0.."

if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate

python -m pip install --upgrade pip >nul
python -m pip install -r requirements.lock pyinstaller tufup >nul

for /f "delims=" %%V in ('python -c "import sys;sys.path.insert(0,'src');import fueltracker;print(fueltracker.__version__)"') do set VERSION=%%V

python -c "import os, pathlib, base64; ICON_B64='AAABAAMAEBAAAAAAIABLAAAANgAAABgYAAAAACAAUQAAAIEAAAAgIAAAAAAgAFMAAADSAAAAiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAEklEQVR4nGNgGAWjYBSMAggAAAQQAAFVN1rQAAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAGElEQVR4nO3BAQEAAACAkP6v7ggKAICqAQkYAAHVDmlyAAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAACAAAAAgCAYAAABzenr0AAAAGklEQVR4nO3BAQEAAACCIP+vbkhAAQAAAO8GECAAARlDNO4AAAAASUVORK5CYII=';p=pathlib.Path('assets','fuel.ico');p.parent.mkdir(exist_ok=True);p.write_bytes(base64.b64decode(ICON_B64)); txt=pathlib.Path('version.txt').read_text(encoding='utf-8').replace('{__VERSION__}', os.environ['VERSION']); pathlib.Path('build','version_final.txt').write_text(txt, encoding='utf-8')"

pyinstaller ^
  --noconfirm --clean --windowed ^
  --name FuelTracker ^
  --icon assets\fuel.ico ^
  --add-data "tuf_metadata\\root.json;tuf_metadata" ^
  --version-file build\version_final.txt ^
  src\fueltracker\__main__.py

if exist dist\FuelTracker\FuelTracker.exe (
    echo Build succeeded: dist\FuelTracker\FuelTracker.exe
) else (
    echo Build failed
)

endlocal
