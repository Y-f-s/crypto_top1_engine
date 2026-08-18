import os
import json
import re
import pandas as pd
import requests
from groq import Groq
from google import genai
from google.genai import types
from sqlalchemy import create_engine
from datetime import datetime

print("🧠 [OTAK A] Analisis AI Triple-Engine (Crypto-Only Filter & Quant Fallback)...", flush=True)

# 1. KONFIGURASI DATABASE
DATABASE_URL = "postgresql://postgres:Bismillah1313@localhost:5432/crypto_db"
engine = create_engine(DATABASE_URL)

# 2. MANAJEMEN API KEY KEYS
TOGETHER_API_KEY = "856bc9ab86ac0af68f247cd49d9e9ab22b477d30aab31f166aafc21f623a4280"
TOGETHER_MODELS = ["meta-llama/Llama-3.3-70B-Instruct-Turbo"]

GROQ_KEYS = ["gsk_IsiDenganKeyGroqBaruAndaDiSini"]
VALID_GROQ_KEYS = [k for k in GROQ_KEYS if isinstance(k, str) and k.startswith("gsk_") and "IsiDenganKey" not in k]
GROQ_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

GEMINI_KEYS = ["AIzaSyIsiDenganKeyGeminiBaruAndaDiSini"]
VALID_GEMINI_KEYS = [k for k in GEMINI_KEYS if isinstance(k, str) and k.startswith("AIzaSy") and "IsiDenganKey" not in k]
GEMINI_MODELS = ["gemini-1.5-flash", "gemini-2.0-flash"]

# Simbol Komoditas, TradFi, Saham untuk dibuang otomatis
NON_CRYPTO_BLACKLIST = [
    'CL/USDT:USDT', 'TTWO/USDT:USDT', 'XAU/USDT:USDT', 'XAG/USDT:USDT', 
    'SPX/USDT:USDT', 'NDX/USDT:USDT', 'DJI/USDT:USDT', 'USOIL/USDT:USDT', 
    'UKOIL/USDT:USDT', 'MSTR/USDT:USDT', 'COIN/USDT:USDT', 'NVDA/USDT:USDT', 
    'TSLA/USDT:USDT', 'DE30/USDT:USDT', 'HSI/USDT:USDT', 'N225/USDT:USDT'
]

def extract_json(text):
    text_cleaned = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
    text_cleaned = re.sub(r'```\s*', '', text_cleaned)
    match = re.search(r'\{.*\}', text_cleaned, re.DOTALL)
    if match: 
        try: return json.loads(match.group(0))
        except json.JSONDecodeError: pass
    raise ValueError("Format JSON AI tidak valid.")

def run_ai_strategy():
    try:
        df_feat = pd.read_sql("SELECT * FROM market_features WHERE timeframe = '1h'", engine)
        if df_feat.empty: 
            print("⚠️ Data pasar di database kosong.")
            return None

        # --- LAYER 1: BLACKLIST CHECK & FILTER TEKNIKAL ---
        df_feat = df_feat[~df_feat['symbol'].isin(NON_CRYPTO_BLACKLIST)].copy()

        layer1_filtered = df_feat[
            (df_feat['rsi'] >= 40) & 
            (df_feat['rsi'] <= 70) & 
            (df_feat['close'] > df_feat['tema_9']) & 
            (df_feat['volume'] > df_feat['vol_sma'])
        ].copy()

        # --- LAYER 2: STRICT TOP 10 CRYPTO ---
        if not layer1_filtered.empty:
            layer1_filtered['vol_ratio'] = layer1_filtered['volume'] / layer1_filtered['vol_sma']
            top10_candidates = layer1_filtered.sort_values(by=['vol_ratio', 'rsi'], ascending=[False, False]).head(10)
        else:
            print("⚠️ Filter Layer 1 ketat, mengambil koin berdasarkan volume murni...")
            top10_candidates = df_feat.sort_values(by='volume', ascending=False).head(10)

        total_selected = len(top10_candidates)
        print(f"🎯 [CRYPTO FILTER SUKSES] Mengirim {total_selected} Koin Kripto Murni ke AI untuk dianalisis.")

        prompt = f"""
        Bertindaklah sebagai Quant Trader. Evaluasi data koin kripto ini:
        {top10_candidates[['symbol', 'close', 'rsi', 'macd', 'obv', 'atr', 'tema_9']].to_string(index=False)}
        Pilih 1 koin TERBAIK untuk posisi LONG. Tentukan leverage (3,5,8,10) dan target_roe (15,20,25,30).
        Format JSON murni: {{"symbol": "NAMA", "action": "BUY", "entry": harga, "tp": harga, "sl": harga, "leverage": angka, "target_roe": angka, "reason": "alasan"}}
        """

        # --- 1. TOGETHER AI ENGINE ---
        if TOGETHER_API_KEY and "856bc" in TOGETHER_API_KEY:
            for model_name in TOGETHER_MODELS:
                try:
                    headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}", "Content-Type": "application/json"}
                    payload = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 300}
                    res = requests.post("https://api.together.xyz/v1/chat/completions", json=payload, headers=headers, timeout=12)
                    if res.status_code == 200:
                        parsed = extract_json(res.json()['choices'][0]['message']['content'])
                        print(f"🚀 [TOGETHER AI] ({model_name}) SUKSES Menganalisis Top 10!")
                        return parsed
                    else:
                        print(f"⚠️ [TOGETHER AI] Limit/Credit Exceeded ({res.status_code}). Beralih ke engine lain...")
                        break
                except Exception: pass

        # --- 2. GROQ ENGINE FALLBACK ---
        if VALID_GROQ_KEYS:
            print("🔄 [OTAK A] Berpindah ke Groq Engine Fallback...")
            for index, key in enumerate(VALID_GROQ_KEYS, start=1):
                for model_name in GROQ_MODELS:
                    try:
                        client = Groq(api_key=key)
                        response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_name, temperature=0.1, max_tokens=250)
                        parsed = extract_json(response.choices[0].message.content)
                        print(f"✅ [GROQ] Key #{index} ({model_name}) Sukses Menganalisis!")
                        return parsed
                    except Exception: pass

        # --- 3. GEMINI ENGINE FALLBACK ---
        if VALID_GEMINI_KEYS:
            print("🔄 [OTAK A] Berpindah ke Gemini Engine Fallback...")
            for index, g_key in enumerate(VALID_GEMINI_KEYS, start=1):
                for g_model in GEMINI_MODELS:
                    try:
                        client = genai.Client(api_key=g_key)
                        response = client.models.generate_content(model=g_model, contents=prompt, config=types.GenerateContentConfig(temperature=0.1))
                        parsed = extract_json(response.text)
                        print(f"✅ [GEMINI] Key #{index} ({g_model}) Sukses Menganalisis!")
                        return parsed
                    except Exception: pass

        # --- 4. HARDENED QUANT ALGORITHMIC FALLBACK (ANTI-MOGOK) ---
        print("⚡ [ANTI-MOGOK] Mengaktifkan Quant Engine Algoritma Murni Kripto...")
        best_candidate = top10_candidates.iloc[0]
        entry_p = float(best_candidate['close'])
        atr_val = float(best_candidate['atr']) if float(best_candidate['atr']) > 0 else entry_p * 0.015
        
        fallback_signal = {
            "symbol": str(best_candidate['symbol']),
            "action": "BUY",
            "entry": entry_p,
            "tp": round(entry_p + (atr_val * 3.0), 6),
            "sl": round(entry_p - (atr_val * 1.5), 6),
            "leverage": 5,
            "target_roe": 20.0,
            "reason": "Sinyal Quant Kripto Murni (Lonjakan Volume & Momentum RSI Terbaik)"
        }
        print(f"✅ [QUANT ENGINE] Berhasil menghasilkan sinyal mandiri untuk {fallback_signal['symbol']}!")
        return fallback_signal

    except Exception as e:
        print(f"❌ Error Otak A (Sistem): {e}")
        return None

if __name__ == "__main__":
    signal = run_ai_strategy()
    if signal:
        try:
            signal['symbol'] = signal['symbol'].strip().upper()
            if not signal['symbol'].endswith(':USDT'): signal['symbol'] += ':USDT'
            signal['entry'], signal['tp'], signal['sl'] = float(signal['entry']), float(signal['tp']), float(signal['sl'])
            signal['leverage'], signal['target_roe'] = int(signal.get('leverage', 5)), float(signal.get('target_roe', 20.0))
            signal['status'], signal['created_at'] = 'PENDING', datetime.now()
            
            pd.DataFrame([signal]).to_sql('trading_signals', con=engine, if_exists='append', index=False)
            print(f"🎯 [DB] Sinyal {signal['symbol']} (Lev: {signal['leverage']}x, Lock ROE: {signal['target_roe']}%) tersimpan (PENDING).")
        except Exception as e: print(f"❌ Error Menyimpan ke Database: {e}")