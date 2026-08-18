# ==========================================
# INISIALISASI & KONFIGURASI MULTI-KEY
# ==========================================
print("🧠 [OTAK A] Memulai Inisialisasi AI dengan Multi-Key Auto-Switching...", flush=True)

load_dotenv(find_dotenv())
engine = create_engine(os.getenv("DATABASE_URL"))

# Pool API Key Groq (AI-3 s.d AI-10)
GROQ_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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"
]

# Pool API Key Gemini (Utama + Cadangan Barumu)
GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY"), # Key Utama (.env)
    "AQ.Ab8RN6Ijz1QLx-nLBsLJyQum-9TT7WAP8L_ZIvmHbUKQuHABDQ", # cryptoAI2
    "AQ.Ab8RN6IaLfzaE9TqhELwruPfNYoPw7laAMh17EynlMSa2Jictg"  # cryptoAI
]