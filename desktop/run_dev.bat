@echo off
title HSBVectoAI — Dev Mode
echo Starting HSBVectoAI in dev mode...
echo.

if not exist ".venv" (
    echo [SETUP] Sanal ortam olusturuluyor...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

python main.py
pause
