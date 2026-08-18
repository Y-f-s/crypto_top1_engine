import streamlit as st
import pandas as pd
import ccxt
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from datetime import datetime

# Konfigurasi Database & Environment (Live Mainnet)[cite: 3]
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Bismillah1313@localhost:5432/crypto_db")
engine = create_engine(DATABASE_URL)

st.set_page_config(
    page_title="Theta Digital Hub | AI Live Trading Command Center",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Ultra-Modern (RGB & Neon Green Theme)[cite: 3]
st.markdown("""
    <style>
        .stApp {
            background-color: #06090e; /* Latar belakang lebih gelap untuk menonjolkan RGB */
            color: #f3f4f6;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Efek Teks Gradient RGB */
        .rgb-text {
            background: linear-gradient(90deg, #00ff87, #60efff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
        }

        /* Kartu Metrik dengan Efek Hover Neon */
        .metric-card {
            background: linear-gradient(135deg, #111827 0%, #0b0f19 100%);
            border: 1px solid #1f2937;
            padding: 18px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            text-align: center;
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            border-color: #00ff87;
            box-shadow: 0 0 15px rgba(0, 255, 135, 0.2);
            transform: translateY(-2px);
        }
        
        .metric-title {
            font-size: 13px;
            color: #9ca3af;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 26px;
            font-weight: 800;
            margin-top: 4px;
        }
        
        /* Tab Menu Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #0b0f19;
            padding: 8px;
            border-radius: 12px;
            border: 1px solid #1f2937;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #111827;
            border-radius: 8px;
            padding: 10px 20px;
            color: #9ca3af;
            border: 1px solid #1f2937;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
            color: #000000 !important;
            border: none;
            box-shadow: 0 0 12px rgba(0, 255, 135, 0.4);
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #020408;
            border-right: 1px solid #1f2937;
        }
        
        /* Header Banner Glowing */
        .header-banner {
            background: linear-gradient(90deg, rgba(0,255,135,0.05) 0%, rgba(96,239,255,0.05) 100%);
            border: 1px solid rgba(0, 255, 135, 0.3);
            padding: 22px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: inset 0 0 20px rgba(0, 255, 135, 0.05);
        }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Koneksi Bybit LIVE MAINNET[cite: 3]
api_key = os.getenv('BYBIT_API_KEY') or os.getenv('BYBIT_TESTNET_API_KEY') or ''
api_secret = os.getenv('BYBIT_SECRET_KEY') or os.getenv('BYBIT_TESTNET_SECRET_KEY') or ''

exchange = ccxt.bybit({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'swap',
        'adjustForTimeDifference': True,
    },
    'apiKey': api_key,
    'secret': api_secret,
})

# Sidebar Kontrol Sistem[cite: 3]
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=56)
    st.markdown("### **Theta Hub v2.9 LIVE**")
    st.caption("AI Quant Production Terminal")
    st.markdown("---")
    
    if st.button("🔄 Refresh Data Real-Time", use_container_width=True):
        st.rerun()
        
    st.markdown("---")
    st.markdown("📡 **Status Jaringan**")
    if api_key:
        st.success("🟢 LIVE MAINNET AKTIF")
    else:
        st.warning("⚠️ API Key Belum Terdeteksi")
        
    st.info(f"⏱️ Waktu: {datetime.now().strftime('%H:%M:%S')}")
    st.markdown("---")
    st.caption("© 2026 Theta Digital Hub")

# Header Utama (Gradien RGB)[cite: 3]
st.markdown("""
    <div class="header-banner">
        <h1 style="margin:0; font-size: 28px;" class="rgb-text">🚀 Theta Digital Hub - LIVE Mainnet Command Center</h1>
        <p style="margin:5px 0 0 0; color: #a7f3d0; font-size: 14px;">Pemantauan posisi modal riil, eksekusi futures live di bursa utama, dan analitik strategi secara langsung.</p>
    </div>
""", unsafe_allow_html=True)

# Layout Utama (Tab Menu)[cite: 3]
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Posisi Live & Laba Rugi", 
    "📈 Analisis Kinerja", 
    "📜 Riwayat Perdagangan", 
    "🤖 Sinyal AI (Otak A)"
])

# --- TAB 1: POSISI LIVE & LABA RUGI ---
with tab1:
    st.subheader("Pemantauan Posisi Aktif di Bybit Live Mainnet")
    
    active_pos = []
    bybit_error = None
    
    if api_key and api_secret:
        try:
            exchange.load_markets()
            # Parameter category linear ditambahkan khusus Bybit V5 API / UTA
            positions = exchange.fetch_positions(params={'category': 'linear'})
            active_pos = [p for p in positions if float(p.get('contracts', 0) or 0) > 0]
        except Exception as e:
            bybit_error = str(e)
    else:
        bybit_error = "Kredensial API Key Live belum lengkap di file .env."

    try:
        df_trades_db = pd.read_sql("SELECT * FROM final_trades ORDER BY id DESC", engine)
    except Exception:
        df_trades_db = pd.DataFrame()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Posisi Aktif</div>
                <div class="metric-value" style="color: #60efff;">{len(active_pos)} Koin</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        total_unrealized = sum([float(p.get('unrealizedPnl', 0)) for p in active_pos]) if active_pos else 0.0
        pnl_color = "#00ff87" if total_unrealized >= 0 else "#ff4b4b"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Unrealized PnL (Live)</div>
                <div class="metric-value" style="color: {pnl_color};">${total_unrealized:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c3:
        total_planned = len(df_trades_db) if not df_trades_db.empty else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Perdagangan Disusun</div>
                <div class="metric-value" style="color: #fcd34d;">{total_planned}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Mode Sistem</div>
                <div class="metric-value rgb-text" style="font-size: 18px; margin-top: 8px;">🟢 LIVE PRODUCTION</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if bybit_error and api_key:
        st.error(f"⚠️ Peringatan Koneksi Live: {bybit_error}")

    if active_pos:
        formatted_pos = []
        for p in active_pos:
            entry_p = float(p.get('entryPrice', 0))
            mark_p = float(p.get('markPrice', 0))
            pnl_val = float(p.get('unrealizedPnl', 0))
            
            formatted_pos.append({
                'Simbol': p['symbol'],
                'Arah (Side)': '🟢 LONG' if p['side'].lower() == 'buy' else '🔴 SHORT',
                'Jumlah Kontrak': p['contracts'],
                'Harga Entry ($)': f"${entry_p:,.4f}",
                'Harga Mark ($)': f"${mark_p:,.4f}",
                'Unrealized PnL ($)': f"${pnl_val:,.2f}",
                'Tipe Margin': p.get('marginType', 'Cross').upper()
            })
            
        df_show_pos = pd.DataFrame(formatted_pos)
        st.dataframe(df_show_pos, use_container_width=True, hide_index=True)
    else:
        st.info("⚡ Tidak ada posisi terbuka di akun Live Mainnet saat ini (Pastikan izin API Key Bybit Anda sudah mengaktifkan izin pembacaan kontrak Futures/Derivatives).")

# --- TAB 2: ANALISIS KINERJA ---
with tab2:
    st.subheader("📊 Analisis Kinerja Quant Live & Strategi")
    try:
        df_perf = pd.read_sql("SELECT * FROM final_trades ORDER BY id ASC", engine)
        if not df_perf.empty:
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("#### **📈 Akumulasi Pertumbuhan Perdagangan**")
                df_perf['Cumulative_Trades'] = range(1, len(df_perf) + 1)
                st.line_chart(df_perf.set_index('id')['Cumulative_Trades'], height=280)
            with col_right:
                st.markdown("#### **⚖️ Distribusi Arah Posisi (LONG vs SHORT)**")
                direction_counts = df_perf['direction'].value_counts()
                st.bar_chart(direction_counts, height=280)
            st.markdown("---")
            col_a2, col_b2 = st.columns(2)
            with col_a2:
                st.markdown("#### **🪙 Koin Paling Sering Ditradingkan**")
                symbol_counts = df_perf['symbol'].value_counts().head(8)
                st.bar_chart(symbol_counts, height=260)
            with col_b2:
                st.markdown("#### **🎯 Rasio Risiko / Imbal Hasil (RRR)**")
                st.line_chart(df_perf['risk_reward_ratio'], height=260)
        else:
            st.info("📊 Belum ada data perdagangan tercatat di database.")
    except Exception as e:
        st.error(f"Gagal memuat analitik kinerja: {e}")

# --- TAB 3: RIWAYAT PERDAGANGAN ---
with tab3:
    st.subheader("📜 Log Riwayat Perdagangan Live (Database)")
    try:
        df_history = pd.read_sql("SELECT * FROM final_trades ORDER BY id DESC LIMIT 50", engine)
        if not df_history.empty:
            st.dataframe(df_history, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada riwayat perdagangan tercatat.")
    except Exception as e:
        st.info(f"Tabel riwayat perdagangan belum siap: {e}")

# --- TAB 4: SINYAL AI (OTAK A) ---
with tab4:
    st.subheader("🤖 Log Sinyal Keputusan Algoritma (Otak A)")
    try:
        df_signals = pd.read_sql("SELECT timestamp, symbol, timeframe, strategy_id, direction, strategy_score, details FROM strategy_signals ORDER BY timestamp DESC LIMIT 50", engine)
        if not df_signals.empty:
            st.dataframe(df_signals, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada sinyal strategi tercatat.")
    except Exception as e:
        st.info(f"Tabel sinyal strategi belum tersedia: {e}")