"""Sıradaki hazır gönderiyi Instagram'a paylaşır (resmi Instagram API).

Ortam değişkenleri:
  IG_TOKEN      : Instagram uzun ömürlü erişim token'ı (Instagram Login)
  GORSEL_TABAN  : hazir/ klasörünün herkese açık URL'si,
                  örn. https://raw.githubusercontent.com/KULLANICI/derinizbirak/main/hazir
  API_SURUM     : (opsiyonel) varsayılan v23.0

Kullanım:
  python paylas.py            # sıradakini paylaş
  python paylas.py --dene     # hiçbir şey paylaşmadan ne yapılacağını göster
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

KOK = Path(__file__).parent
HAZIR = KOK / "hazir"
DURUM = KOK / "paylasildi.json"
API = f"https://graph.instagram.com/{os.environ.get('API_SURUM', 'v23.0')}"

ETIKETLER = "#derinizbirak #sözler #anlamlısözler #kısasözler #güzelsözler #duygusalsözler #alıntı"


def istek(yol, params, post=False):
    veri = urllib.parse.urlencode(params).encode()
    url = f"{API}/{yol}"
    req = urllib.request.Request(url, data=veri) if post else urllib.request.Request(f"{url}?{veri.decode()}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"API hatası {e.code}: {e.read().decode()}")


def aciklama(no):
    posts = json.loads((KOK / "posts.json").read_text(encoding="utf-8"))
    p = posts[no - 1]
    if p.get("duzen") == "alt":
        soz = f"{p['ana']} {p['ust']}"
    else:
        soz = f"{p['ust']} {p['ana']}"
    return f"{soz}\n\n{ETIKETLER}"


def siradaki():
    paylasilan = json.loads(DURUM.read_text()) if DURUM.exists() else []
    for f in sorted(HAZIR.glob("*.jpg")):
        if f.name not in paylasilan:
            return f, paylasilan
    return None, paylasilan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dene", action="store_true")
    a = ap.parse_args()

    dosya, paylasilan = siradaki()
    if not dosya:
        print("Kuyruk boş, paylaşılacak gönderi kalmadı.")
        return
    caption = aciklama(int(dosya.stem))
    taban = os.environ.get("GORSEL_TABAN", "<GORSEL_TABAN>").rstrip("/")
    gorsel_url = f"{taban}/{dosya.name}"
    print(f"Sıradaki: {dosya.name}\nURL: {gorsel_url}\nAçıklama:\n{caption}\n")
    if a.dene:
        return

    token = os.environ["IG_TOKEN"]
    ben = istek("me", {"fields": "user_id,username", "access_token": token})
    uid = ben.get("user_id") or ben["id"]
    print(f"Hesap: @{ben.get('username')}")

    kap = istek(f"{uid}/media", {"image_url": gorsel_url, "caption": caption, "access_token": token}, post=True)
    for _ in range(20):  # Instagram görseli işleyene kadar bekle
        d = istek(kap["id"], {"fields": "status_code", "access_token": token})
        if d.get("status_code") == "FINISHED":
            break
        if d.get("status_code") == "ERROR":
            sys.exit(f"Instagram görseli işleyemedi: {d}")
        time.sleep(5)
    yayin = istek(f"{uid}/media_publish", {"creation_id": kap["id"], "access_token": token}, post=True)
    print(f"Paylaşıldı, medya id: {yayin['id']}")

    paylasilan.append(dosya.name)
    DURUM.write_text(json.dumps(paylasilan, indent=1))


if __name__ == "__main__":
    main()
