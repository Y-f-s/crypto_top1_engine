import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
engine = create_engine(os.getenv("DATABASE_URL"))

def init_database_tables():
    drop_table_sql = "DROP TABLE IF EXISTS trading_signals;"
    create_table_sql = """
    CREATE TABLE trading_signals (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        action VARCHAR(10) NOT NULL,
        entry DOUBLE PRECISION NOT NULL,
        tp DOUBLE PRECISION NOT NULL,
        sl DOUBLE PRECISION NOT NULL,
        leverage INT DEFAULT 5,
        target_roe DOUBLE PRECISION DEFAULT 20.0,
        reason TEXT,
        status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with engine.begin() as conn:
            conn.execute(text(drop_table_sql))
            conn.execute(text(create_table_sql))
        print("✅ Database terverifikasi: Tabel 'trading_signals' V2 (mendukung AI Leverage & ROE) siap.")
    except Exception as e:
        print(f"❌ Gagal membuat tabel database: {e}")

if __name__ == "__main__":
    init_database_tables()