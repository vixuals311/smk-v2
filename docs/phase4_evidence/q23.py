import glob,sys
from PIL import Image
def segs(v,gap):
    if not v: return []
    S=[];s=v[0];p=v[0]
    for x in v[1:]:
        if x-p>gap: S.append((s,p)); s=x
        p=x
    S.append((s,p)); return S
def load(d):
    fs=sorted(glob.glob(d+'/r_*.png')); bg=Image.open(fs[0]).convert('RGB').getpixel((3,3))
    return bg,[Image.open(f).convert('RGB').load() for f in fs]
def units(fr,bg,unit,cy,half,ref=60):
    px=fr[ref]; d=lambda p:p[0]-bg[0]>40
    if unit=="word":
        cols=[x for x in range(300,1700) if any(d(px[x,y]) for y in range(cy-half,cy+half,2))]
        return [((a,b),(cy-half,cy+half)) for a,b in segs(cols,9)]
    rows=[y for y in range(cy-half,cy+half) if any(d(px[x,y]) for x in range(300,1700,3))]
    cols=[x for x in range(300,1700) if any(d(px[x,y]) for y in range(cy-half,cy+half,2))]
    return [((min(cols),max(cols)),(a-4,b+4)) for a,b in segs(rows,8)]
def alpha_series(fr,bg,box,pad_x=0,pad_y=0):
    (xa,xb),(ya,yb)=box; out=[]
    for px in fr:
        m=0
        for x in range(max(0,xa-pad_x),xb+pad_x+1,2):
            for y in range(max(0,ya-pad_y),yb+pad_y+1,2):
                v=px[x,y][0]-bg[0]
                if v>m: m=v
        out.append(m/(255-bg[0]))
    return out
if __name__=="__main__":
    d,unit=sys.argv[1],sys.argv[2]
    texts=eval(sys.argv[3]); ys=eval(sys.argv[4]); halfs=eval(sys.argv[5])
    bg,fr=load(d)
    for t,y,h in zip(texts,ys,halfs):
        cy=int(1080*(1-y)); U=units(fr,bg,unit,cy,h)
        res=[]
        for box in U:
            a=alpha_series(fr,bg,box,pad_y=0 if unit=="line" else 70)
            pk=max(a[60:100]); s=next((f for f in range(60,len(a)) if a[f]<0.97*pk),None); g=next((f for f in range(60,len(a)) if a[f]<0.03),None)
            res.append((s,g,round(a[-1],2)))
        print(repr(t),"| %d %ss | (alpha-Out starts, alpha gone, last-frame alpha) per unit:"%(len(U),unit),res)
