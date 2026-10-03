import glob,sys
from PIL import Image
def letters(path, cy=540, half=70, x0=100, x1=1820, gap=5, bg=None):
    im=Image.open(path).convert('RGB'); px=im.load(); bg=bg or px[3,3]
    d=lambda p: sum(abs(a-b) for a,b in zip(p,bg))
    cols=[x for x in range(x0,x1) if any(d(px[x,y])>12 for y in range(cy-half,cy+half,2))]
    if not cols: return []
    segs=[];s=cols[0];p=cols[0]
    for x in cols[1:]:
        if x-p>gap: segs.append((s,p)); s=x
        p=x
    segs.append((s,p)); return segs
def peak(path, seg, cy=540, half=70):
    px=Image.open(path).convert('RGB').load(); bg=px[3,3]
    best=0
    for x in range(seg[0],seg[1]+1):
        for y in range(cy-half,cy+half,2):
            best=max(best,px[x,y][0]-bg[0])
    return best
