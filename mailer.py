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
    rates = data['rates']
    tanggal_bi = data.get('tanggal_bi', datetime.now().strftime("%d %B %Y"))
    jam_update = data.get('timestamp', '08:00 WIB')
    dashboard_url = os.environ.get('DASHBOARD_URL', 'https://nsg-9roup.github.io/nsg-kurs/')
    
    logo_src = "cid:nsg_logo" if (use_cid and os.path.exists(LOGO_PATH)) else ONLINE_LOGO_URL

    # Render selisih / tren dengan table cell khusus agar Outlook tidak memotong tanda kurung
    def render_trend_td(cur_code):
        val = rates.get(cur_code, {})
        trend_icon = val.get('trend_icon', '-')
        delta_str = val.get('trend_text', '')
        
        if trend_icon == '▲':
            # Merah: Kurs naik
            bg = '#fef2f2'
            border = '#fecaca'
            color = '#dc2626'
            txt = f"▲ {delta_str}"
        elif trend_icon == '▼':
            # Hijau: Kurs turun
            bg = '#f0fdf4'
            border = '#bbf7d0'
            color = '#16a34a'
            txt = f"▼ {delta_str}"
        else:
            bg = '#f8fafc'
            border = '#e2e8f0'
            color = '#94a3b8'
            txt = "- Tetap"

        return f'''
        <td align="right" nowrap="nowrap" style="padding: 8px 4px; white-space: nowrap;">
          <table border="0" cellpadding="0" cellspacing="0" align="right">
            <tr>
              <td bgcolor="{bg}" nowrap="nowrap" style="background-color: {bg}; border: 1px solid {border}; padding: 3px 6px; font-size: 10px; font-weight: bold; color: {color}; font-family: 'Segoe UI', Arial, sans-serif; white-space: nowrap;">
                {txt}
              </td>
            </tr>
          </table>
        </td>
        '''

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Laporan Kurs Transaksi BI - Nabel Sakha Group</title>
</head>
<body style="margin: 0; padding: 20px 0; background-color: #ffffff; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;">

  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 630px; margin: 0 auto; background-color: #ffffff; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;">
    
    <!-- Top Brand Header: Nabel Sakha Group -->
    <tr>
      <td style="padding: 10px 0 16px 0; border-bottom: 2px solid #ea580c;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
          <tr>
            <!-- Left: Title & Date -->
            <td valign="middle" align="left">
              <table border="0" cellpadding="0" cellspacing="0" style="margin-bottom: 8px;">
                <tr>
                  <td bgcolor="#fff7ed" style="background-color: #fff7ed; border: 1px solid #fed7aa; border-radius: 12px; padding: 3px 10px; font-size: 11px; font-weight: 700; color: #c2410c; text-transform: uppercase; letter-spacing: 0.5px;">
                    &#9679; BANK INDONESIA &bull; RESMI
                  </td>
                </tr>
              </table>
              <h2 style="margin: 0; color: #0f172a; font-size: 22px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2;">
                Laporan Kurs Transaksi
              </h2>
              <p style="margin: 4px 0 0 0; color: #64748b; font-size: 13px;">
                Tanggal Rilis: <strong style="color: #1e293b;">{tanggal_bi}</strong> &bull; {jam_update}
              </p>
            </td>

            <!-- Right: Official Logo Nabel Sakha Group -->
            <td valign="middle" align="right" style="text-align: right; width: 130px;">
              <img src="{logo_src}" alt="Nabel Sakha Group" width="118" style="display: block; width: 118px; max-width: 118px; height: auto; border: 0; outline: none;" />
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- Main Table Data Area -->
    <tr>
      <td style="padding: 20px 0 16px 0;">
        
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse; width: 100%;">
          
          <!-- Table Header: Columns -->
          <thead>
            <tr style="border-bottom: 2px solid #cbd5e1;">
              <th align="left" style="padding: 12px 6px; font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; width: 20%;">
                TIPE KURS
              </th>
              <th align="right" style="padding: 12px 6px; font-size: 13px; font-weight: 800; color: #0f172a; width: 16%;">
                EUR
              </th>
              <th align="right" style="padding: 12px 6px; font-size: 13px; font-weight: 800; color: #0f172a; width: 15%;">
                JPY
              </th>
              <th align="right" style="padding: 12px 6px; font-size: 13px; font-weight: 800; color: #0f172a; width: 15%;">
                KRW
              </th>
              <th align="right" style="padding: 12px 6px; font-size: 13px; font-weight: 800; color: #0f172a; width: 16%;">
                SGD
              </th>
              <th align="right" style="padding: 12px 8px; font-size: 13px; font-weight: 800; color: #ea580c; width: 18%;">
                USD
              </th>
            </tr>
          </thead>

          <!-- Table Body -->
          <tbody>
            <!-- Row 1: Kurs Jual -->
            <tr style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 13px 6px; font-size: 13px; font-weight: 600; color: #475569;">
                Kurs Jual
              </td>
              <td align="right" style="padding: 13px 6px; font-size: 13px; color: #0f172a; font-family: 'Consolas', 'Courier New', monospace; font-weight: 500;">
                {rates.get('EUR', {}).get('jual_str', '-')}
              </td>
              <td align="right" style="padding: 13px 6px; font-size: 13px; color: #0f172a; font-family: 'Consolas', 'Courier New', monospace; font-weight: 500;">
                {rates.get('JPY', {}).get('jual_str', '-')}
              </td>
              <td align="right" style="padding: 13px 6px; font-size: 13px; color: #0f172a; font-family: 'Consolas', 'Courier New', monospace; font-weight: 500;">
                {rates.get('KRW', {}).get('jual_str', '-')}
              </td>
              <td align="right" style="padding: 13px 6px; font-size: 13px; color: #0f172a; font-family: 'Consolas', 'Courier New', monospace; font-weight: 500;">
                {rates.get('SGD', {}).get('jual_str', '-')}
              </td>
              <td align="right" style="padding: 13px 8px; font-size: 13px; color: #c2410c; font-family: 'Consolas', 'Courier New', monospace; font-weight: 700;">
                {rates.get('USD', {}).get('jual_str', '-')}
              </td>
            </tr>

            <!-- Row 2: Kurs Beli -->
            <tr style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 13px 6px; font-size: 13px; font-weight: 600; color: #475569;">
                Kurs Beli
              </td>
              <td align="right" style="padding: 13px 6px; font-size: 13px; color: #0f172a; font-family: 'Consolas', 'Courier New', monospace; font-weight: 500;">
                {rates.get('EUR', {}).get('beli_str', '-')}
              </td>
              <td align="right" style="padding: 13px 6px; font-size: 13px; color: #0f172a; font-family: 'Consolas', 'Courier New', monospace; font-weight: 500;">
                {rates.get('JPY', {}).get('beli_str', '-')}
              </td>
              <td align="right" style="padding: 13px 6px; font-size: 13px; color: #0f172a; font-family: 'Consolas', 'Courier New', monospace; font-weight: 500;">
                {rates.get('KRW', {}).get('beli_str', '-')}
              </td>
              <td align="right" style="padding: 13px 6px; font-size: 13px; color: #0f172a; font-family: 'Consolas', 'Courier New', monospace; font-weight: 500;">
                {rates.get('SGD', {}).get('beli_str', '-')}
              </td>
              <td align="right" style="padding: 13px 8px; font-size: 13px; color: #c2410c; font-family: 'Consolas', 'Courier New', monospace; font-weight: 700;">
                {rates.get('USD', {}).get('beli_str', '-')}
              </td>
            </tr>

            <!-- Row 3: Kurs Tengah (Highlighted Clean Row) -->
            <tr bgcolor="#f0fdf4" style="background-color: #f0fdf4;">
              <td bgcolor="#f0fdf4" style="background-color: #f0fdf4; padding: 14px 6px; font-size: 13px; font-weight: 800; color: #166534;">
                &#9733; Kurs Tengah
              </td>
              <td align="right" bgcolor="#f0fdf4" style="background-color: #f0fdf4; padding: 14px 6px; font-size: 13px; color: #166534; font-family: 'Consolas', 'Courier New', monospace; font-weight: 700;">
                {rates.get('EUR', {}).get('tengah_str', '-')}
              </td>
              <td align="right" bgcolor="#f0fdf4" style="background-color: #f0fdf4; padding: 14px 6px; font-size: 13px; color: #166534; font-family: 'Consolas', 'Courier New', monospace; font-weight: 700;">
                {rates.get('JPY', {}).get('tengah_str', '-')}
              </td>
              <td align="right" bgcolor="#f0fdf4" style="background-color: #f0fdf4; padding: 14px 6px; font-size: 13px; color: #166534; font-family: 'Consolas', 'Courier New', monospace; font-weight: 700;">
                {rates.get('KRW', {}).get('tengah_str', '-')}
              </td>
              <td align="right" bgcolor="#f0fdf4" style="background-color: #f0fdf4; padding: 14px 6px; font-size: 13px; color: #166534; font-family: 'Consolas', 'Courier New', monospace; font-weight: 700;">
                {rates.get('SGD', {}).get('tengah_str', '-')}
              </td>
              <td align="right" bgcolor="#f0fdf4" style="background-color: #f0fdf4; padding: 14px 8px; font-size: 14px; color: #15803d; font-family: 'Consolas', 'Courier New', monospace; font-weight: 800;">
                {rates.get('USD', {}).get('tengah_str', '-')}
              </td>
            </tr>

            <!-- Row 4: Perubahan / Tren vs Kemarin (Nowrap & Bulletproof Table Pills) -->
            <tr style="border-bottom: 2px solid #e2e8f0; background-color: #fafafa;">
              <td style="padding: 10px 6px; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">
                Perubahan (24h)
              </td>
              {render_trend_td('EUR')}
              {render_trend_td('JPY')}
              {render_trend_td('KRW')}
              {render_trend_td('SGD')}
              {render_trend_td('USD')}
            </tr>

          </tbody>
        </table>

        <!-- Notes & Direct BI Action Button (Outlook Bulletproof Table Button) -->
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top: 18px; padding-top: 12px;">
          <tr>
            <td valign="middle" align="left" style="font-size: 11px; color: #64748b; line-height: 1.6;">
              &bull; <strong>JPY:</strong> Nilai dinormalisasi per 1 Yen (Nilai resmi BI per 100 Yen).<br>
              &bull; <strong>Kurs Tengah:</strong> Dihitung dari <em>(Jual + Beli) &divide; 2</em>.<br>
              &bull; <strong>Perubahan:</strong> Selisih Kurs Tengah terhadap hari kerja sebelumnya.
            </td>
            <td valign="middle" align="right" style="padding-left: 12px; white-space: nowrap;">
              <!-- Bulletproof Action Buttons for Outlook / Webmail -->
              <table border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td bgcolor="#f8fafc" style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 7px 12px; text-align: center;">
                    <a href="https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx" target="_blank" style="font-size: 11px; font-weight: bold; color: #0284c7; text-decoration: none; font-family: 'Segoe UI', Arial, sans-serif; display: inline-block;">
                      Verifikasi di Web BI &nearr;
                    </a>
                  </td>
                  <td width="8" style="width: 8px;"></td>
                  <td bgcolor="#ea580c" style="background-color: #ea580c; border: 1px solid #ea580c; border-radius: 6px; padding: 7px 12px; text-align: center;">
                    <a href="{dashboard_url}" target="_blank" style="font-size: 11px; font-weight: bold; color: #ffffff; text-decoration: none; font-family: 'Segoe UI', Arial, sans-serif; display: inline-block;">
                      📊 Dashboard Kurs &nearr;
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- Subtle Footer with Company Info -->
    <tr>
      <td style="padding: 14px 0 0 0; text-align: left; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
          <tr>
            <td align="left" style="font-size: 11px; color: #94a3b8;">
              Sistem Otomasi Finansial &bull; <strong>Nabel Sakha Group</strong>
            </td>
            <td align="right" style="font-size: 11px; color: #94a3b8;">
              Internal Report
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

    # 1. Plain text fallback (Sangat penting agar lolos anti-spam Microsoft 365 / Corporate Defender)
    rates = data.get('rates', {})
    tanggal_bi = data.get('tanggal_bi', '')
    jam_update = data.get('timestamp', '')
    plain_text = f"""Laporan Kurs Transaksi Bank Indonesia - Nabel Sakha Group
Tanggal Rilis: {tanggal_bi} ({jam_update})

-------------------------------------------------------------------------
Mata Uang | Kurs Jual       | Kurs Beli       | Kurs Tengah   | Tren
-------------------------------------------------------------------------
EUR       | {rates.get('EUR', {}).get('jual_str', '-'):15} | {rates.get('EUR', {}).get('beli_str', '-'):15} | {rates.get('EUR', {}).get('tengah_str', '-'):13} | {rates.get('EUR', {}).get('trend_text', '-')}
JPY (1)   | {rates.get('JPY', {}).get('jual_str', '-'):15} | {rates.get('JPY', {}).get('beli_str', '-'):15} | {rates.get('JPY', {}).get('tengah_str', '-'):13} | {rates.get('JPY', {}).get('trend_text', '-')}
KRW       | {rates.get('KRW', {}).get('jual_str', '-'):15} | {rates.get('KRW', {}).get('beli_str', '-'):15} | {rates.get('KRW', {}).get('tengah_str', '-'):13} | {rates.get('KRW', {}).get('trend_text', '-')}
SGD       | {rates.get('SGD', {}).get('jual_str', '-'):15} | {rates.get('SGD', {}).get('beli_str', '-'):15} | {rates.get('SGD', {}).get('tengah_str', '-'):13} | {rates.get('SGD', {}).get('trend_text', '-')}
USD       | {rates.get('USD', {}).get('jual_str', '-'):15} | {rates.get('USD', {}).get('beli_str', '-'):15} | {rates.get('USD', {}).get('tengah_str', '-'):13} | {rates.get('USD', {}).get('trend_text', '-')}
-------------------------------------------------------------------------
* JPY dinormalisasi per 1 Yen (nilai resmi BI per 100 Yen).
* Verifikasi resmi : https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx
* Dashboard online : {os.environ.get('DASHBOARD_URL', 'https://nsg-9roup.github.io/nsg-kurs/')}
"""
    msg_alt.attach(MIMEText(plain_text, 'plain', 'utf-8'))

    # 2. Rich HTML content
    html_content = build_html_template(data, use_cid=True)
    msg_alt.attach(MIMEText(html_content, 'html', 'utf-8'))

    if os.path.exists(LOGO_PATH):
        try:
            with open(LOGO_PATH, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<nsg_logo>')
                img.add_header('Content-Disposition', 'inline', filename='logo.png')
                msg.attach(img)
        except Exception as e:
            print(f"[Mailer] Gagal melampirkan logo CID: {e}")

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
