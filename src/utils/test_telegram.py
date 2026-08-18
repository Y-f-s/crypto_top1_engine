import os
import sys
from dotenv import load_dotenv, find_dotenv

# Memastikan modul src terbaca
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.utils.telegram_notifier import send_telegram_alert

load_dotenv(find_dotenv())

if __name__ == "__main__":
    print("📲 Mengirim pesan uji coba ke Telegram...")
    pesan = "🚨 **TES SISTEM THETA DIGITAL HUB**\nNotifikasi Telegram berhasil terhubung dan siap mengawal bot Sniper Anda 24 Jam!"
    
    if send_telegram_alert(pesan):
        print("✅ Pesan tes BERHASIL dikirim! Cek aplikasi Telegram di HP Anda.")
    else:
        print("❌ Gagal mengirim pesan. Periksa koneksi internet atau token Anda.")