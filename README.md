# Otomasi Laporan Kurs Transaksi Bank Indonesia
### Nabel Sakha Group

Sistem otomatisasi harian untuk mengambil kurs resmi Bank Indonesia (USD, EUR, JPY, KRW, SGD), menghitung normalisasi satuan dan kurs tengah, menampilkan tren pergerakan harian, dan mengirimkan laporan berformat elegan ke email penerima tepat setiap hari kerja pukul 08:00 WIB.

---

## 🚀 Fitur Unggulan

1. **Akurat Sesuai Bank Indonesia:** Mengambil data kurs transaksi resmi langsung dari `bi.go.id`.
2. **Normalisasi Khusus JPY:** Kurs JPY per 100 unit otomatis dinormalisasi menjadi per 1 unit.
3. **Kalkulasi Kurs Tengah & Tren:** Menghitung rata-rata `(Jual + Beli) / 2` dan menghitung tren kenaikan (`▲`) atau penurunan (`▼`) dibanding hari kerja sebelumnya.
4. **Desain Outlook-Bulletproof:** Tampilan modern, bersih, beridentitas resmi *Nabel Sakha Group* (Merah-Orange) dengan logo resmi.
5. **Smart Polling 08:00 WIB:** Cerdas mengecek rilis data BI. Jika jam 08:00 belum rilis, script menunggu dan mengecek berkala sampai data resmi hari ini terbit sebelum mengirim email.
6. **Otomatis Tanpa Server (GitHub Actions):** Berjalan di cloud GitHub secara gratis setiap Senin–Jumat jam 08:00 WIB tanpa perlu komputer menyala.

---

## 📁 Struktur File

```text
├── assets/
│   └── logo.png              # Logo resmi Nabel Sakha Group (Inline CID)
├── data/
│   └── history.json          # Database riwayat kurs untuk kalkulasi tren
├── .github/workflows/
│   └── daily_kurs.yml        # Jadwal otomatis GitHub Actions (08:00 WIB)
├── config.py                 # Manajemen konfigurasi dan environment
├── scraper.py                # Engine scraping dan kalkulasi data BI
├── mailer.py                 # Generator template HTML dan pengirim SMTP
├── main.py                   # Entry point aplikasi (CLI & Scheduler)
├── preview_with_trend.html   # Preview tampilan email lengkap
├── requirements.txt          # Dependensi Python
├── .env.example              # Contoh konfigurasi kredensial email
└── README.md                 # Dokumentasi panduan
```

---

## 🛠️ Cara Uji Coba di Komputer Lokal

1. Salin file `.env.example` menjadi `.env`:
   ```bash
   cp .env.example .env
   ```
2. Buka `.env` dan isi akun pengirim email Anda (`SMTP_USER` dan `SMTP_PASS`).
3. Jalankan pengiriman email uji coba sekarang:
   ```bash
   python main.py --now
   ```
   *(Atau tentukan penerima spesifik):*
   ```bash
   python main.py --now --to samsul@nabelsakha.com
   ```

---

## ☁️ Cara Pasang di GitHub Actions (Otomatis Jam 08:00 WIB)

1. Buat repository baru di GitHub (bisa diset **Private** agar aman).
2. Push seluruh folder project ini ke repository tersebut:
   ```bash
   git init
   git add .
   git commit -m "Inisialisasi sistem otomasi kurs BI Nabel Sakha"
   git branch -M main
   git remote add origin https://github.com/USERNAME/REPO-KURS.git
   git push -u origin main
   ```
3. Di halaman repository GitHub Anda:
   * Masuk ke **Settings** > **Secrets and variables** > **Actions**.
   * Klik tombol **New repository secret**, tambahkan:
     * `SMTP_HOST`: `smtp.office365.com` (atau `smtp.gmail.com`)
     * `SMTP_PORT`: `587`
     * `SMTP_USER`: Email pengirim Anda
     * `SMTP_PASS`: Password atau App Password email
     * `RECIPIENT_EMAIL`: `samsul@nabelsakha.com` (nanti bisa diganti `ferri@nabelsakha.com`)
     * `FROM_NAME`: `Laporan Kurs - Nabel Sakha Group`
4. Selesai! Script akan otomatis berjalan setiap **Senin s/d Jumat pukul 08:00 WIB (01:00 UTC)**. Anda juga bisa menekan tombol **"Run workflow"** di tab **Actions** kapanpun untuk tes jalan langsung di cloud.
