import sys
from pathlib import Path
from PIL import Image, ImageDraw
d=Path(sys.argv[1]); files=sorted(d.glob('[0-9][0-9].jpg'))
cols=8; tw,th=240,300
sheet=Image.new('RGB',(cols*tw,((len(files)+cols-1)//cols)*th),'white'); dr=ImageDraw.Draw(sheet)
for i,f in enumerate(files):
    try: im=Image.open(f).convert('RGB'); im.thumbnail((tw-6,th-26))
    except Exception: continue
    x,y=(i%cols)*tw,(i//cols)*th
    sheet.paste(im,(x+3,y+3)); dr.text((x+5,y+th-20),f.stem,fill='red')
sheet.save(d/'kontakt.jpg',quality=80)
