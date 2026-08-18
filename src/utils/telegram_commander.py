import time

def main():
    print("📡 [TELEGRAM COMMANDER] Modul kontrol jarak jauh siap siaga...")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Telegram Commander dihentikan.")

if __name__ == "__main__":
    main()