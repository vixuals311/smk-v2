import glob,sys
from PIL import Image
def firsts(d, cy, nframes, half=60, gap=6, thr=150, x0=200, x1=1750):
    fs=sorted(glob.glob(d+'/r_*.png'))
    last=Image.open(fs[min(nframes,len(fs)-1)]).convert('RGB').load()
    cols=[x for x in range(x0,x1) if any(last[x,y][0]>thr for y in range(cy-half,cy+half,2))]
    segs=[];s=cols[0];p=cols[0]
    for x in cols[1:]:
        if x-p>gap: segs.append((s,p)); s=x
        p=x
    segs.append((s,p))
    first=[None]*len(segs); 
    for f in range(0,min(nframes,len(fs)-1)+1):
        q=Image.open(fs[f]).convert('RGB').load()
        for i,(a,b) in enumerate(segs):
            if first[i] is None and any(q[x,y][0]>thr for x in range(a,b+1,2) for y in range(cy-half,cy+half,3)): first[i]=f
    return first,segs
