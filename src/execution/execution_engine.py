import os, pandas as pd, ccxt
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

print("🛡️ [OTAK B] Mandor Posisi Aktif (Smart BEP & AI Profit Lock Manager)...", flush=True)

load_dotenv(find_dotenv())
engine = create_engine(os.getenv("DATABASE_URL"))

try:
    exchange = ccxt.bybit({'apiKey': os.getenv("BYBIT_API_KEY"), 'secret': os.getenv("BYBIT_SECRET_KEY"), 'options': {'defaultType': 'linear', 'recvWindow': 60000}})
    exchange.load_markets()
except Exception as e: print(f"❌ [OTAK B] Gagal koneksi Bybit: {e}")

def manage_positions_and_signals():
    try:
        df_pending = pd.read_sql("SELECT * FROM trading_signals WHERE status = 'PENDING'", con=engine)
        with engine.begin() as conn:
            if not df_pending.empty:
                for _, row in df_pending.iterrows():
                    conn.execute(text("UPDATE trading_signals SET status = 'READY_TO_EXECUTE' WHERE id = :id AND status = 'PENDING'"), {"id": row['id']})
                    print(f"✅ [OTAK B] Sinyal {row['symbol']} disahkan.")

        print("🔍 [MANDOR] Memindai posisi aktif untuk Target ROE & BEP...")
        positions = exchange.fetch_positions()
        executed_signals = pd.read_sql("SELECT symbol, target_roe FROM trading_signals WHERE status = 'EXECUTED'", con=engine)
        roe_map = dict(zip(executed_signals['symbol'], executed_signals['target_roe'])) if not executed_signals.empty else {}

        for pos in positions:
            if float(pos.get('contracts', 0)) > 0:
                sym, entry, mark = pos['symbol'], float(pos['entryPrice']), float(pos['markPrice'])
                leverage = float(pos.get('leverage', 10))
                contracts = float(pos['contracts'])
                
                roe_pct = ((mark - entry) / entry) * 100 * leverage if pos['side'].lower() == 'long' else ((entry - mark) / entry) * 100 * leverage
                target_roe = float(roe_map.get(sym, 20.0))

                print(f"📊 [MONITOR] {sym} | ROE: {roe_pct:.2f}% | Target Lock AI: {target_roe}%")

                if roe_pct >= target_roe:
                    print(f"🎯 [PROFIT LOCK] {sym} mencapai target AI ({roe_pct:.2f}% >= {target_roe}%). Kunci Kemenangan!")
                    try:
                        exchange.create_order(symbol=sym, type='market', side='sell' if pos['side'].lower() == 'long' else 'buy', amount=contracts, params={'reduceOnly': True})
                        with engine.begin() as conn: conn.execute(text("UPDATE trading_signals SET status = 'CLOSED' WHERE symbol = :sym AND status = 'EXECUTED'"), {"sym": sym})
                        print(f"✅ [SUCCESS] Profit {sym} aman dikunci!")
                        continue
                    except Exception as err: print(f"⚠️ Gagal close posisi: {err}")

                sl = float(pos.get('stopLoss') or 0)
                if pos['side'].lower() == 'long' and 4.0 <= roe_pct < target_roe and sl < entry:
                    print(f"🛡️ [BEP SYSTEM] ROE {roe_pct:.2f}%. Menggeser SL ke BEP ({entry})...")
                    try:
                        exchange.private_post_v5_position_trading_stop({'category': 'linear', 'symbol': sym.replace('/', '').replace(':USDT', ''), 'stopLoss': str(entry), 'positionIdx': 0})
                        print(f"✅ [BEP] Posisi {sym} aman tanpa risiko!")
                    except Exception as err: print(f"⚠️ Gagal BEP: {err}")

    except Exception as e: print(f"❌ [OTAK B] Error: {e}")

if __name__ == "__main__": manage_positions_and_signals()