import glob
from PIL import Image
def isink(p): return (p[0]>200 and p[1]>200 and p[2]>200) or (p[0]<60 and p[1]<60 and p[2]<60)
def tip(px,W,H,x0=0,x1=None,y0=0,y1=None,step=1):
    x1=x1 or W; y1=y1 or H
    L=T=None; R=B=None
    for y in range(y0,y1,step):
        for x in range(x0,x1,step):
            if isink(px[x,y]):
                if L is None or x<L: L=x
                if T is None or y<T: T=y
                if R is None or x>R: R=x
                if B is None or y>B: B=y
    return (L,T,R,B) if L is not None else None
def blue(px,W,H,step=4):
    return sum(1 for y in range(0,H,step) for x in range(0,W,step) if px[x,y][2]>200 and px[x,y][0]<130)
