import json, shutil
from pathlib import Path
from PIL import Image
# aday no -> (post sırası 1-tabanlı, y, renk)
esle = {"25":(1,0.22,"beyaz"),"41":(2,0.22,"auto"),"58":(3,0.30,"auto"),"47":(6,0.20,"auto"),
        "08":(10,0.20,"siyah"),"03":(12,0.22,"auto"),"38":(14,0.20,"auto"),"54":(17,0.22,"auto"),
        "46":(19,0.30,"auto"),"13":(20,0.18,"beyaz"),"43":(22,0.20,"auto"),"37":(25,0.20,"auto"),
        "07":(28,0.22,"auto"),"20":(29,0.16,"beyaz")}
satirlar = Path("aday/liste.txt").read_text().splitlines()
posts = json.loads(Path("posts.json").read_text(encoding="utf-8"))
kaynak = []
for no,(idx,y,renk) in esle.items():
    q,id_,url,wh = satirlar[int(no)-1].split("|")
    ad = f"ov_{no}.jpg"
    Image.open(f"aday/{no}.jpg").convert("RGB").save(f"input/{ad}", quality=95)
    p = posts[idx-1]
    p.update(gorsel=ad, y=y, renk=renk)
    if p.get("duzen") == "alt": p["y"] = y + 0.12
    kaynak.append(f"{ad}\t{url}\tCC0/PD (Openverse id {id_})")
    print(idx, ad, Image.open(f"input/{ad}").size)
Path("posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=1), encoding="utf-8")
Path("input/KAYNAKLAR.txt").write_text("\n".join(kaynak)+"\n", encoding="utf-8")
