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

def is_already_sent_today(report_type, tanggal_bi=None):
    """
    Mengecek apakah email jenis tertentu (NSG atau DQW) sudah pernah sukses terkirim
    untuk tanggal BI yang bersangkutan pada riwayat audit log.
    Mencegah pengiriman ganda pada jadwal cadangan maupun pemicu manual di luar jam kerja.
    """
    if not os.path.exists(LOG_FILE):
        return False
    
    target_date = (tanggal_bi or get_today_id_string()).lower().strip()
    target_type = report_type.upper()
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        for entry in logs:
            if entry.get("status") == "SUCCESS":
                entry_date = entry.get("tanggal_bi", "").lower().strip()
                # Jika log lama belum ada field report_type, anggap sebagai NSG
                entry_type = entry.get("report_type", "NSG").upper()
                if entry_type == target_type and (target_date in entry_date or entry_date in target_date):
                    return True
    except Exception:
        pass
    return False

def record_audit_log(tanggal_bi, recipients, status, message, duration, report_type="NSG"):
    """Mencatat bukti riwayat pengiriman ke data/audit_log.json beserta tipe laporannya."""
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
        "id": f"LOG-{now_wib.strftime('%Y%m%d-%H%M%S')}-{report_type.upper()}",
        "report_type": report_type.upper(),
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

def run_immediate_send(data=None, recipient=None, report_types=None, force=False):
    """
    Mengambil kurs terbaru, sinkron dashboard, dan mengirim email untuk tipe yang dipilih
    (default: kedua tipe NSG dan DQW dikirim berurutan).
    """
    start_time = time.time()
    target = recipient or config.RECIPIENT_EMAIL
    if report_types is None:
        report_types = ["NSG", "DQW"]

    print(f"\n==========================================")
    print(f"[*] Menjalankan Pengiriman Kurs Langsung")
    print(f"[*] Target Penerima : {target}")
    print(f"[*] Tipe Laporan    : {', '.join(report_types)}")
    print(f"[*] Mode Paksa      : {'YA' if force else 'TIDAK (Cek Anti-Dobel Aktif)'}")
    print(f"==========================================")

    if data is None:
        try:
            data = sync_data()
        except Exception as e:
            duration = time.time() - start_time
            err_msg = f"Gagal mengambil data dari Bank Indonesia: {e}"
            print(f"[!] {err_msg}")
            for rtype in report_types:
                record_audit_log("N/A", target, "FAILED", err_msg, duration, report_type=rtype)
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
        for rtype in report_types:
            record_audit_log(data['tanggal_bi'], target, "PENDING", "Data disinkronkan ke dashboard lokal (Kredensial SMTP belum diset)", time.time() - start_time, report_type=rtype)
        sync_data(latest_data=data)
        return False

    today_formatted = datetime.now(WIB).strftime("%d/%m/%Y")
    overall_success = True

    for rtype in report_types:
        rtype_upper = rtype.upper()
        # Cek pengaman tanggal: apakah sudah terkirim hari ini?
        if not force and is_already_sent_today(rtype_upper, data['tanggal_bi']):
            print(f"\n[+] Laporan [{rtype_upper}] untuk tanggal {data['tanggal_bi']} SUDAH TERKIRIM HARI INI.")
            print(f"    Pengiriman [{rtype_upper}] dilewati untuk mencegah email ganda.")
            continue

        subj = f"[KURS] {rtype_upper} - Laporan kurs hari ini {today_formatted}"
        
        send_start = time.time()
        try:
            success = send_kurs_email(data, target, smtp_cfg, subject=subj, report_type=rtype_upper)
            duration = time.time() - send_start
            if success:
                print(f"[+] Sukses! Email [{rtype_upper}] telah terkirim sempurna dalam {duration:.2f} detik.")
                record_audit_log(data['tanggal_bi'], target, "SUCCESS", f"Email [{rtype_upper}] berhasil dikirim via SMTP dalam {duration:.2f}s", duration, report_type=rtype_upper)
            else:
                overall_success = False
        except Exception as e:
            duration = time.time() - send_start
            print(f"[!] Gagal mengirim email [{rtype_upper}]: {e}")
            record_audit_log(data['tanggal_bi'], target, "FAILED", f"Gagal mengirim [{rtype_upper}]: {e}", duration, report_type=rtype_upper)
            overall_success = False

    # Update dashboard dengan log audit terbaru tanpa fetch ulang ke BI
    sync_data(latest_data=data)
    return overall_success

def run_smart_polling(max_minutes=45, interval_seconds=300):
    """
    Menjalankan pengecekan cerdas jam 08:00 WIB:
    - Mengecek apakah kedua email (NSG & DQW) untuk hari ini sudah terkirim.
    - Jika sudah terkirim keduanya, lewati (skip) agar tidak dobel pada jadwal cadangan / manual.
    - Menunggu data rilis di BI, lalu mengirimkan kedua email dan selesai.
    """
    today_str = get_today_id_string()
    
    # Cek apakah kedua laporan (NSG dan DQW) sudah berhasil dikirim untuk tanggal hari ini
    if is_already_sent_today("NSG", today_str) and is_already_sent_today("DQW", today_str):
        print(f"\n==========================================")
        print(f"[+] Kedua laporan kurs (NSG & DQW) untuk tanggal '{today_str}' sudah sukses terkirim hari ini.")
        print(f"[*] Jadwal otomatis dilewati untuk mencegah pengiriman email ganda.")
        print(f"==========================================")
        sync_data()
        return True

    print(f"\n==========================================")
    print(f"[*] Mode Smart Polling Aktif (NSG & DQW)")
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
                print(f"[+] DATA HARI INI TELAH TERBIT! Mengirim email NSG & DQW sekarang...")
                return run_immediate_send(data=data, report_types=["NSG", "DQW"])
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
    return run_immediate_send(data=last_fetched_data, report_types=["NSG", "DQW"])

def main():
    parser = argparse.ArgumentParser(description="Otomasi Laporan Kurs BI Nabel Sakha Group (NSG & DQW)")
    parser.add_argument("--now", action="store_true", help="Kirim email sekarang langsung tanpa polling")
    parser.add_argument("--poll", action="store_true", help="Jalankan mode smart polling jam 08:00 WIB")
    parser.add_argument("--sync", action="store_true", help="Sinkronkan data realtime BI ke dashboard lokal saja")
    parser.add_argument("--to", type=str, help="Email tujuan spesifik (opsional)")
    parser.add_argument("--type", type=str, choices=["ALL", "NSG", "DQW"], default="ALL", help="Pilih tipe laporan (ALL, NSG, atau DQW)")
    parser.add_argument("--force", action="store_true", help="Paksa kirim email meskipun sudah pernah terkirim hari ini")
    args = parser.parse_args()

    selected_types = ["NSG", "DQW"] if args.type == "ALL" else [args.type]

    success = True
    if args.sync:
        sync_data()
    elif args.poll:
        success = run_smart_polling()
    else:
        success = run_immediate_send(recipient=args.to, report_types=selected_types, force=args.force)

    if not success and not args.sync:
        sys.exit(1)

if __name__ == "__main__":
    main()
