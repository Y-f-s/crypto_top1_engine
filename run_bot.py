import os
import subprocess
import sys
import time
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

def print_banner(text):
    print(f"\n{'='*60}", flush=True)
    print(f" {text} ", flush=True)
    print(f"{'='*60}", flush=True)

def run_step(script_path, description):
    print(f"\n🚀 {description} [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]", flush=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    result = subprocess.run([sys.executable, script_path], env=env)
    if result.returncode != 0:
        print(f"❌ Error pada: {description}")
        return False
    return True

def reset_market_features_table():
    """Mereset total tabel market_features di awal booting agar siap diisi kolom indikator baru."""
    print(f"\n🚀 Auto-Fix: Reset Tabel market_features [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]", flush=True)
    try:
        load_dotenv(find_dotenv())
        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS market_features;"))
        print("✅ [SUCCESS] Tabel 'market_features' lama dihapus! Siap diganti struktur baru oleh Pandas.")
    except Exception as e:
        print(f"❌ [ERROR] Gagal mereset database: {e}")

if __name__ == "__main__":
    print_banner("⚙️ [SYSTEM BOOT] AUTO-INSTALLER & VERIFIKASI PUSTAKA")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "google-genai", "groq", "pandas-ta", "ccxt", "sqlalchemy", "psycopg2-binary", "python-dotenv", "requests"], check=False)
    
    print_banner("⚙️ [SYSTEM BOOT] INISIALISASI DATABASE")
    reset_market_features_table() 
    run_step("src/utils/db_init.py", "Verifikasi Tabel Database")

    print_banner("🤖 SISTEM FULL-FLOW TRADING BOT AKTIF")
    LOOP_INTERVAL_SECONDS = 300 

    try:
        while True:
            print_banner(f"🔄 SIKLUS BARU DIMULAI: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if run_step("src/collectors/data_collector.py", "Tahap 1: Radar 360° (Data Collector)"):
                if run_step("src/features/feature_builder.py", "Tahap 2: Pabrik Indikator (TEMA, MACD, OBV, ATR, dll)"):
                    if run_step("src/strategies/strategy_engine.py", "Tahap 3: Otak A (AI Triple-Engine + Whale Detector)"):
                        if run_step("src/execution/execution_engine.py", "Tahap 4 & 6: Otak B (Mandor Posisi & Smart BEP/Lock)"):
                            run_step("src/execution/exchange_executor.py", "Tahap 5: Otak C (Eksekutor Bybit + Notional Guard)")

            print(f"\n💤 Siklus Selesai. Menunggu {LOOP_INTERVAL_SECONDS} detik...")
            time.sleep(LOOP_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n🛑 Bot dihentikan dengan aman.")