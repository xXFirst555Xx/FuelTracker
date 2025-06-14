@echo off
setlocal


REM Build FuelTracker with PyInstaller
pyinstaller --noconfirm --clean --onefile build.spec

REM Optionally sign the binary if SIGNTOOL and CERT_PATH are set
IF NOT "%SIGNTOOL%"=="" IF NOT "%CERT_PATH%"=="" (
    "%SIGNTOOL%" sign /f "%CERT_PATH%" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist\FuelTracker.exe
)

endlocal
