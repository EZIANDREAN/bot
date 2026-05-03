import requests
import xml.etree.ElementTree as ET
import time
import datetime
import re
from zoneinfo import ZoneInfo

TOKEN = "8122135095:AAHwtq6eln4zWo6t6FN17WaA1ixJWc488-s"
CHAT_ID = "7069387382"

# =========================
# TIMEZONE LOMBOK (WITA UTC+8)
# =========================
WITA = ZoneInfo("Asia/Makassar")


# =========================
# TELEGRAM
# =========================
def kirim(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("ERROR TELEGRAM:", e)


# =========================
# DATA SAHAM
# =========================
def get_data():
    url = "https://scanner.tradingview.com/indonesia/scan"

    payload = {
        "filter": [
            {"left": "change", "operation": "greater", "right": 1},
            {"left": "volume", "operation": "greater", "right": 500000}
        ],
        "columns": ["name", "close", "change", "volume"]
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json().get("data", [])
    except:
        return []


# =========================
# NEWS
# =========================
def get_news(keyword):
    try:
        url = f"https://news.google.com/rss/search?q={keyword}+saham+indonesia"
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)
        items = root.findall(".//item")[:3]
        return [i.find("title").text for i in items]
    except:
        return []


# =========================
# ANALISA BERITA
# =========================
def analisa_berita(news_list):
    hasil = {
        "laba_profit": [],
        "rugi": [],
        "dividen": [],
        "akuisisi": [],
        "utang": [],
        "penurunan": [],
        "dilusi": [],
        "right_issue": []
    }

    for n in news_list:
        t = n.lower()
        angka = re.findall(r'(\d+[.,]?\d*\s?(triliun|miliar|juta|%|rb)?)', t)

        item = n + (" | 📊 " + ", ".join([a[0] for a in angka[:2]]) if angka else "")

        if "laba" in t or "profit" in t:
            hasil["laba_profit"].append(item)
        if "rugi" in t or "loss" in t:
            hasil["rugi"].append(item)
        if "dividen" in t:
            hasil["dividen"].append(item)
        if "akuisisi" in t:
            hasil["akuisisi"].append(item)
        if "utang" in t or "debt" in t:
            hasil["utang"].append(item)
        if "turun" in t or "penurunan" in t:
            hasil["penurunan"].append(item)
        if "dilusi" in t:
            hasil["dilusi"].append(item)
        if "right issue" in t or "rights issue" in t:
            hasil["right_issue"].append(item)

    return hasil


# =========================
# FORMAT
# =========================
def fmt(title, data):
    if not data:
        return f"{title}: Tidak ada"
    return f"{title}:\n- " + "\n- ".join(data[:2])


def format_right_issue(data):
    if not data:
        return "🔄 RIGHT ISSUE: Tidak ada"

    hasil = "🔄 RIGHT ISSUE (WASPADA DILUSI):\n"
    for d in data[:2]:
        hasil += f"- 📰 {d}\n  ⚠️ Potensi dilusi & tekanan harga\n"
    return hasil


# =========================
# ANALISA UTAMA
# =========================
def main():
    data = get_data()
    hasil = []

    for d in data[:10]:
        try:
            item = d.get("d", [])
            if len(item) < 4:
                continue

            kode = item[0]
            change = item[2]
            volume = item[3]

            if change >= 3 and volume >= 2000000:
                signal = "BUY 🔥"
            elif change >= 1.5:
                signal = "WAIT ⏳"
            else:
                signal = "AVOID ⚠️"

            news = get_news(kode)
            kategori = analisa_berita(news)

            msg = (
                f"📊 {kode}\n"
                f"Signal: {signal}\n"
                f"Change: {change}% | Vol: {volume}\n\n"
                f"🧠 FUNDAMENTAL BERITA\n\n"
                f"{fmt('📈 LABA/PROFIT', kategori['laba_profit'])}\n\n"
                f"{fmt('📉 RUGI', kategori['rugi'])}\n\n"
                f"{fmt('💰 DIVIDEN', kategori['dividen'])}\n\n"
                f"{fmt('🏢 AKUISISI', kategori['akuisisi'])}\n\n"
                f"{fmt('💳 UTANG', kategori['utang'])}\n\n"
                f"{fmt('📉 PENURUNAN', kategori['penurunan'])}\n\n"
                f"{fmt('⚠️ DILUSI', kategori['dilusi'])}\n\n"
                f"{format_right_issue(kategori['right_issue'])}\n"
            )

            hasil.append(msg)

        except:
            continue

    full_msg = "📊 AI SAHAM LOMBOK SCANNER\n\n" + "\n----------------\n".join(hasil)
    kirim(full_msg)
    print("Kirim sukses")


# =========================
# SCHEDULER WITA (LOMBOK)
# =========================
JADWAL = ["10:00", "11:30", "14:30", "15:00"]
sudah_kirim = set()

while True:
    try:
        now = datetime.datetime.now(WITA).strftime("%H:%M")

        # reset harian
        if now == "00:00":
            sudah_kirim.clear()

        if now in JADWAL and now not in sudah_kirim:
            print(f"Kirim jam {now} WITA")
            main()
            sudah_kirim.add(now)
            time.sleep(60)

        else:
            print("Menunggu jadwal WITA...")
            time.sleep(20)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(60)
