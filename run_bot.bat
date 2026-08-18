@echo off
chcp 65001 >nul
title Theta Bot Engine (24/7 Looping)
cd /d C:\Users\yans_13\crypto_top1_engine

echo [1/3] Mengaktifkan Virtual Environment...
call venv\Scripts\activate

echo [2/3] Memastikan Pustaka Terinstal...
pip install -q ccxt pandas sqlalchemy python-dotenv psycopg2-binary pandas-ta requests openai

echo [3/3] Memulai Bot Trading Otomatis (Orchestrator)...
python run_all.py

pause