-- 1. Hapus tabel lama yang strukturnya sudah tidak relevan
DROP TABLE IF EXISTS features_log;

-- 2. Buat tabel baru dengan struktur yang sesuai dengan feature_builder.py
CREATE TABLE features_log (
    id SERIAL PRIMARY KEY,
    timestamp BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(5) NOT NULL,
    close NUMERIC(18, 8) NOT NULL,
    ema_fast NUMERIC(18, 8),
    ema_slow NUMERIC(18, 8),
    rsi NUMERIC(6, 2),
    atr_pct NUMERIC(6, 2),
    adx NUMERIC(6, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe, timestamp)
);