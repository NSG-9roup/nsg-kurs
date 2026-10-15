import os
from PIL import Image, ImageDraw, ImageFont

def create_favicons():
    # 1. Buat favicon.svg (Vector Tajam untuk Modern Browsers)
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <defs>
    <!-- Gradasi Merah ke Orange Khas Nabel Sakha Group -->
    <linearGradient id="dollarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#dc2626" />
      <stop offset="100%" stop-color="#ea580c" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" flood-color="rgba(0,0,0,0.1)" />
    </filter>
  </defs>

  <!-- Background Putih Square Rounded -->
  <rect x="2" y="2" width="60" height="60" rx="14" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#shadow)"/>

  <!-- Simbol Dolar Bold Tengah dengan Gradasi Merah-Orange -->
  <text x="32" y="44" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Plus Jakarta Sans', Arial, sans-serif" font-size="38" font-weight="900" fill="url(#dollarGrad)" text-anchor="middle" letter-spacing="-1">$</text>
</svg>'''

    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = base_dir

    svg_path = os.path.join(root_dir, 'favicon.svg')
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"[OK] Berhasil membuat {svg_path}")

    # 2. Buat favicon.png (High Resolution 128x128) & favicon.ico via Pillow
    size = 128
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background putih square rounded
    # Corner radius 28px untuk canvas 128px
    margin = 4
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=28,
        fill=(255, 255, 255, 255),
        outline=(226, 232, 240, 255),
        width=3
    )

    # Buat mask teks simbol dolar
    # Coba beberapa font sistem Windows (Arial Black, Segoe UI Black, dll)
    font_candidates = [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\ariblk.ttf",
        "C:\\Windows\\Fonts\\seguihb.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    font = None
    for fc in font_candidates:
        if os.path.exists(fc):
            try:
                font = ImageFont.truetype(fc, 84)
                break
            except Exception:
                pass
    if not font:
        font = ImageFont.load_default()

    # Bikin gradasi merah ke orange
    # Merah: (220, 38, 38), Orange: (234, 88, 12)
    grad_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(size):
        r = int(220 + (234 - 220) * (y / size))
        g = int(38 + (88 - 38) * (y / size))
        b = int(38 + (12 - 38) * (y / size))
        for x in range(size):
            grad_img.putpixel((x, y), (r, g, b, 255))

    # Mask teks
    text_mask = Image.new("L", (size, size), 0)
    text_draw = ImageDraw.Draw(text_mask)
    text = "$"
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (size - text_w) // 2 - bbox[0]
    text_y = (size - text_h) // 2 - bbox[1] - 2
    text_draw.text((text_x, text_y), text, fill=255, font=font)

    # Tempel gradasi ke gambar utama menggunakan mask teks
    img.paste(grad_img, (0, 0), text_mask)

    png_path = os.path.join(root_dir, 'favicon.png')
    img.save(png_path, "PNG")
    print(f"[OK] Berhasil membuat {png_path}")

    ico_path = os.path.join(root_dir, 'favicon.ico')
    img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print(f"[OK] Berhasil membuat {ico_path}")

if __name__ == '__main__':
    create_favicons()
