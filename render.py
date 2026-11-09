"""derinizbirak gönderi üretici.

Kullanım:
  .venv/bin/python render.py                 # posts.json içindeki tüm gönderileri üretir
  .venv/bin/python render.py --sadece 3      # sadece 3 numaralı gönderi

posts.json alanları:
  gorsel   : input/ klasöründeki dosya adı (yoksa koyu degrade demo arka plan kullanılır)
  ust      : küçük giriş satırı
  ana      : dev vurucu satır (nokta otomatik eklenmez, kendin yaz)
  duzen    : "ust" (küçük satır üstte, varsayılan) | "alt" (dev satır üstte, küçük alta)
  y        : metnin dikey konumu, 0-1 arası (varsayılan 0.30)
  renk     : "auto" | "beyaz" | "siyah"
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

KOK = Path(__file__).parent
W, H = 1080, 1350  # Instagram 4:5
FILIGRAN = "DERİNİZBİRAK ® 2026"
BUYUK_FONT = KOK / "fonts/ArchivoBlack.ttf"
KUCUK_FONT = KOK / "fonts/Montserrat.ttf"


def font(path, size, agirlik=None):
    f = ImageFont.truetype(str(path), size)
    if agirlik:
        f.set_variation_by_axes([agirlik])
    return f


def genislik(text, f, track):
    return sum(f.getlength(c) for c in text) + track * (len(text) - 1) if text else 0


def ciz(d, xy, text, f, renk, track):
    """Harf aralığı daraltılmış metin çizer (kerning yaklaşık korunur)."""
    x, y = xy
    for i, c in enumerate(text):
        d.text((x, y), c, font=f, fill=renk)
        if i + 1 < len(text):
            adv = f.getlength(c + text[i + 1]) - f.getlength(text[i + 1])
            x += adv + track


def kirp(img):
    img = img.convert("RGB")
    oran = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * oran), round(img.height * oran)), Image.LANCZOS)
    l, t = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((l, t, l + W, t + H))


def demo_arka_plan():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for yy in range(H):
        for xx in range(W):
            dx, dy = (xx - W / 2) / W, (yy - H * 0.6) / H
            v = max(0, 60 - int((dx * dx + dy * dy) ** 0.5 * 140))
            px[xx, yy] = (v, v, v + 4)
    return img


def renk_sec(img, kutu, istek):
    if istek == "beyaz":
        return (255, 255, 255)
    if istek == "siyah":
        return (8, 8, 8)
    parlak = ImageStat.Stat(img.crop(kutu).convert("L")).mean[0]
    return (8, 8, 8) if parlak > 150 else (255, 255, 255)


def uret(post, cikti):
    yol = KOK / "input" / post.get("gorsel", "")
    img = kirp(Image.open(yol)) if post.get("gorsel") and yol.exists() else demo_arka_plan()

    ana, ust = post["ana"], post.get("ust", "")
    max_w = W * 0.84

    # Dev satır: genişliğe sığacak en büyük punto (üst sınır 200)
    size = 200
    while size > 40:
        bf = font(BUYUK_FONT, size)
        track = -size * 0.045
        if genislik(ana, bf, track) <= max_w:
            break
        size -= 2
    bw = genislik(ana, bf, track)
    asc, desc = bf.getmetrics()

    kf = font(KUCUK_FONT, max(30, int(size * 0.30)), 650)
    ktrack = -kf.size * 0.02
    kw = genislik(ust, kf, ktrack)
    while kw > max_w and kf.size > 20:  # uzun küçük satırı sığdır
        kf = font(KUCUK_FONT, kf.size - 2, 650)
        ktrack = -kf.size * 0.02
        kw = genislik(ust, kf, ktrack)
    wf = font(BUYUK_FONT, 17)

    x0 = (W - bw) / 2
    y_merkez = H * post.get("y", 0.30)
    x_header = 0.05 * size  # küçük satır biraz içeriden başlar

    if post.get("duzen", "ust") == "ust":
        ky = y_merkez - size * 0.62
        by = ky + kf.size * 0.55
        wy = by + asc * 0.98
        wx = x0 + bw - genislik(FILIGRAN, wf, 0.5)
        kx = x0 + x_header
    else:
        by = y_merkez - size * 0.62
        wy = by + bf.getbbox(ana)[1] - wf.size - 8
        wx = x0 + size * 0.04
        ky = by + asc * 0.93
        kx = x0 + (bw - kw) / 2 if post.get("ortala", True) else x0 + x_header

    kutu = (int(x0), int(min(ky, by, wy)), int(x0 + bw), int(max(ky + kf.size, by + asc)))
    renk = renk_sec(img, kutu, post.get("renk", "auto"))

    # çok hafif gölge: okunurluk için, referanstaki temiz görünümü bozmadan
    golge = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(golge)
    for (txt, f, t, xy) in [(ust, kf, ktrack, (kx, ky)), (ana, bf, track, (x0, by))]:
        ciz(gd, xy, txt, f, 255, t)
    golge = golge.filter(ImageFilter.GaussianBlur(14)).point(lambda p: p * 0.28)
    golge_renk = (0, 0, 0) if renk[0] > 128 else (255, 255, 255)
    img = Image.composite(Image.new("RGB", (W, H), golge_renk), img, golge)

    d = ImageDraw.Draw(img)
    ciz(d, (kx, ky), ust, kf, renk, ktrack)
    ciz(d, (x0, by), ana, bf, renk, track)
    ciz(d, (wx, wy), FILIGRAN, wf, renk, 0.5)

    img.save(cikti, quality=95)
    return cikti


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sadece", type=int)
    a = ap.parse_args()
    posts = json.loads((KOK / "posts.json").read_text(encoding="utf-8"))
    for i, p in enumerate(posts, 1):
        if a.sadece and a.sadece != i:
            continue
        print(uret(p, KOK / "output" / f"{i:02d}.jpg"))
