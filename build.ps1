$ErrorActionPreference = 'Stop'


pyinstaller --noconfirm --clean --onefile fueltracker.spec

if ($env:SIGNTOOL -and $env:CERT_PATH) {
    & $env:SIGNTOOL sign /f $env:CERT_PATH /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist/FuelTracker.exe
}
