import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
engine = create_engine(os.getenv("DATABASE_URL"))

def clean_database():
    print("🧹 Memulai proses pembersihan database...")
    try:
        with engine.begin() as conn:
            # Mengosongkan isi tabel dan mereset ID kembali ke 1
            conn.execute(text("TRUNCATE TABLE market_data RESTART IDENTITY CASCADE;"))
            conn.execute(text("TRUNCATE TABLE market_features RESTART IDENTITY CASCADE;"))
            
        print("✅ Database berhasil dibersihkan! Ruang penyimpanan (disk) sudah kembali lega.")
        print("🛡️ Catatan: Tabel 'trading_signals' (Riwayat Mandor) dibiarkan aman dan tidak dihapus.")
    except Exception as e:
        print(f"❌ Gagal membersihkan database: {e}")

if __name__ == "__main__":
    clean_database()