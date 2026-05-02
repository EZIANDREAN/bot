import requests
import xml.etree.ElementTree as ET

TOKEN = "8122135095:AAHwtq6eln4zWo6t6FN17WaA1ixJWc488-s"
CHAT_ID = "7069387382"


# =========================
# TELEGRAM
# =========================
def kirim(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# DATA SAHAM (TRADINGVIEW)
# =========================
def get_data():
    url = "https://scanner.tradingview.com/indonesia/scan"

    payload = {
        "filter": [
            {"left": "change", "operation": "greater", "right": 1},
            {"left": "volume", "operation": "greater", "right": 500000}
        ],
        "options": {"lang": "id"},
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name", "close", "change", "volume"]
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        data = r.json().get("data", [])
        return data
    except:
        return []


# =========================
# BERITA (GOOGLE NEWS RSS)
# =========================
def get_news(keyword):
    try:
        url = f"https://news.google.com/rss/search?q={keyword}+saham+indonesia"
        r = requests.get(url)
        root = ET.fromstring(r.content)

        items = root.findall(".//item")[:2]

        news_list = []
        for item in items:
            title = item.find("title").text
            news_list.append(title)

        return news_list
    except:
        return []


# =========================
# ANALISA + ALASAN
# =========================
def analisa(data):
    hasil = []

    if not data:
        return ["❌ Tidak ada data saham"]

    for d in data[:10]:
        try:
            item = d.get("d", [])

            if len(item) < 4:
                continue

            kode = item[0]
            change = item[2]
            volume = item[3]

            # ===== LOGIKA SINYAL =====
            if change >= 3 and volume >= 2000000:
                signal = "BUY 🔥"
                alasan = "- Breakout + volume spike"
            elif change >= 1.5:
                signal = "WAIT ⏳"
                alasan = "- Momentum mulai naik"
            else:
                signal = "AVOID ⚠️"
                alasan = "- Lemah / tidak ada minat beli"

            # ===== BERITA =====
            news = get_news(kode)
            news_text = "\n".join(news) if news else "Tidak ada berita terbaru"

            hasil.append(
                f"{kode} → {signal}\n"
                f"{change}% | Vol:{volume}\n\n"
                f"📌 Alasan:\n{alasan}\n\n"
                f"📰 Berita:\n{news_text}\n"
            )

        except:
            continue

    return hasil


# =========================
# MAIN
# =========================
def main():
    data = get_data()
    hasil = analisa(data)

    msg = "📊 SAHAM INDONESIA ANALISIS PRO+\n\n"

    for i, h in enumerate(hasil, 1):
        msg += f"{i}. {h}\n--------------------\n"

    kirim(msg)
    print("Selesai")

import time
import datetime

def is_10am():
    now = datetime.datetime.now()

    # JAM 10 PAGI (server time)
    return now.hour == 10 and now.minute == 0


while True:
    try:
        if is_10am():
            main()
            kirim("📢 Notifikasi jam 10 pagi sudah dikirim")

            # biar tidak spam dalam 1 menit
            time.sleep(60)

        else:
            print("Menunggu jam 10 pagi...")
            time.sleep(30)

    except Exception as e:
        print("ERROR LOOP:", e)
        time.sleep(60)

print("BOT SUDAH JALAN DI RAILWAY")
