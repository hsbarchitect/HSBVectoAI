@echo off
title HSBVectoAI — Build
echo.
echo  ╔══════════════════════════════╗
echo  ║   HSBVectoAI Build Script    ║
echo  ╚══════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python bulunamadi! https://python.org adresinden yukleyin.
    pause & exit /b 1
)

:: Create venv if not exists
if not exist ".venv" (
    echo [1/4] Sanal ortam olusturuluyor...
    python -m venv .venv
)

:: Activate venv
call .venv\Scripts\activate.bat

:: Install dependencies
echo [2/4] Bagimliliklar yukleniyor...
pip install -q -r requirements.txt
pip install -q pyinstaller

:: Build exe
echo [3/4] EXE olusturuluyor...
pyinstaller ^
    --name "HSBVectoAI" ^
    --icon "assets\icon.ico" ^
    --windowed ^
    --onefile ^
    --add-data "assets;assets" ^
    --hidden-import PyQt6 ^
    --hidden-import keyring.backends.Windows ^
    --hidden-import win32com ^
    main.py

echo [4/4] Tamamlandi!
echo.
echo  Cikti: dist\HSBVectoAI.exe
echo.
pause
