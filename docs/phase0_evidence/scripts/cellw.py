import sys, glob
from PIL import Image
def cellw(f):
    im=Image.open(f).convert('RGB'); W,H=im.size; px=im.load()
    y=H//2+7
    lum=[sum(px[x,y]) for x in range(W)]
    w=64; pre=[0]
    for v in lum: pre.append(pre[-1]+v)
    sg=[]
    for x in range(W):
        a=max(0,x-w); b=min(W,x+w+1); m=(pre[b]-pre[a])/(b-a)
        sg.append(lum[x]>m)
    tr=[i for i in range(1,W) if sg[i]!=sg[i-1]]
    ds=sorted(b-a for a,b in zip(tr,tr[1:]))
    return (ds[len(ds)//2] if ds else 0)
for f in sorted(glob.glob(sys.argv[1])):
    c=cellw(f); print(f.split('/')[-1], "cell px", c, "=> size", round(c/32,3))
