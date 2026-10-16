"""
main.py
Program utama otomasi Kurs Transaksi Bank Indonesia untuk Nabel Sakha Group.
Mendukung:
- Pengiriman instan (--now) untuk pengujian manual.
- Mode Smart Polling (--poll) untuk jadwal otomatis jam 08:00 WIB.
- Sinkronisasi otomatis ke dashboard lokal (data/data.js).
- Pencatatan log audit pengiriman ke data/audit_log.json.
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime, timezone, timedelta
import config
from scraper import get_latest_kurs_data
from mailer import send_kurs_email
from sync_dashboard import sync_data, LOG_FILE

WIB = timezone(timedelta(hours=7))

# Kamus nama bulan Indonesia
BULAN_ID = {
    1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
    5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
    9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
}

def get_today_id_string():
    now = datetime.now(WIB)
    return f"{now.day} {BULAN_ID[now.month]} {now.year}"

def is_already_sent_today():
    """Mengecek apakah email untuk tanggal hari ini sudah pernah berhasil dikirim."""
    today_str = get_today_id_string()
    now_wib = datetime.now(WIB).strftime("%d/%m/%Y")
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            for entry in logs:
                if entry.get("status") == "SUCCESS":
                    if today_str.lower() in entry.get("tanggal_bi", "").lower():
                        return True
                    if entry.get("timestamp", "").startswith(now_wib):
                        return True
        except Exception:
            pass
    return False

def record_audit_log(tanggal_bi, recipients, status, message, duration):
    """Mencatat bukti riwayat pengiriman ke data/audit_log.json."""
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except Exception:
            logs = []

    now_wib = datetime.now(WIB)
    rec_list = [r.strip() for r in recipients.split(',') if r.strip()]
    new_entry = {
        "id": f"LOG-{now_wib.strftime('%Y%m%d-%H%M%S')}",
        "tanggal_bi": tanggal_bi,
        "timestamp": now_wib.strftime("%d/%m/%Y %H:%M:%S WIB"),
        "recipients": rec_list,
        "status": status,
        "status_code": 200 if status == "SUCCESS" else 500,
        "message": message,
        "duration_seconds": round(duration, 2)
    }

    logs.insert(0, new_entry)
    # Simpan 50 riwayat terakhir
    logs = logs[:50]
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def run_immediate_send(data=None, recipient=None):
    """Mengambil kurs terbaru, sinkron dashboard, dan mengirim email."""
    start_time = time.time()
    target = recipient or config.RECIPIENT_EMAIL
    print(f"\n==========================================")
    print(f"[*] Menjalankan Pengiriman Kurs Langsung")
    print(f"[*] Target Penerima: {target}")
    print(f"==========================================")

    if data is None:
        try:
            data = sync_data()
        except Exception as e:
            duration = time.time() - start_time
            err_msg = f"Gagal mengambil data dari Bank Indonesia: {e}"
            print(f"[!] {err_msg}")
            record_audit_log("N/A", target, "FAILED", err_msg, duration)
            return False
    else:
        # Gunakan data yang sudah diambil agar tidak memanggil website BI dua kali
        sync_data(latest_data=data)

    print(f"[+] Data BI: {data['tanggal_bi']} ({data['timestamp']})")
    for code, val in data['rates'].items():
        print(f"    - {code:4} | Jual: {val['jual_str']} | Beli: {val['beli_str']} | Tengah: {val['tengah_str']} | Tren: {val['trend_text']}")

    smtp_cfg = config.get_smtp_config()
    if not smtp_cfg['user'] or not smtp_cfg['pass']:
        print("\n[!] PERINGATAN: Kredensial SMTP belum diisi di file .env!")
        print("    Data dashboard lokal berhasil disinkronkan, namun email belum dikirim.")
        record_audit_log(data['tanggal_bi'], target, "PENDING", "Data disinkronkan ke dashboard lokal (Kredensial SMTP belum diset)", time.time() - start_time)
        sync_data(latest_data=data)
        return False

    today_formatted = datetime.now(WIB).strftime("%d/%m/%Y")
    subject = f"[KURS] Laporan kurs hari ini {today_formatted}"

    try:
        success = send_kurs_email(data, target, smtp_cfg, subject=subject)
        duration = time.time() - start_time
        if success:
            print(f"[+] Sukses! Email telah terkirim sempurna dalam {duration:.2f} detik.")
            record_audit_log(data['tanggal_bi'], target, "SUCCESS", f"Email berhasil dikirim via SMTP dalam {duration:.2f}s", duration)
            sync_data(latest_data=data) # Update dashboard dengan log audit terbaru tanpa fetch ulang ke BI
        return success
    except Exception as e:
        duration = time.time() - start_time
        print(f"[!] Gagal mengirim email: {e}")
        record_audit_log(data['tanggal_bi'], target, "FAILED", f"Gagal mengirim: {e}", duration)
        sync_data(latest_data=data)
        return False

def run_smart_polling(max_minutes=45, interval_seconds=300):
    """
    Menjalankan pengecekan cerdas jam 08:00 WIB:
    - Mengecek apakah tanggal data di web BI sudah berganti ke tanggal hari ini.
    - Jika belum, tidur 5 menit lalu cek lagi (hingga max_minutes).
    - Begitu rilis, kirimkan email satu kali dan selesai.
    """
    today_str = get_today_id_string()
    
    # Cek apakah hari ini sudah pernah berhasil kirim email (mencegah email ganda pada jadwal cadangan)
    if is_already_sent_today():
        print(f"\n==========================================")
        print(f"[+] Laporan kurs hari ini ({today_str}) SUDAH BERHASIL dikirim sebelumnya.")
        print(f"[*] Jadwal cadangan otomatis dilewati untuk mencegah pengiriman ganda.")
        print(f"==========================================")
        sync_data()
        return True

    print(f"\n==========================================")
    print(f"[*] Mode Smart Polling Aktif")
    print(f"[*] Menunggu rilis data BI untuk: {today_str}")
    print(f"==========================================")

    start_time = time.time()
    attempt = 1
    last_fetched_data = None

    while (time.time() - start_time) < (max_minutes * 60):
        print(f"\n[Attempt {attempt}] Mengecek tanggal rilis di bi.go.id...")
        try:
            data = get_latest_kurs_data()
            last_fetched_data = data
            bi_date = data['tanggal_bi']
            print(f"    Tanggal di BI saat ini : '{bi_date}'")
            print(f"    Target tanggal hari ini: '{today_str}'")

            if today_str.lower() in bi_date.lower():
                print(f"[+] DATA HARI INI TELAH TERBIT! Mengirim email sekarang...")
                return run_immediate_send(data=data)
            else:
                print(f"[-] Data hari ini belum dirilis oleh BI.")
                print(f"    Menunggu {interval_seconds // 60} menit sebelum pengecekan berikutnya...")
                time.sleep(interval_seconds)
                attempt += 1

        except Exception as e:
            print(f"[!] Error saat mengambil data: {e}")
            time.sleep(interval_seconds)
            attempt += 1

    print("\n[!] Waktu tunggu batas maksimal tercapai (08:45 WIB).")
    print("    Mengirim data kurs terakhir yang tersedia...")
    return run_immediate_send(data=last_fetched_data)

def main():
    parser = argparse.ArgumentParser(description="Otomasi Laporan Kurs BI Nabel Sakha Group")
    parser.add_argument("--now", action="store_true", help="Kirim email sekarang langsung tanpa polling")
    parser.add_argument("--poll", action="store_true", help="Jalankan mode smart polling jam 08:00 WIB")
    parser.add_argument("--sync", action="store_true", help="Sinkronkan data realtime BI ke dashboard lokal saja")
    parser.add_argument("--to", type=str, help="Email tujuan spesifik (opsional)")
    args = parser.parse_args()

    success = True
    if args.sync:
        sync_data()
    elif args.poll:
        success = run_smart_polling()
    else:
        success = run_immediate_send(recipient=args.to)

    if not success and not args.sync:
        sys.exit(1)

if __name__ == "__main__":
    main()
