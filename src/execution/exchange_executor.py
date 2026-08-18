import os
import pandas as pd
import ccxt
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

print("⚡ [OTAK C] Eksekutor Bybit (Compound Margin, AI Leverage, Notional Guard)...", flush=True)

load_dotenv(find_dotenv())
engine = create_engine(os.getenv("DATABASE_URL"))

try:
    exchange = ccxt.bybit({
        'apiKey': os.getenv("BYBIT_API_KEY"),
        'secret': os.getenv("BYBIT_SECRET_KEY"),
        'enableRateLimit': True,
        'options': {'defaultType': 'linear', 'recvWindow': 60000}
    })
    exchange.load_markets()
except Exception as e: 
    print(f"❌ [OTAK C] Gagal terhubung ke Bybit: {e}")
    exit(1)

def get_margin_with_notional_guard(ai_leverage):
    try:
        # Pembacaan fleksibel untuk Akun Standar dan Akun Terpadu (UTA)
        bal = exchange.fetch_balance({'type': 'linear'})
        usdt_free = 0.0
        
        if 'USDT' in bal and 'free' in bal['USDT']:
            usdt_free = float(bal['USDT']['free'] or 0.0)
        elif 'info' in bal and 'result' in bal['info'] and 'list' in bal['info']['result']:
            coin_list = bal['info']['result']['list'][0].get('coin', [])
            for c in coin_list:
                if c.get('coin') == 'USDT':
                    usdt_free = float(c.get('equity') or c.get('walletBalance') or 0.0)
                    break

        print(f"💰 [WALLET] Saldo USDT Aktif Terbaca: ${usdt_free:.2f}")

        active_bal = usdt_free if usdt_free > 0 else 4.0
        margin = max(round(active_bal * (0.50 if active_bal < 10 else 0.30 if active_bal <= 50 else 0.20), 2), 1.0)
        
        # Jaga nilai transaksi minimal bursa ($5 Notional Value)
        if (margin * ai_leverage) < 5.0:
            margin = round(5.0 / ai_leverage, 2)
            print(f"🛡️ [NOTIONAL GUARD] Margin disesuaikan ke ${margin} agar memenuhi syarat Bybit.")
            
        return margin
    except Exception as e:
        print(f"⚠️ Pembacaan saldo dompet fallback ke $2.0: {e}")
        return 2.0

def execute_ready_signals():
    try:
        df_ready = pd.read_sql("SELECT * FROM trading_signals WHERE status = 'READY_TO_EXECUTE'", con=engine)
        if df_ready.empty: 
            print("💤 [OTAK C] Tidak ada sinyal siap tembak.")
            return

        with engine.begin() as conn:
            for _, row in df_ready.iterrows():
                sym, entry, ai_lev, sig_id = str(row['symbol']), float(row['entry']), int(row['leverage']), row['id']
                margin = get_margin_with_notional_guard(ai_lev)

                try:
                    try: exchange.set_leverage(ai_lev, sym)
                    except Exception: pass

                    tp = exchange.price_to_precision(sym, float(row['tp']))
                    sl = exchange.price_to_precision(sym, float(row['sl']))
                    qty = exchange.amount_to_precision(sym, (margin * ai_lev) / entry)
                    
                    print(f"🔫 [OTAK C] Tembak ID {sig_id} ({sym}) | Margin: ${margin} | AI Lev: {ai_lev}x | Qty: {qty}")
                    order = exchange.create_order(
                        symbol=sym, type='market', 
                        side='buy' if str(row['action']).upper() == 'BUY' else 'sell', 
                        amount=float(qty), 
                        params={'takeProfit': str(tp), 'stopLoss': str(sl), 'positionIdx': 0}
                    )
                    print(f"✅ [OTAK C] Sukses Tembak! Order ID: {order['id']}")
                    conn.execute(text("UPDATE trading_signals SET status = 'EXECUTED' WHERE id = :id"), {"id": sig_id})
                except Exception as ex:
                    print(f"❌ [OTAK C] Gagal eksekusi {sym}: {ex}")
                    conn.execute(text("UPDATE trading_signals SET status = 'FAILED' WHERE id = :id"), {"id": sig_id})
    except Exception as e: 
        print(f"❌ [OTAK C] Error Database: {e}")

if __name__ == "__main__": execute_ready_signals()