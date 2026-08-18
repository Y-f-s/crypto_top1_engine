import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

print("⚙️ [SYSTEM] Mereset tabel 'market_features' agar kolom baru bisa masuk...")

load_dotenv(find_dotenv())
engine = create_engine(os.getenv("DATABASE_URL"))

try:
    with engine.begin() as conn:
        # Menghapus tabel market_features lama secara paksa
        conn.execute(text("DROP TABLE IF EXISTS market_features;"))
    print("✅ [SUCCESS] Tabel 'market_features' lama telah dihapus!")
    print("👉 Silakan jalankan kembali 'python run_bot.py'. Sistem akan otomatis membuat tabel baru dengan kolom yang lengkap.")
except Exception as e:
    print(f"❌ [ERROR] Gagal mereset database: {e}")