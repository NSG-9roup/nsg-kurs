"""
mailer.py
Bertanggung jawab menyusun konten HTML email dengan CID inline attachment
dan mengirimkannya menggunakan protokol SMTP standar.
Dioptimasi 100% untuk rendering presisi di Microsoft Outlook Desktop.
Format angka disesuaikan khusus agar kompatibel dengan sistem SAP.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
LOGO_PATH = os.path.join(ASSETS_DIR, 'logo.png')
BTN_BI_PATH = os.path.join(ASSETS_DIR, 'btn_bi.png')
BTN_DASHBOARD_PATH = os.path.join(ASSETS_DIR, 'btn_dashboard.png')

ONLINE_LOGO_URL = 'https://nsg-9roup.github.io/nsg-kurs/assets/logo.png'
ONLINE_BTN_BI_URL = 'https://nsg-9roup.github.io/nsg-kurs/assets/btn_bi.png'
ONLINE_BTN_DASHBOARD_URL = 'https://nsg-9roup.github.io/nsg-kurs/assets/btn_dashboard.png'

def format_sap(val):
    """
    Format angka khusus kompatibilitas SAP:
    - Tanpa pemisah ribuan titik (.)
    - Desimal menggunakan koma (,)
    - Jika bilangan bulat (.00), hilangkan ,00 (misal 17910)
    - Jika memiliki desimal, tampilkan 2 digit (misal 20235,09)
    """
    if val is None or val == '':
        return '-'
    if isinstance(val, (int, float)):
        s = f"{val:.2f}".replace('.', ',')
        if s.endswith(',00'):
            return s[:-3]
        return s
    
    val_str = str(val).replace('.', '')
    if val_str.endswith(',00'):
        return val_str[:-3]
    return val_str

def build_html_template(data, use_cid=True):
    rates = data.get('rates', {})
    tanggal_bi = data.get('tanggal_bi', datetime.now().strftime("%d %B %Y"))
    jam_update = data.get('timestamp', '08:00 WIB')
    dashboard_url = os.environ.get('DASHBOARD_URL', 'https://nsg-9roup.github.io/nsg-kurs/')

    logo_src = "cid:nsg_logo" if (use_cid and os.path.exists(LOGO_PATH)) else ONLINE_LOGO_URL
    btn_bi_src = "cid:btn_bi" if (use_cid and os.path.exists(BTN_BI_PATH)) else ONLINE_BTN_BI_URL
    btn_dash_src = "cid:btn_dashboard" if (use_cid and os.path.exists(BTN_DASHBOARD_PATH)) else ONLINE_BTN_DASHBOARD_URL

    def get_val(cur_code, key):
        val = rates.get(cur_code, {})
        if f"{key}_sap" in val:
            return val[f"{key}_sap"]
        if key in val:
            return format_sap(val[key])
        return format_sap(val.get(f"{key}_str", '-'))

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>[KURS] Laporan Kurs Transaksi Bank Indonesia - {tanggal_bi}</title>
</head>
<body style="margin: 0; padding: 24px 0; background-color: #f8fafc; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif; -webkit-font-smoothing: antialiased;">

  <!-- Outer Container Card -->
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 630px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif;">
    
    <!-- Top Header Bar -->
    <tr>
      <td style="padding: 22px 26px 16px 26px; border-bottom: 2px solid #0056b3;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
          <tr>
            <td valign="middle" align="left">
              <span style="display: inline-block; background-color: #eff6ff; color: #1d4ed8; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px; border: 1px solid #bfdbfe; letter-spacing: 0.5px; text-transform: uppercase;">
                &#9679; RESMI BANK INDONESIA &bull; SAP-READY
              </span>
              <h1 style="margin: 6px 0 3px 0; font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: -0.3px;">
                Laporan Kurs Transaksi
              </h1>
              <p style="margin: 0; font-size: 13px; color: #64748b;">
                Tanggal Rilis: <strong style="color: #1e293b;">{tanggal_bi}</strong> &bull; {jam_update}
              </p>
            </td>
            <td valign="middle" align="right" width="125" style="text-align: right; width: 125px;">
              <img src="{logo_src}" alt="Nabel Sakha Group" width="112" style="display: block; width: 112px; max-width: 112px; height: auto; border: 0;" />
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- Main Table Data Area -->
    <tr>
      <td style="padding: 22px 26px 14px 26px;">
        
        <!-- SAP-Compatible Kurs Table -->
        <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; border: 1px solid #334155; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; width: 100%;">
          <thead>
            <tr bgcolor="#f1f5f9" style="background-color: #f1f5f9;">
              <th style="border: 1px solid #334155; padding: 8px 12px; width: 22%; background-color: #f1f5f9;"></th>
              <th style="border: 1px solid #334155; padding: 8px 10px; color: #0284c7; font-weight: 800; text-align: center; width: 15%; background-color: #f1f5f9; font-size: 14px; font-family: 'Segoe UI', Arial, sans-serif;">EUR</th>
              <th style="border: 1px solid #334155; padding: 8px 10px; color: #0284c7; font-weight: 800; text-align: center; width: 15%; background-color: #f1f5f9; font-size: 14px; font-family: 'Segoe UI', Arial, sans-serif;">JPY</th>
              <th style="border: 1px solid #334155; padding: 8px 10px; color: #0284c7; font-weight: 800; text-align: center; width: 15%; background-color: #f1f5f9; font-size: 14px; font-family: 'Segoe UI', Arial, sans-serif;">KRW</th>
              <th style="border: 1px solid #334155; padding: 8px 10px; color: #0284c7; font-weight: 800; text-align: center; width: 16%; background-color: #f1f5f9; font-size: 14px; font-family: 'Segoe UI', Arial, sans-serif;">SGD</th>
              <th style="border: 1px solid #334155; padding: 8px 10px; color: #0284c7; font-weight: 800; text-align: center; width: 17%; background-color: #f1f5f9; font-size: 14px; font-family: 'Segoe UI', Arial, sans-serif;">USD</th>
            </tr>
          </thead>
          <tbody>
            <!-- Row 1: Kurs Jual -->
            <tr>
              <td style="border: 1px solid #334155; padding: 8px 12px; font-weight: 700; text-align: left; color: #0f172a; white-space: nowrap; font-family: 'Segoe UI', Arial, sans-serif;">Kurs Jual</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 500;">{get_val('EUR', 'jual')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 500;">{get_val('JPY', 'jual')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 500;">{get_val('KRW', 'jual')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 500;">{get_val('SGD', 'jual')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 700;">{get_val('USD', 'jual')}</td>
            </tr>
            <!-- Row 2: Kurs Beli -->
            <tr>
              <td style="border: 1px solid #334155; padding: 8px 12px; font-weight: 700; text-align: left; color: #0f172a; white-space: nowrap; font-family: 'Segoe UI', Arial, sans-serif;">Kurs Beli</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 500;">{get_val('EUR', 'beli')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 500;">{get_val('JPY', 'beli')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 500;">{get_val('KRW', 'beli')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 500;">{get_val('SGD', 'beli')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: 700;">{get_val('USD', 'beli')}</td>
            </tr>
            <!-- Row 3: Kurs Tengah (Highlighted Clean Row) -->
            <tr bgcolor="#f8fafc" style="background-color: #f8fafc;">
              <td style="border: 1px solid #334155; padding: 8px 12px; font-weight: 800; text-align: left; color: #0284c7; white-space: nowrap; background-color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif;">Kurs Tengah</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0284c7; white-space: nowrap; font-weight: 700; background-color: #f8fafc;">{get_val('EUR', 'tengah')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0284c7; white-space: nowrap; font-weight: 700; background-color: #f8fafc;">{get_val('JPY', 'tengah')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0284c7; white-space: nowrap; font-weight: 700; background-color: #f8fafc;">{get_val('KRW', 'tengah')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0284c7; white-space: nowrap; font-weight: 700; background-color: #f8fafc;">{get_val('SGD', 'tengah')}</td>
              <td style="border: 1px solid #334155; padding: 8px 10px; text-align: right; color: #0284c7; white-space: nowrap; font-weight: 800; background-color: #f8fafc;">{get_val('USD', 'tengah')}</td>
            </tr>
          </tbody>
        </table>

        <!-- Graphical Action Buttons Generated by nanobanana -->
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
          <tr>
            <td align="center" style="text-align: center; padding-bottom: 4px;">
              <table border="0" cellpadding="0" cellspacing="0" align="center">
                <tr>
                  <!-- Button 1: Verifikasi Bank Indonesia -->
                  <td align="center" valign="middle" style="padding: 0 8px;">
                    <a href="https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx" target="_blank" style="text-decoration: none; display: inline-block;">
                      <img src="{btn_bi_src}" alt="Verifikasi Bank Indonesia" height="42" style="display: block; height: 42px; width: auto; border: 0; outline: none;" />
                    </a>
                  </td>
                  <!-- Button 2: Dashboard Kurs Online -->
                  <td align="center" valign="middle" style="padding: 0 8px;">
                    <a href="{dashboard_url}" target="_blank" style="text-decoration: none; display: inline-block;">
                      <img src="{btn_dash_src}" alt="Dashboard Kurs Online" height="42" style="display: block; height: 42px; width: auto; border: 0; outline: none;" />
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Fallback Text Links -->
          <tr>
            <td align="center" style="font-size: 11.5px; color: #64748b; padding-top: 8px;">
              Tautan Langsung: 
              <a href="https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx" target="_blank" style="color: #0284c7; text-decoration: underline; margin-right: 12px; font-weight: 600;">Web Bank Indonesia &nearr;</a>
              &bull;
              <a href="{dashboard_url}" target="_blank" style="color: #ea580c; text-decoration: underline; margin-left: 12px; font-weight: 600;">Dashboard Kurs Realtime &nearr;</a>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- Footer -->
    <tr>
      <td style="padding: 16px 26px 20px 26px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b; line-height: 1.6;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
          <tr>
            <td align="left" valign="top">
              &bull; <strong>Kompatibilitas SAP:</strong> Format angka tanpa titik ribuan untuk mempermudah copy-paste ke SAP.<br>
              &bull; <strong>JPY:</strong> Nilai dinormalisasi per 1 Yen (nilai resmi Bank Indonesia per 100 Yen).<br>
              &bull; <strong>Kurs Tengah:</strong> Dihitung otomatis dari <em>(Jual + Beli) &divide; 2</em>.
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-top: 12px; font-size: 10.5px; color: #94a3b8; border-top: 1px dashed #cbd5e1; margin-top: 8px;">
              Sistem Otomasi Finansial &bull; <strong>Nabel Sakha Group</strong> &bull; <a href="mailto:marketing@nabelsakha.com" style="color: #64748b; text-decoration: none;">marketing@nabelsakha.com</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>

  </table>

</body>
</html>
"""
    return html

def send_kurs_email(data, recipient_email, smtp_config, subject=None):
    if not subject:
        today_str = datetime.now().strftime("%d/%m/%Y")
        subject = f"[KURS] Laporan kurs hari ini {today_str}"

    # Sanitasi daftar penerima
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

    rates = data.get('rates', {})
    tanggal_bi = data.get('tanggal_bi', '')
    today_formatted = datetime.now().strftime("%d/%m/%Y")
    dashboard_url = os.environ.get('DASHBOARD_URL', 'https://nsg-9roup.github.io/nsg-kurs/')

    def get_sap(cur_code, key):
        val = rates.get(cur_code, {})
        if f"{key}_sap" in val:
            return val[f"{key}_sap"]
        if key in val:
            return format_sap(val[key])
        return format_sap(val.get(f"{key}_str", '-'))

    # 1. Plain text fallback (Format SAP)
    plain_text = f"""[KURS] Laporan kurs hari ini {today_formatted}
Tanggal Rilis BI: {tanggal_bi}

            EUR        JPY       KRW        SGD        USD
Kurs Jual   {get_sap('EUR', 'jual'):>9}  {get_sap('JPY', 'jual'):>7}  {get_sap('KRW', 'jual'):>6}  {get_sap('SGD', 'jual'):>9}  {get_sap('USD', 'jual'):>9}
Kurs Beli   {get_sap('EUR', 'beli'):>9}  {get_sap('JPY', 'beli'):>7}  {get_sap('KRW', 'beli'):>6}  {get_sap('SGD', 'beli'):>9}  {get_sap('USD', 'beli'):>9}
Kurs Tengah {get_sap('EUR', 'tengah'):>9}  {get_sap('JPY', 'tengah'):>7}  {get_sap('KRW', 'tengah'):>6}  {get_sap('SGD', 'tengah'):>9}  {get_sap('USD', 'tengah'):>9}

* Format angka disesuaikan tanpa pemisah ribuan agar kompatibel untuk input/copy-paste ke SAP.
* JPY dinormalisasi per 1 Yen (nilai resmi BI per 100 Yen).
* Verifikasi Resmi Bank Indonesia: https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx
* Dashboard Kurs Realtime: {dashboard_url}
"""
    msg_alt.attach(MIMEText(plain_text, 'plain', 'utf-8'))

    # 2. Rich HTML content dengan CID images
    html_content = build_html_template(data, use_cid=True)
    msg_alt.attach(MIMEText(html_content, 'html', 'utf-8'))

    # Lampirkan Logo & Tombol nanobanana sebagai CID Inline
    attachments = [
        (LOGO_PATH, '<nsg_logo>', 'logo.png'),
        (BTN_BI_PATH, '<btn_bi>', 'btn_bi.png'),
        (BTN_DASHBOARD_PATH, '<btn_dashboard>', 'btn_dashboard.png')
    ]
    for path, cid, filename in attachments:
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', cid)
                    img.add_header('Content-Disposition', 'inline', filename=filename)
                    msg.attach(img)
            except Exception as e:
                print(f"[Mailer] Gagal melampirkan CID {cid}: {e}")

    host = smtp_config['host']
    port = int(smtp_config.get('port', 587))
    user = smtp_config['user']
    password = smtp_config['pass']
    use_tls = smtp_config.get('use_tls', True)

    print(f"[Mailer] Menghubungkan ke {host}:{port} (Penerima: {', '.join(recipients_list)})...")
    
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
    print("Berhasil memperbarui kedua file preview dengan tombol nanobanana dan format SAP!")
