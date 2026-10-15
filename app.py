"""
app.py
Server lokal mini untuk Dashboard Monitoring Kurs Bank Indonesia - Nabel Sakha Group.

Fitur:
1. Web server lokal (http://localhost:5000)
2. Endpoint API Realtime:
   - GET /api/sync         : Trigger scraper BI realtime dan refresh data.js
   - GET /api/status       : Cek status koneksi dan server
   - POST /api/send-email  : Trigger pengiriman email laporan langsung
3. Kompatibel dengan semua browser modern tanpa dependensi eksternal (100% Python Standard Library).
"""

import os
import sys
import json
import socket
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Import modul internal
from sync_dashboard import sync_data
from main import run_immediate_send

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class KursAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):
        # Format log konsol yang rapi
        sys.stdout.write(f"[Server] {self.address_string()} - {format % args}\n")

    def end_headers(self):
        # Header CORS & No-Cache untuk mendukung realtime update
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/sync':
            self.handle_sync()
        elif path == '/api/status':
            self.send_json(200, {
                "status": "online",
                "service": "BI Exchange Rate Monitor",
                "company": "Nabel Sakha Group",
                "port": PORT
            })
        elif path == '/' or path == '':
            self.path = '/index.html'
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/sync':
            self.handle_sync()
        elif path == '/api/send-email':
            self.handle_send_email()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_sync(self):
        try:
            print("\n[Server API] [SYNC] Menerima instruksi pembaruan kurs realtime dari Web...")
            latest_data = sync_data()
            self.send_json(200, {
                "success": True,
                "message": "Data berhasil disinkronkan langsung dari Bank Indonesia",
                "tanggal_bi": latest_data.get('tanggal_bi'),
                "timestamp": latest_data.get('timestamp'),
                "rates": latest_data.get('rates')
            })
        except Exception as e:
            print(f"[Server API Error] Gagal sinkronisasi: {e}")
            self.send_json(500, {
                "success": False,
                "error": str(e)
            })

    def handle_send_email(self):
        try:
            print("\n[Server API] [EMAIL] Menerima instruksi pengiriman email laporan...")
            success = run_immediate_send()

            self.send_json(200, {
                "success": success,
                "message": "Email berhasil dikirim via SMTP" if success else "Pengiriman email belum berhasil. Periksa konfigurasi .env"
            })
        except Exception as e:
            self.send_json(500, {
                "success": False,
                "error": str(e)
            })

    def send_json(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def find_open_port(start=5000):
    for p in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', p)) != 0:
                return p
    return start

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def main():
    global PORT
    PORT = find_open_port(5000)
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, KursAppHandler)
    local_ip = get_local_ip()

    url_local = f"http://localhost:{PORT}"
    url_network = f"http://{local_ip}:{PORT}"
    print("=" * 65)
    print(f"[*] SERVER MONITORING KURS BI - NABEL SAKHA GROUP")
    print("=" * 65)
    print(f"[*] Dashboard (Laptop Anda)      : {url_local}")
    print(f"[*] Dashboard (Teman Satu Kantor): {url_network}")
    print(f"[*] Sinkronisasi Realtime API    : {url_local}/api/sync")
    print(f"[*] Tekan Ctrl+C untuk menghentikan server.")
    print("=" * 65 + "\n")

    # Buka otomatis di browser
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Server dimatikan oleh pengguna.")
        httpd.server_close()

if __name__ == '__main__':
    main()
