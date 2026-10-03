import glob
from PIL import Image
def segs(path, cy=540, half=100, gap=0, x0=0, x1=1920, thr=40):
    im=Image.open(path).convert('RGB'); px=im.load(); bg=px[3,3]
    cols=[x for x in range(x0,x1) if any(sum(abs(a-b) for a,b in zip(px[x,y],bg))>thr for y in range(cy-half,cy+half,2))]
    if not cols: return []
    out=[];s=cols[0];p=cols[0]
    for x in cols[1:]:
        if x-p>gap+1: out.append((s,p)); s=x
        p=x
    out.append((s,p)); return out
def stat(path, seg, y0=0, y1=1080):
    px=Image.open(path).convert('RGB').load(); bg=px[3,3]; best=0; ys=[]
    for x in range(seg[0],seg[1]+1):
        for y in range(y0,y1,2):
            d=px[x,y][0]-bg[0]
            if d>best: best=d
            if d>30: ys.append(y)
    return best/(255-bg[0]), (min(ys),max(ys)) if ys else None
