@echo off
:: HSBVectoAI Backend — Local Development Starter

echo [HSBVectoAI] Backend geliştirici modu başlatılıyor...

if not exist ".env" (
    echo .env dosyası bulunamadı. .env.example kopyalanıyor...
    copy .env.example .env
    echo Lütfen .env dosyasını düzenleyin ve tekrar çalıştırın.
    pause
    exit /b 1
)

if not exist "venv" (
    echo Virtual environment oluşturuluyor (Python 3.12)...
    py -3.12 -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo.
echo Backend başlatılıyor: http://localhost:8000
echo Swagger UI:           http://localhost:8000/docs
echo.
uvicorn main:app --reload --port 8000 --host 0.0.0.0
