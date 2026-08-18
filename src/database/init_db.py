import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def init_database_tables():
    """Membuat dan mereset struktur tabel database agar tipe data timestamp & fitur sesuai."""
    print("⚙️ [DB INIT] Memeriksa & memperbarui struktur tabel database...")
    
    query_trades = """
    CREATE TABLE IF NOT EXISTS final_trades (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        direction VARCHAR(10) NOT NULL,
        position_size_usdt FLOAT NOT NULL,
        stop_loss FLOAT NOT NULL,
        status VARCHAR(30) NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Hapus tabel mentah lama jika tipe datanya masih BIGINT
    query_drop_data = "DROP TABLE IF EXISTS market_data;"
    query_data = """
    CREATE TABLE market_data (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        timeframe VARCHAR(10) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume FLOAT
    );
    """
    
    query_drop_features = "DROP TABLE IF EXISTS market_features;"
    query_features = """
    CREATE TABLE market_features (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        timeframe VARCHAR(10) NOT NULL,
        close FLOAT,
        volume FLOAT,
        macd FLOAT,
        macd_signal FLOAT,
        tema_9 FLOAT,
        tema_21 FLOAT,
        rsi FLOAT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(query_trades))
            conn.execute(text(query_drop_data))     # Reset tabel data mentah
            conn.execute(text(query_data))          # Buat dengan tipe TIMESTAMP
            conn.execute(text(query_drop_features)) # Reset tabel fitur
            conn.execute(text(query_features))      
            conn.commit()
        print("   ✅ Struktur tabel database berhasil diperbarui total.")
    except Exception as e:
        print(f"   ❌ Gagal menginisialisasi tabel database: {e}")

if __name__ == "__main__":
    init_database_tables()