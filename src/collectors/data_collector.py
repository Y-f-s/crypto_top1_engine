import os, time, ccxt, pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
engine = create_engine(os.getenv("DATABASE_URL"))
exchange = ccxt.bybit({'enableRateLimit': True, 'options': {'defaultType': 'swap'}})

def get_all_target_coins():
    try:
        # 1. Definisikan kata kunci yang ingin dihindari (Blacklist)
        BLACKLIST_KEYWORDS = ["STOCK", "PRE", "USDC", "PERP", "BETA"]
        
        tickers = exchange.fetch_tickers()
        valid = []
        
        for s, t in tickers.items():
            # Syarat 1: Harus berakhiran :USDT dan Volume > $1M
            if s.endswith(':USDT') and t.get('quoteVolume', 0) > 1_000_000:
                
                # Syarat 2: Cek apakah simbol mengandung kata kunci Blacklist
                if any(keyword in s for keyword in BLACKLIST_KEYWORDS):
                    continue  # Lewati koin ini (mencegah error 110126 di Bybit)
                
                valid.append({'symbol': s, 'volume': t.get('quoteVolume', 0)})
                
        return [p['symbol'] for p in sorted(valid, key=lambda x: x['volume'], reverse=True)]
    except: return ['BTC/USDT:USDT', 'ETH/USDT:USDT']

def collect_market_data():
    symbols = get_all_target_coins()
    total = len(symbols)
    print(f"   🎯 Target: {total} Koin USDT Perpetual (Likuiditas > $1M)", flush=True)
    
    all_data = []
    for idx, symbol in enumerate(symbols, 1):
        if idx % 50 == 0 or idx == total: print(f"      ... {idx}/{total} koin berhasil dipindai ...", flush=True)
        for tf in ['4h', '1h', '15m', '5m']:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
                for r in ohlcv:
                    all_data.append({'symbol': symbol, 'timeframe': tf, 'timestamp': pd.to_datetime(r[0], unit='ms'), 'open': float(r[1]), 'high': float(r[2]), 'low': float(r[3]), 'close': float(r[4]), 'volume': float(r[5])})
            except: pass
            time.sleep(0.05) 

    if all_data:
        try:
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM market_data"))
                conn.commit()
            pd.DataFrame(all_data).to_sql('market_data', engine, if_exists='append', index=False)
            print(f"   ✅ {len(all_data):,} baris data historis disimpan.", flush=True)
        except Exception as e: print(f"   ❌ Gagal simpan: {e}", flush=True)

if __name__ == "__main__": collect_market_data()