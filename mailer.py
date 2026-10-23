"""
mailer.py
Bertanggung jawab menyusun konten HTML email murni (tanpa gambar)
dan mengirimkannya menggunakan protokol SMTP standar.
Dioptimasi 100% untuk tampilan bersih di Outlook Desktop, Webmail, dan Microsoft Teams.
Format angka disesuaikan tanpa titik ribuan untuk kemudahan input data.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

CURRENCIES_NSG = ['EUR', 'JPY', 'KRW', 'SGD', 'USD']
CURRENCIES_DQW = ['AUD', 'EUR', 'GBP', 'KRW', 'CNY', 'SGD', 'USD']

def format_sap(val):
    """
    Format angka bersih:
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

def build_html_template(data, report_type='NSG', use_cid=False):
    rates = data.get('rates', {})
    tanggal_bi = data.get('tanggal_bi', datetime.now().strftime("%d %B %Y"))
    jam_update = data.get('timestamp', '08:00 WIB')
    dashboard_url = os.environ.get('DASHBOARD_URL', 'https://nsg-9roup.github.io/nsg-kurs/')

    is_dqw = (str(report_type).upper() == 'DQW')
    currencies = CURRENCIES_DQW if is_dqw else CURRENCIES_NSG
    
    brand_title = "DQW DIVISION" if is_dqw else "NABEL SAKHA GROUP"
    report_title = "Laporan Kurs Transaksi (DQW)" if is_dqw else "Laporan Kurs Transaksi"
    rpt_prefix = "DQW" if is_dqw else "NSG"
    email_title_tag = f"[KURS] {rpt_prefix} - Laporan Kurs Transaksi Bank Indonesia - {tanggal_bi}"

    def get_val(cur_code, key):
        val = rates.get(cur_code, {})
        if f"{key}_sap" in val:
            return val[f"{key}_sap"]
        if key in val:
            return format_sap(val[key])
        return format_sap(val.get(f"{key}_str", '-'))

    # Dynamic Column Calculations
    label_width = "18%" if is_dqw else "22%"
    col_width = f"{int(82 / len(currencies))}%" if is_dqw else f"{int(78 / len(currencies))}%"

    th_cells = "".join([
        f'<th style="border: 1px solid #334155; padding: 8px 6px; color: #0284c7; font-weight: 800; text-align: center; width: {col_width}; background-color: #f1f5f9; font-size: 13.5px; font-family: \'Segoe UI\', Arial, sans-serif;">{c}</th>'
        for c in currencies
    ])

    jual_cells = "".join([
        f'<td style="border: 1px solid #334155; padding: 8px 6px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: {700 if c == "USD" else 500}; font-size: 12.5px;">{get_val(c, "jual")}</td>'
        for c in currencies
    ])

    beli_cells = "".join([
        f'<td style="border: 1px solid #334155; padding: 8px 6px; text-align: right; color: #0f172a; white-space: nowrap; font-weight: {700 if c == "USD" else 500}; font-size: 12.5px;">{get_val(c, "beli")}</td>'
        for c in currencies
    ])

    tengah_cells = "".join([
        f'<td style="border: 1px solid #334155; padding: 8px 6px; text-align: right; color: #0284c7; white-space: nowrap; font-weight: {800 if c == "USD" else 700}; background-color: #f8fafc; font-size: 12.5px;">{get_val(c, "tengah")}</td>'
        for c in currencies
    ])

    # Footnote logic
    footnote_items = []
    if 'JPY' in currencies:
        footnote_items.append('&bull; <strong>JPY:</strong> Nilai dinormalisasi per 1 Yen (nilai resmi Bank Indonesia per 100 Yen).')
    footnote_items.append('&bull; <strong>Kurs Tengah:</strong> Dihitung otomatis dari <em>(Jual + Beli) &divide; 2</em>.')
    footnote_html = "<br>".join(footnote_items)

    footer_entity = "Nabel Sakha Group (DQW)" if is_dqw else "Nabel Sakha Group"

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <title>{email_title_tag}</title>
</head>
<body style="margin: 0; padding: 20px 0; background-color: #f8fafc; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif; -webkit-font-smoothing: antialiased;">

  <!-- Outer Card Container -->
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 650px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; border-collapse: separate;">
    
    <!-- Header Section (Murni Teks Tanpa Gambar) -->
    <tr>
      <td style="padding: 22px 26px 16px 26px; border-bottom: 2px solid #0056b3;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="border: none !important; border-collapse: collapse;">
          <tr>
            <td valign="middle" align="left" style="border: none !important;">
              <span style="display: inline-block; background-color: #eff6ff; color: #1d4ed8; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px; border: 1px solid #bfdbfe; letter-spacing: 0.5px; text-transform: uppercase;">
                &#9679; RESMI BANK INDONESIA
              </span>
              <h1 style="margin: 6px 0 3px 0; font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: -0.3px;">
                {report_title}
              </h1>
              <p style="margin: 0; font-size: 13px; color: #64748b;">
                Tanggal Rilis: <strong style="color: #1e293b;">{tanggal_bi}</strong> &bull; {jam_update}
              </p>
            </td>
            <td valign="middle" align="right" style="text-align: right; border: none !important; white-space: nowrap;">
              <div style="font-size: 14px; font-weight: 800; color: #0f172a; letter-spacing: -0.2px;">
                {brand_title}
              </div>
              <div style="font-size: 11px; color: #64748b; font-weight: 600; margin-top: 2px;">
                Financial Operations
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- Main Table Data Area -->
    <tr>
      <td style="padding: 22px 26px 16px 26px; border: none !important;">
        
        <!-- Tabel Kurs Bersih -->
        <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; border: 1px solid #334155; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; width: 100%;">
          <thead>
            <tr bgcolor="#f1f5f9" style="background-color: #f1f5f9;">
              <th style="border: 1px solid #334155; padding: 8px 10px; width: {label_width}; background-color: #f1f5f9;"></th>
              {th_cells}
            </tr>
          </thead>
          <tbody>
            <!-- Row 1: Kurs Jual -->
            <tr>
              <td style="border: 1px solid #334155; padding: 8px 10px; font-weight: 700; text-align: left; color: #0f172a; white-space: nowrap; font-family: 'Segoe UI', Arial, sans-serif;">Kurs Jual</td>
              {jual_cells}
            </tr>
            <!-- Row 2: Kurs Beli -->
            <tr>
              <td style="border: 1px solid #334155; padding: 8px 10px; font-weight: 700; text-align: left; color: #0f172a; white-space: nowrap; font-family: 'Segoe UI', Arial, sans-serif;">Kurs Beli</td>
              {beli_cells}
            </tr>
            <!-- Row 3: Kurs Tengah (Highlighted Clean Row) -->
            <tr bgcolor="#f8fafc" style="background-color: #f8fafc;">
              <td style="border: 1px solid #334155; padding: 8px 10px; font-weight: 800; text-align: left; color: #0284c7; white-space: nowrap; background-color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif;">Kurs Tengah</td>
              {tengah_cells}
            </tr>
          </tbody>
        </table>

        <!-- Tombol Berbasis Tabel Murni (100% Anti-Pecah & Bersih di Teams / Outlook) -->
        <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 20px auto 4px auto; border: none !important; border-collapse: separate;">
          <tr>
            <!-- Tombol 1: Bank Indonesia -->
            <td bgcolor="#0056b3" style="background-color: #0056b3; border-radius: 4px; padding: 9px 18px; text-align: center; border: none !important;">
              <a href="https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx" target="_blank" style="color: #ffffff !important; text-decoration: none; font-family: 'Segoe UI', Arial, sans-serif; font-size: 12.5px; font-weight: bold; display: inline-block; white-space: nowrap;">
                Verifikasi Bank Indonesia &nearr;
              </a>
            </td>
            <td width="12" style="width: 12px; border: none !important;"></td>
            <!-- Tombol 2: Dashboard Online -->
            <td bgcolor="#ea580c" style="background-color: #ea580c; border-radius: 4px; padding: 9px 18px; text-align: center; border: none !important;">
              <a href="{dashboard_url}" target="_blank" style="color: #ffffff !important; text-decoration: none; font-family: 'Segoe UI', Arial, sans-serif; font-size: 12.5px; font-weight: bold; display: inline-block; white-space: nowrap;">
                Dashboard Kurs Online &nearr;
              </a>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- Footer -->
    <tr>
      <td style="padding: 16px 26px 20px 26px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b; line-height: 1.6;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="border: none !important; border-collapse: collapse;">
          <tr>
            <td align="left" valign="top" style="border: none !important;">
              {footnote_html}
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-top: 12px; font-size: 10.5px; color: #94a3b8; border-top: 1px dashed #cbd5e1; margin-top: 8px; border-left: none; border-right: none; border-bottom: none;">
              Sistem Otomasi Finansial &bull; <strong>{footer_entity}</strong> &bull; <a href="mailto:marketing@nabelsakha.com" style="color: #64748b; text-decoration: none;">marketing@nabelsakha.com</a>
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

def send_kurs_email(data, recipient_email, smtp_config, subject=None, report_type='NSG'):
    is_dqw = (str(report_type).upper() == 'DQW')
    today_str = datetime.now().strftime("%d/%m/%Y")
    
    if not subject:
        rpt_prefix = "DQW" if is_dqw else "NSG"
        subject = f"[KURS] {rpt_prefix} - Laporan kurs hari ini {today_str}"

    recipients_list = [r.strip() for r in recipient_email.split(',') if r.strip()]
    if not recipients_list:
        raise ValueError("Target penerima email kosong.")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    from_name = smtp_config.get('from_name', 'Sistem Kurs Nabel Sakha')
    msg['From'] = f"{from_name} <{smtp_config['user']}>"
    msg['To'] = ", ".join(recipients_list)

    rates = data.get('rates', {})
    tanggal_bi = data.get('tanggal_bi', '')
    today_formatted = datetime.now().strftime("%d/%m/%Y")
    dashboard_url = os.environ.get('DASHBOARD_URL', 'https://nsg-9roup.github.io/nsg-kurs/')
    currencies = CURRENCIES_DQW if is_dqw else CURRENCIES_NSG

    def get_sap(cur_code, key):
        val = rates.get(cur_code, {})
        if f"{key}_sap" in val:
            return val[f"{key}_sap"]
        if key in val:
            return format_sap(val[key])
        return format_sap(val.get(f"{key}_str", '-'))

    # 1. Plain text fallback
    header_line = f"{'':12}" + "".join([f"{c:>11}" for c in currencies])
    jual_line   = f"{'Kurs Jual':12}" + "".join([f"{get_sap(c, 'jual'):>11}" for c in currencies])
    beli_line   = f"{'Kurs Beli':12}" + "".join([f"{get_sap(c, 'beli'):>11}" for c in currencies])
    tengah_line = f"{'Kurs Tengah':12}" + "".join([f"{get_sap(c, 'tengah'):>11}" for c in currencies])

    jpy_plain_note = "* JPY dinormalisasi per 1 Yen (nilai resmi BI per 100 Yen).\n" if 'JPY' in currencies else ""

    plain_text = f"""{subject}
Tanggal Rilis BI: {tanggal_bi}

{header_line}
{jual_line}
{beli_line}
{tengah_line}

{jpy_plain_note}* Verifikasi Resmi Bank Indonesia: https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx
* Dashboard Kurs Realtime: {dashboard_url}
"""
    msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))

    # 2. Rich HTML content murni tanpa gambar
    html_content = build_html_template(data, report_type=report_type, use_cid=False)
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    host = smtp_config['host']
    port = int(smtp_config.get('port', 587))
    user = smtp_config['user']
    password = smtp_config['pass']
    use_tls = smtp_config.get('use_tls', True)

    print(f"[Mailer - {report_type}] Menghubungkan ke {host}:{port} (Penerima: {', '.join(recipients_list)})...")
    
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
    print(f"[Mailer - {report_type}] Sukses terkirim ke {', '.join(recipients_list)}!")
    return True

if __name__ == '__main__':
    from scraper import get_latest_kurs_data
    data = get_latest_kurs_data()
    
    html_nsg = build_html_template(data, report_type='NSG', use_cid=False)
    html_dqw = build_html_template(data, report_type='DQW', use_cid=False)
    
    with open('preview_email.html', 'w', encoding='utf-8') as f:
        f.write(html_nsg)
    with open('preview_with_trend.html', 'w', encoding='utf-8') as f:
        f.write(html_nsg)
    with open('preview_email_dqw.html', 'w', encoding='utf-8') as f:
        f.write(html_dqw)
        
    print("Berhasil memperbarui preview email NSG (preview_email.html) & DQW (preview_email_dqw.html)!")
