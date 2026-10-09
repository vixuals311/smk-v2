import sys,glob; sys.path.insert(0,'.')
from conn import *
W,H=1920,1080
def series(d,rows=6):
    out={i:[] for i in range(rows)}
    for f in sorted(glob.glob(d+'/*.png')):
        px=Image.open(f).convert('RGB').load()
        for i in range(rows):
            y=0.9-0.16*i; yc=int((1-y)*H); xs=[];ink=0
            for v in range(yc-40,yc+41,2):
                for u in range(0,W,2):
                    if blue(px[u,v]): ink+=1; xs.append(u)
            out[i].append((max(xs) if xs else -1,ink))
    return out
x0,x1=0.15*W,0.85*W
for d in sys.argv[1:]:
    s=series(d); n=len(s[0]); print(d,n,"frames")
    for i in range(6):
        prog=[max(0,(e-x0)/(x1-x0)) for e,_ in s[i]]; ink=[k for _,k in s[i]]
        first=next((k for k,p in enumerate(prog) if p>0.03),None); full=next((k for k,p in enumerate(prog) if p>=0.98),None)
        out=next((k for k in range(n//3,n) if prog[k]<0.97),None); gone=next((k for k in range(n//2,n) if ink[k]==0),None)
        print(" row%d first-progress f%s full f%s undraw-start f%s ink=0 from f%s last-frame ink %d"%(i,first,full,out,gone,ink[-1]))
