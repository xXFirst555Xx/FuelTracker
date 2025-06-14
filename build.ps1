$ErrorActionPreference = 'Stop'

python tools/fetch_icons.py
python tools/compile_resources.py

pyinstaller --noconfirm --clean --onefile build.spec

if ($env:SIGNTOOL -and $env:CERT_PATH) {
    & $env:SIGNTOOL sign /f $env:CERT_PATH /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist/FuelTracker.exe
}
