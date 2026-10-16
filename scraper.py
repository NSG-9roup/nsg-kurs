"""
scraper.py
Mengambil data kurs transaksi resmi dari Bank Indonesia (bi.go.id),
menormalisasi nilai per 1 satuan valuta asing, menghitung kurs tengah,
serta membandingkannya dengan data kurs sebelumnya untuk menghitung tren (delta).
"""

import urllib.request
import ssl
import re
import json
import os
import time
from datetime import datetime, timezone, timedelta

TARGET_CURRENCIES = ['EUR', 'JPY', 'KRW', 'SGD', 'USD']
BI_URL = 'https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx'
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'data', 'history.json')
WIB = timezone(timedelta(hours=7))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
}

MONTH_MAP = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
    'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
    'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
}

def parse_date_key(date_str):
    """
    Mengubah format tanggal Indonesia (contoh: '15 Oktober 2026') menjadi
    objek datetime agar pengurutan riwayat (history) 100% akurat secara kronologis,
    bukan pengurutan string alfabetis yang salah.
    """
    if not date_str:
        return datetime.min.replace(tzinfo=WIB)
    try:
        parts = date_str.strip().split()
        if len(parts) >= 3:
            day = int(parts[0])
            month = MONTH_MAP.get(parts[1].lower(), 1)
            year = int(parts[2])
            return datetime(year, month, day, tzinfo=WIB)
    except Exception:
        pass
    return datetime.min.replace(tzinfo=WIB)

def fetch_bi_html(max_retries=3, timeout=35):
    """Mengambil HTML halaman kurs BI dengan mekanisme retry."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(BI_URL, headers=HEADERS)
    last_err = None

    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                return resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            last_err = e
            print(f"[Scraper] Percobaan {attempt}/{max_retries} gagal: {e}")
            if attempt < max_retries:
                time.sleep(5)

    raise RuntimeError(f"Gagal mengakses Bank Indonesia setelah {max_retries} percobaan: {last_err}")

def parse_bi_date(html):
    """Mengekstrak tanggal Pembaruan Terakhir yang tertera di website BI."""
    match = re.search(r'Update Terakhir(?:&nbsp;|\s*)<span>(.*?)</span>', html, re.IGNORECASE)
    if match:
        clean = match.group(1).replace('&nbsp;', ' ').replace('\xa0', ' ').strip()
        return clean
    
    # Fallback search jika elemen span berubah
    dates = re.findall(r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})', html, re.IGNORECASE)
    if dates:
        return dates[-1].strip()
    
    now_wib = datetime.now(WIB)
    bulan_id = list(MONTH_MAP.keys())[now_wib.month - 1].capitalize()
    return f"{now_wib.day} {bulan_id} {now_wib.year}"

def format_idr(num):
    """Format angka ke standar Indonesia: pemisah ribuan titik (.), desimal koma (,)."""
    parts = f"{num:,.2f}".split('.')
    integer_part = parts[0].replace(',', '.')
    decimal_part = parts[1]
    return f"{integer_part},{decimal_part}"

def format_sap(num):
    """Format angka untuk SAP: tanpa titik ribuan, desimal koma (,), tanpa ,00 jika bilangan bulat."""
    if num is None:
        return '-'
    s = f"{num:.2f}".replace('.', ',')
    if s.endswith(',00'):
        return s[:-3]
    return s

def load_history():
    """Membaca histori kurs sebelumnya yang diurutkan secara kronologis."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Urutkan berdasarkan tanggal kronologis
                sorted_keys = sorted(data.keys(), key=parse_date_key)
                return {k: data[k] for k in sorted_keys}
        except Exception:
            return {}
    return {}

def save_history(date_str, rates):
    """Menyimpan data kurs hari ini ke riwayat histori secara kronologis."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history = load_history()
    history[date_str] = rates
    # Simpan maksimal 30 hari riwayat terakhir berdasarkan urutan tanggal nyata
    sorted_keys = sorted(history.keys(), key=parse_date_key)[-30:]
    trimmed = {k: history[k] for k in sorted_keys}
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)

def get_latest_kurs_data():
    """
    Fungsi utama untuk scraping data kurs BI, normalisasi, dan kalkulasi tren.
    Returns:
        dict: {
            'tanggal_bi': str,
            'timestamp': str,
            'rates': {
                'USD': {
                    'jual': float, 'jual_str': str,
                    'beli': float, 'beli_str': str,
                    'tengah': float, 'tengah_str': str,
                    'delta': float, 'delta_pct': float,
                    'trend_icon': str, 'trend_class': str, 'trend_text': str
                },
                ...
            }
        }
    """
    html = fetch_bi_html()
    bi_date = parse_bi_date(html)
    
    rates = {}
    history = load_history()
    # Dapatkan kurs tanggal terakhir sebelum tanggal ini (kronologis)
    prev_dates = [d for d in sorted(history.keys(), key=parse_date_key) if d != bi_date]
    prev_rates = history[prev_dates[-1]] if prev_dates else {}

    # Cari tabel kurs di dalam HTML
    for m in re.finditer(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE):
        table_content = m.group(1)
        if 'Kurs Jual' in table_content and 'USD' in table_content:
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_content, re.DOTALL | re.IGNORECASE)
            for r in rows:
                tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL | re.IGNORECASE)
                clean = [re.sub(r'<[^>]+>', '', td).replace('&nbsp;', ' ').replace('\xa0', ' ').strip() for td in tds]
                if clean and clean[0] in TARGET_CURRENCIES:
                    code = clean[0]
                    # Sanitasi nilai unit (misal '100,00' atau '1')
                    raw_unit = clean[1].replace('.', '').replace(',', '.')
                    unit = float(raw_unit) if raw_unit else 1.0

                    raw_jual = float(clean[2].replace('.', '').replace(',', '.'))
                    raw_beli = float(clean[3].replace('.', '').replace(',', '.'))

                    # Normalisasi per 1 satuan (khusus JPY dibagi 100)
                    jual = raw_jual / unit
                    beli = raw_beli / unit
                    tengah = (jual + beli) / 2.0

                    # Hitung tren (selisih terhadap hari sebelumnya)
                    delta = 0.0
                    delta_pct = 0.0
                    trend_icon = '-'
                    trend_class = 'neutral'
                    trend_text = 'Tetap'

                    if code in prev_rates:
                        prev_tengah = prev_rates[code].get('tengah', tengah)
                        delta = tengah - prev_tengah
                        if prev_tengah > 0:
                            delta_pct = (delta / prev_tengah) * 100

                        if delta > 0.005:
                            trend_icon = '▲'
                            trend_class = 'up'
                            trend_text = f"+{format_idr(delta)} (+{delta_pct:.2f}%)"
                        elif delta < -0.005:
                            trend_icon = '▼'
                            trend_class = 'down'
                            trend_text = f"{format_idr(delta)} ({delta_pct:.2f}%)"
                        else:
                            trend_icon = '■'
                            trend_class = 'flat'
                            trend_text = "0,00 (0,00%)"

                    rates[code] = {
                        'jual': round(jual, 2),
                        'jual_str': format_idr(round(jual, 2)),
                        'jual_sap': format_sap(round(jual, 2)),
                        'beli': round(beli, 2),
                        'beli_str': format_idr(round(beli, 2)),
                        'beli_sap': format_sap(round(beli, 2)),
                        'tengah': round(tengah, 2),
                        'tengah_str': format_idr(round(tengah, 2)),
                        'tengah_sap': format_sap(round(tengah, 2)),
                        'delta': round(delta, 2),
                        'delta_pct': round(delta_pct, 2),
                        'trend_icon': trend_icon,
                        'trend_class': trend_class,
                        'trend_text': trend_text
                    }

    # Simpan hasil scraping hari ini ke histori secara kronologis
    if rates:
        save_history(bi_date, rates)

    now_wib = datetime.now(WIB)
    return {
        'tanggal_bi': bi_date,
        'timestamp': now_wib.strftime('%H:%M WIB'),
        'rates': rates
    }

if __name__ == '__main__':
    print("Mencoba mengambil data kurs BI...")
    data = get_latest_kurs_data()
    print(f"Tanggal BI : {data['tanggal_bi']} ({data['timestamp']})")
    for cur, val in data['rates'].items():
        icon = '^' if val['trend_icon'] == '▲' else ('v' if val['trend_icon'] == '▼' else '-')
        print(f"{cur:4} -> Jual: {val['jual_str']} | Beli: {val['beli_str']} | Tengah: {val['tengah_str']} | Tren: {icon} {val['trend_text']}")
