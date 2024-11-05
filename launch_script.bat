@echo off

net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Dieses Skript erfordert Administratorrechte. Starte neu...
    :: Batch-Datei mit Administratorrechten neu starten
    powershell -Command "Start-Process cmd -Argument '/c \"%~s0\"' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

python xL_IpsumWalll.py

pause