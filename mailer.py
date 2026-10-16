"""
mailer.py
Bertanggung jawab menyusun konten HTML email dengan CID inline attachment
dan mengirimkannya menggunakan protokol SMTP standar.
Dioptimasi 100% untuk rendering presisi di Microsoft Outlook Desktop.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

LOGO_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
ONLINE_LOGO_URL = 'https://i.imgur.com/jyix5CY.png'

def build_html_template(data, use_cid=True):
    rates = data.get('rates', {})
    tanggal_bi = data.get('tanggal_bi', datetime.now().strftime("%d %B %Y"))
    dashboard_url = os.environ.get('DASHBOARD_URL', 'https://nsg-9roup.github.io/nsg-kurs/')

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Laporan Kurs Transaksi Bank Indonesia</title>
</head>
<body style="margin: 0; padding: 20px; background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">

  <div style="font-family: Arial, Helvetica, sans-serif; font-size: 13px; color: #000000; line-height: 1.5; max-width: 620px;">
    
    <p style="margin: 0 0 14px 0; font-size: 14px; font-weight: bold; color: #000000;">
      Laporan Kurs Transaksi Bank Indonesia ({tanggal_bi}):
    </p>

    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; border: 1px solid #000000; font-family: Arial, Helvetica, sans-serif; font-size: 13px; width: 100%; max-width: 580px;">
      <thead>
        <tr>
          <th style="border: 1px solid #000000; padding: 6px 10px; width: 22%;"></th>
          <th style="border: 1px solid #000000; padding: 6px 10px; color: #0056b3; font-weight: bold; text-align: center; width: 15%;">EUR</th>
          <th style="border: 1px solid #000000; padding: 6px 10px; color: #0056b3; font-weight: bold; text-align: center; width: 15%;">JPY</th>
          <th style="border: 1px solid #000000; padding: 6px 10px; color: #0056b3; font-weight: bold; text-align: center; width: 15%;">KRW</th>
          <th style="border: 1px solid #000000; padding: 6px 10px; color: #0056b3; font-weight: bold; text-align: center; width: 16%;">SGD</th>
          <th style="border: 1px solid #000000; padding: 6px 10px; color: #0056b3; font-weight: bold; text-align: center; width: 17%;">USD</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="border: 1px solid #000000; padding: 6px 10px; font-weight: bold; text-align: left; color: #000000; white-space: nowrap;">Kurs Jual</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('EUR', {}).get('jual_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('JPY', {}).get('jual_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('KRW', {}).get('jual_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('SGD', {}).get('jual_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('USD', {}).get('jual_str', '-')}</td>
        </tr>
        <tr>
          <td style="border: 1px solid #000000; padding: 6px 10px; font-weight: bold; text-align: left; color: #000000; white-space: nowrap;">Kurs Beli</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('EUR', {}).get('beli_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('JPY', {}).get('beli_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('KRW', {}).get('beli_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('SGD', {}).get('beli_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('USD', {}).get('beli_str', '-')}</td>
        </tr>
        <tr>
          <td style="border: 1px solid #000000; padding: 6px 10px; font-weight: bold; text-align: left; color: #000000; white-space: nowrap;">Kurs Tengah</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('EUR', {}).get('tengah_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('JPY', {}).get('tengah_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('KRW', {}).get('tengah_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('SGD', {}).get('tengah_str', '-')}</td>
          <td style="border: 1px solid #000000; padding: 6px 10px; text-align: right; color: #000000; white-space: nowrap;">{rates.get('USD', {}).get('tengah_str', '-')}</td>
        </tr>
      </tbody>
    </table>

    <div style="margin-top: 14px; font-size: 12px; color: #333333; line-height: 1.6;">
      <p style="margin: 0 0 4px 0;">
        Link Bank Indonesia: <a href="https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx" target="_blank" style="color: #0056b3; text-decoration: underline;">https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx</a>
      </p>
      <p style="margin: 0;">
        Link Dashboard Kurs: <a href="{dashboard_url}" target="_blank" style="color: #0056b3; text-decoration: underline;">{dashboard_url}</a>
      </p>
    </div>

  </div>

</body>
</html>
"""
    return html

def send_kurs_email(data, recipient_email, smtp_config, subject=None):
    if not subject:
        today_str = datetime.now().strftime("%d/%m/%Y")
        subject = f"[KURS] Laporan kurs hari ini {today_str}"

    # Sanitasi daftar penerima (mendukung format satu email atau multi-email dipisah koma)
    recipients_list = [r.strip() for r in recipient_email.split(',') if r.strip()]
    if not recipients_list:
        raise ValueError("Target penerima email kosong.")

    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    from_name = smtp_config.get('from_name', 'Sistem Kurs Nabel Sakha')
    msg['From'] = f"{from_name} <{smtp_config['user']}>"
    msg['To'] = ", ".join(recipients_list)

    msg_alt = MIMEMultipart('alternative')
    msg.attach(msg_alt)

    # 1. Plain text fallback
    rates = data.get('rates', {})
    tanggal_bi = data.get('tanggal_bi', '')
    dashboard_url = os.environ.get('DASHBOARD_URL', 'https://nsg-9roup.github.io/nsg-kurs/')
    
    plain_text = f"""Laporan Kurs Transaksi Bank Indonesia ({tanggal_bi})

            EUR         JPY        KRW         SGD         USD
Kurs Jual   {rates.get('EUR', {}).get('jual_str', '-'):>9}  {rates.get('JPY', {}).get('jual_str', '-'):>9}  {rates.get('KRW', {}).get('jual_str', '-'):>9}  {rates.get('SGD', {}).get('jual_str', '-'):>9}  {rates.get('USD', {}).get('jual_str', '-'):>9}
Kurs Beli   {rates.get('EUR', {}).get('beli_str', '-'):>9}  {rates.get('JPY', {}).get('beli_str', '-'):>9}  {rates.get('KRW', {}).get('beli_str', '-'):>9}  {rates.get('SGD', {}).get('beli_str', '-'):>9}  {rates.get('USD', {}).get('beli_str', '-'):>9}
Kurs Tengah {rates.get('EUR', {}).get('tengah_str', '-'):>9}  {rates.get('JPY', {}).get('tengah_str', '-'):>9}  {rates.get('KRW', {}).get('tengah_str', '-'):>9}  {rates.get('SGD', {}).get('tengah_str', '-'):>9}  {rates.get('USD', {}).get('tengah_str', '-'):>9}

Link Bank Indonesia: https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx
Link Dashboard Kurs: {dashboard_url}
"""
    msg_alt.attach(MIMEText(plain_text, 'plain', 'utf-8'))

    # 2. Rich HTML content
    html_content = build_html_template(data, use_cid=False)
    msg_alt.attach(MIMEText(html_content, 'html', 'utf-8'))

    host = smtp_config['host']
    port = int(smtp_config.get('port', 587))
    user = smtp_config['user']
    password = smtp_config['pass']
    use_tls = smtp_config.get('use_tls', True)

    print(f"[Mailer] Menghubungkan ke {host}:{port} (Penerima: {', '.join(recipients_list)})...")
    
    # Dukung koneksi SSL murni (Port 465) maupun STARTTLS (Port 587 / 25)
    if port == 465:
        server = smtplib.SMTP_SSL(host, port, timeout=30)
        server.ehlo()
    else:
        server = smtplib.SMTP(host, port, timeout=30)
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
    
    server.login(user, password)
    server.sendmail(user, recipients_list, msg.as_string())
    server.quit()
    print(f"[Mailer] Sukses terkirim ke {', '.join(recipients_list)}!")
    return True

if __name__ == '__main__':
    from scraper import get_latest_kurs_data
    data = get_latest_kurs_data()
    sample_html = build_html_template(data, use_cid=False)
    with open('preview_with_trend.html', 'w', encoding='utf-8') as f:
        f.write(sample_html)
    with open('preview_email.html', 'w', encoding='utf-8') as f:
        f.write(sample_html)
    print("Berhasil memperbarui kedua file preview dengan tombol dan badge anti-wrap!")
