"""
config.py
Mengelola konfigurasi sistem (SMTP, kredensial, target penerima)
melalui environment variables atau file .env lokal.
"""

import os
from dotenv import load_dotenv

# Muat file .env jika ada
load_dotenv()

# Konfigurasi SMTP Pengirim
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_NAME = os.getenv("FROM_NAME", "Laporan Kurs - Nabel Sakha Group")
USE_TLS = os.getenv("USE_TLS", "true").lower() in ("true", "1", "yes")

# Target Penerima Email
# Default uji coba ke Samsul, nanti bisa diubah ke Ferrian
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "samsul@nabelsakha.com")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "samsul@nabelsakha.com")

def get_smtp_config():
    return {
        "host": SMTP_HOST,
        "port": SMTP_PORT,
        "user": SMTP_USER,
        "pass": SMTP_PASS,
        "from_name": FROM_NAME,
        "use_tls": USE_TLS
    }
