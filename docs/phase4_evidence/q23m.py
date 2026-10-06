import sys
sys.path.insert(0,'.')
from q23 import *
def run(d,unit,texts,ys,halfs,axis):
    bg,fr=load(d)
    for t,y,h in zip(texts,ys,halfs):
        cy=int(1080*(1-y)); U=units(fr,bg,unit,cy,h)
        res=[]
        for (xa,xb),(ya,yb) in U:
            def cen(f):
                px=fr[f]; sx=sy=n=0
                for x in range(max(0,xa-(150 if axis=="x" else 0)),min(1919,xb+(150 if axis=="x" else 0))+1,2):
                    for yy in range(max(0,ya-(0 if axis=="x" else 100)),min(1079,yb+(0 if axis=="x" else 100))+1,2):
                        v=px[x,yy][0]-bg[0]
                        if v>60: sx+=x; sy+=yy; n+=1
                return ((sx/n) if axis=="x" else (sy/n)) if n else None
            c=[cen(f) for f in range(len(fr))]
            rest=c[60]; off=[(v-rest) if v is not None else None for v in c]
            mx=max(abs(o) for o in off if o is not None)
            # In: offset from 0 to start
            inS=next((f for f in range(0,60) if off[f] is not None and abs(off[f])<0.98*mx),None)
            inF=next((f for f in range(0,60) if off[f] is not None and abs(off[f])<1.0),None)
            outS=next((f for f in range(60,len(off)) if off[f] is not None and abs(off[f])>1.0),None)
            outF=next((f for f in range(60,len(off)) if off[f] is not None and abs(off[f])>0.98*mx),None)
            res.append((inS,inF,outS,outF,round(abs(off[-1])/mx,2)))
        print(repr(t),"| (In starts, In finishes, Out starts, Out finishes, final offset/start offset) per",unit,":",res)
if __name__=="__main__":
    run(sys.argv[1],sys.argv[2],eval(sys.argv[3]),eval(sys.argv[4]),eval(sys.argv[5]),sys.argv[6])
