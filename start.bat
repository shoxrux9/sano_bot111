@echo off
echo =======================================
echo    SANO BOOKS BOT - Ishga tushirish
echo =======================================
echo.

REM Python mavjudligini tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo XATO: Python o'rnatilmagan!
    echo https://python.org dan yuklab o'rnating.
    pause
    exit /b 1
)

REM .env fayli mavjudligini tekshirish
if not exist ".env" (
    echo XATO: .env fayli topilmadi!
    echo .env.example faylini nusxalab .env nomini bering
    echo va BOT_TOKEN hamda ADMIN_IDS ni kiriting.
    pause
    exit /b 1
)

REM Paketlarni o'rnatish (birinchi marta)
echo Paketlar tekshirilmoqda...
python -m pip install -r requirements.txt -q

echo.
echo Bot ishga tushmoqda...
echo To'xtatish uchun: Ctrl+C
echo.

python bot.py

pause
