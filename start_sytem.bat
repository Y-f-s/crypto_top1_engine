@echo off
chcp 65001 >nul
title Theta Digital Hub - System Launcher
echo ========================================================
echo   MENYALAKAN THETA DIGITAL HUB (DASHBOARD + BOT + TELEGRAM)
echo ========================================================

cd /d C:\Users\yans_13\crypto_top1_engine

echo.
echo [1/3] Menyalakan Dashboard Streamlit...
start "Theta Dashboard" cmd /k "chcp 65001 >nul && call venv\Scripts\activate && streamlit run dashboard.py"

echo [2/3] Menyalakan Mesin Bot Utama...
start "Theta Bot Engine" cmd /k "run_bot.bat"

echo [3/3] Menyalakan Telegram Commander (Remote Control)...
start "Telegram Commander" cmd /k "chcp 65001 >nul && call venv\Scripts\activate && set PYTHONPATH=. && python src/utils/telegram_commander.py"

echo.
echo [SUCCESS] Ketiga sistem berhasil dijalankan bersamaan!
pause