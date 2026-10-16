import glob
from PIL import Image
import numpy as np
NAMES=["TextLetter","TextWord","TextLine","ProgressRing","ProgressBar"]+[b+s for b in ("UIBlock","CardStack","StatCard","ClickDemo") for s in ("",""," Glass"," Neon"," Soft")]
names=["TextLetter","TextWord","TextLine","ProgressRing","ProgressBar"]
for b in ("UIBlock","CardStack","StatCard","ClickDemo"):
    for s in ("","Glass","Neon","Soft"): names.append((b+" "+s).strip())
rows=[]
for n in names:
    r=[]
    for lab in ("f0","f12","mid","last3"):
        d="p14_e3_SMK2_%s_%s"%(n.replace(" ","_"),lab); g=glob.glob(d+"/*.png")
        if not g: r.append(None); continue
        a=np.array(Image.open(g[0]).convert("RGB")).astype(int); b=a[2,2]
        r.append((int((np.abs(a[::4,::4]-b).max(axis=2)>6).sum()),tuple(int(x) for x in b)))
    rows.append((n,r))
for n,r in rows: print("| SMK2 %s | %s |"%(n," | ".join(str(x[0]) if x else "-" for x in r)), "bg",r[0][1] if r[0] else None)
