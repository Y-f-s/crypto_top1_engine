SELECT DISTINCT ON (symbol) 
    timestamp, symbol, timeframe, close, ema_fast, ema_slow, adx, rsi, atr_pct
FROM features_log
ORDER BY symbol, timestamp DESC
```[cite: 13]

### Penyebab Utama Error:
1. **Nilai Indikator Kosong (NaN):** Beberapa koin di tabel `features_log` mungkin memiliki kolom seperti `ema_fast`, `ema_slow`, atau `adx` yang bernilai `NULL` (kosong). Ketika Python mencoba membaca nilai `None` tersebut dan memasukkannya ke query SQL, format SQL menjadi rusak (kosong di tengah *query*), sehingga memicu *syntax error* saat dieksekusi.
2. **Tidak Ada Validasi `dropna()`:** Berbeda dengan *script* `feature_builder.py` yang membersihkan data kosong menggunakan `df.dropna()`, di dalam *script* `strategy_engine_2.py` baris data yang memiliki nilai kosong langsung dievaluasi dan dimasukkan ke query tanpa disaring terlebih dahulu.

---

### Cara Memperbaikinya:
Buka file **`strategy_engine_2.py`**, lalu tambahkan filter penyaringan data kosong (`dropna`) tepat setelah data ditarik dari pandas. 

Ubah fungsi `evaluate_strategies()` menjadi seperti ini:

```python
def evaluate_strategies():
    print("🧠 [OTAK A] Mengevaluasi Sinyal Strategi & Indikator Teknikal...")
    try:
        query = """
            SELECT DISTINCT ON (symbol) 
                timestamp, symbol, timeframe, close, ema_fast, ema_slow, adx, rsi, atr_pct
            FROM features_log
            ORDER BY symbol, timestamp DESC
        """
        df_features = pd.read_sql(query, engine)
        
        if df_features.empty:
            print("⚠️ Belum ada data fitur di tabel features_log.")
            return

        # 🛠️ TAMBAHKAN BARIS INI: Buang baris yang memiliki nilai kosong/NaN
        df_features = df_features.dropna(subset=['ema_fast', 'ema_slow', 'adx', 'rsi'])

        if df_features.empty:
            print("⚠️ Semua data fitur yang tersedia masih memiliki nilai kosong (NaN).")
            return

        signals_to_save = []
        current_timestamp = int(pd.Timestamp.now().timestamp() * 1000)

        for _, row in df_features.iterrows():
            symbol = row['symbol']
            close = float(row['close'])
            ema_fast = float(row['ema_fast'])
            ema_slow = float(row['ema_slow'])
            adx = float(row['adx'])
            rsi = float(row['rsi'])
            
            if adx > 20:
                if ema_fast > ema_slow and rsi < 70:
                    direction = "LONG"
                    score = 85.0
                    details = f"Bullish Trend. ADX: {adx:.1f}"
                elif ema_fast < ema_slow and rsi > 30:
                    direction = "SHORT"
                    score = 85.0
                    details = f"Bearish Trend. ADX: {adx:.1f}"
                else:
                    continue
                
                signals_to_save.append({
                    'timestamp': current_timestamp,
                    'symbol': symbol,
                    'timeframe': row['timeframe'],
                    'strategy_id': 'EMA_ADX_V1',
                    'direction': direction,
                    'strategy_score': score,
                    'details': details
                })

        if signals_to_save:
            df_signals = pd.DataFrame(signals_to_save)
            df_signals.to_sql('strategy_signals', engine, if_exists='append', index=False, method='multi')
            print(f"✅ Berhasil menghasilkan {len(signals_to_save)} sinyal strategi baru.")
        else:
            print("⚡ Tidak ada koin yang memenuhi kriteria sinyal saat ini.")

    except Exception as e:
        print(f"❌ Error pada Otak A (Strategy Engine): {e}")