@echo off
title UNIVERSITET IQTIDORLI TALABALAR BOTI VA ADMIN PANELI
echo ===============================================================
echo     UNIVERSITET IQTIDORLI TALABALAR BOTI VA ADMIN PANELI
echo ===============================================================
echo.
echo [1/3] Virtual muhit (venv) faollashtirilmoqda...
call .\venv\Scripts\activate.bat

echo [2/3] Brauzerda Admin Panel ochilmoqda: http://localhost:8000/login
start http://localhost:8000/login

echo [3/3] Telegram Bot va FastAPI Server ishga tushirilmoqda...
echo.
echo Serverni to'xtatish uchun: CTRL + C bosing.
echo.
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
pause
