import glob,sys
from PIL import Image
def run(d, unit):
    fs=sorted(glob.glob(d+'/r_*.png'))
    bg=Image.open(fs[0]).convert('RGB').getpixel((3,3))
    fr=[Image.open(f).convert('RGB').load() for f in fs]
    YS=[0.9,0.75,0.6,0.45,0.2]; names=["SMK TEXT DEMO","ONE TWO THREE","HELLO","A","3 lines"]
    d_=lambda p: p[0]-bg[0]>8
    for r,(y,nm) in enumerate(zip(YS,names)):
        cy=int(1080*(1-y)); half=130 if r==4 else 40
        y0,y1=cy-half,cy+half
        # union of ink over all frames
        cols=set(); rows=set()
        for px in fr[::3]:
            for x in range(300,1700,2):
                if any(d_(px[x,yy]) for yy in range(y0,y1,2)): cols.add(x)
            for yy in range(y0,y1,2):
                if any(d_(px[x,yy]) for x in range(300,1700,4)): rows.add(yy)
        if not cols: print(nm,"no ink"); continue
        cols=sorted(cols); rows=sorted(rows)
        def segs(v,gap):
            S=[];s=v[0];p=v[0]
            for x in v[1:]:
                if x-p>gap: S.append((s,p)); s=x
                p=x
            S.append((s,p)); return S
        if unit=="line":
            units=[(None,b) for b in segs(rows,10)]; boxes=[((min(cols),max(cols)),b) for _,b in units]
        else:
            if r==4:
                bands=segs(rows,10); boxes=[]
                for b in bands:
                    cs=sorted(x for x in cols if any(d_(px[x,yy]) for px in fr[::3] for yy in range(b[0],b[1]+1,2)))
                    for s in segs(cs,3 if unit=="letter" else 12): boxes.append((s,b))
            else:
                boxes=[(s,(y0,y1)) for s in segs(cols,3 if unit=="letter" else 12)]
        res=[]
        for (xa,xb),(ya,yb) in boxes:
            def al(f):
                px=fr[f]; m=0
                for x in range(xa,xb+1,2):
                    for yy in range(ya,yb+1,2):
                        v=px[x,yy][0]-bg[0]
                        if v>m: m=v
                return m/(255-bg[0])
            a=[al(f) for f in range(len(fr))]
            peak=max(a); out0=next((f for f in range(60,len(a)) if a[f]<0.97*peak),None); gone=next((f for f in range(60,len(a)) if a[f]<0.03),None)
            res.append((out0,gone,round(a[-1],2)))
        last_gone=max((g for _,g,_ in res if g is not None),default=None)
        print(nm,"| %d %ss | max last-frame alpha: %.2f"%(len(res),unit,max(x[2] for x in res)),"| first unit Out start/gone:",res[0][:2],"| last unit Out start/gone:",res[-1][:2],"| last unit gone at frame",last_gone,"=> %s frames before the last frame (119)"%(119-last_gone if last_gone is not None else "n/a"))
if __name__=="__main__": run(sys.argv[1],sys.argv[2])
