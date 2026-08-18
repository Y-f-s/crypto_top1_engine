import os
import pandas as pd
import pandas_ta as ta
import traceback
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
engine = create_engine(os.getenv("DATABASE_URL"))

def calculate_tema(df, length=9):
    try:
        t = ta.tema(df['close'], length=length)
        if t is not None: return t
    except: pass
    e1 = df['close'].ewm(span=length, adjust=False).mean()
    e2 = e1.ewm(span=length, adjust=False).mean()
    return (3 * e1) - (3 * e2) + e2.ewm(span=length, adjust=False).mean()

def process_features():
    print(f"   ⏳ Meracik Indikator Lengkap (TEMA, MACD, RSI, BB, VOL_SMA, OBV, ATR, EMA)...", flush=True)
    try:
        df_raw = pd.read_sql("SELECT symbol, timeframe, timestamp, open, high, low, close, volume FROM market_data", engine)
        if df_raw.empty: return

        feats = []
        for (symbol, timeframe), group in df_raw.groupby(['symbol', 'timeframe']):
            df = group.sort_values('timestamp').copy()
            if len(df) < 50: continue 
                
            # 1. Tren & Momentum
            df['tema_9'] = calculate_tema(df, 9)
            df['tema_21'] = calculate_tema(df, 21)
            df['ema_50'] = ta.ema(df['close'], length=50)
            df['ema_200'] = ta.ema(df['close'], length=200)
            
            macd_df = ta.macd(df['close'], fast=12, slow=26, signal=9)
            df['macd'] = macd_df.iloc[:, 0] if macd_df is not None and not macd_df.empty else 0.0
            
            # 2. Volatilitas & Swing (Safe Check)
            rsi_s = ta.rsi(df['close'], length=14)
            df['rsi'] = rsi_s if rsi_s is not None else 50.0
            
            atr_s = ta.atr(df['high'], df['low'], df['close'], length=14)
            df['atr'] = atr_s if atr_s is not None else 0.0
            
            bb_df = ta.bbands(df['close'], length=20, std=2.0)
            if bb_df is not None and not bb_df.empty:
                df['bb_lower'] = bb_df.iloc[:, 0]
                df['bb_upper'] = bb_df.iloc[:, 2]
            else:
                df['bb_lower'] = df['close'] * 0.98
                df['bb_upper'] = df['close'] * 1.02
                
            # 3. Detektor Paus & Volume (Safe Check)
            vol_sma_s = ta.sma(df['volume'], length=20)
            df['vol_sma'] = vol_sma_s if vol_sma_s is not None else df['volume']
            
            obv_s = ta.obv(df['close'], df['volume'])
            df['obv'] = obv_s if obv_s is not None else 0.0
            
            latest = df.iloc[-1]
            
            feats.append({
                'symbol': symbol, 'timeframe': timeframe, 'close': float(latest['close']), 
                'volume': float(latest['volume']), 
                'vol_sma': float(latest['vol_sma']) if not pd.isna(latest['vol_sma']) else float(latest['volume']),
                'obv': float(latest['obv']) if not pd.isna(latest['obv']) else 0.0,
                'macd': float(latest['macd']) if not pd.isna(latest['macd']) else 0.0, 
                'tema_9': float(latest['tema_9']) if not pd.isna(latest['tema_9']) else 0.0,
                'tema_21': float(latest['tema_21']) if not pd.isna(latest['tema_21']) else 0.0, 
                'ema_50': float(latest['ema_50']) if not pd.isna(latest['ema_50']) else 0.0,
                'ema_200': float(latest['ema_200']) if not pd.isna(latest['ema_200']) else 0.0,
                'rsi': float(latest['rsi']) if not pd.isna(latest['rsi']) else 50.0,
                'atr': float(latest['atr']) if not pd.isna(latest['atr']) else 0.0,
                'bb_lower': float(latest['bb_lower']) if not pd.isna(latest['bb_lower']) else 0.0, 
                'bb_upper': float(latest['bb_upper']) if not pd.isna(latest['bb_upper']) else 0.0,
            })
            
        if feats:
            pd.DataFrame(feats).to_sql('market_features', engine, if_exists='replace', index=False)
            print(f"   ✅ {len(feats):,} matriks indikator super lengkap berhasil diracik.", flush=True)
            
    except Exception as e: 
        print(f"   ❌ Error detail: {e}", flush=True)
        traceback.print_exc()

if __name__ == "__main__": process_features()