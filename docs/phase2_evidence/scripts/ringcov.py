import sys, math, glob
from PIL import Image
f=glob.glob(sys.argv[1])[0]; im=Image.open(f).convert('L'); px=im.load()
W=1920; cxs=[0.15+0.2*i for i in range(5)]
names=["Ring_Trim025","Ring_Trim025_Start025","Ring_TrimKeyframe","Ring_TrimMotionModifier","Line_Trim05"]
for i,n in enumerate(names[:4]):
    cx=cxs[i]*W; cy=540
    if n.startswith("Line"):
        xs=[x for x in range(int(cx-0.14*W/2*1.9), int(cx+0.25*W/2+40)) if px[x,cy]>150]
        print(n, "line x extent", (min(xs),max(xs)) if xs else None, "expected full", (cx-0.25*W/2, cx+0.25*W/2)); continue
    r=0.14*W/2-11   # ring centre-line radius
    cov=[]
    for deg in range(0,360,3):
        a=math.radians(deg)  # clockwise from 12 o'clock
        x=cx+r*math.sin(a); y=cy-r*math.cos(a)
        cov.append((deg, px[int(round(x)),int(round(y))]>150))
    on=[d for d,c in cov if c]
    # contiguous runs
    runs=[]; start=None
    for d,c in cov:
        if c and start is None: start=d
        if not c and start is not None: runs.append((start,d-3)); start=None
    if start is not None: runs.append((start,357))
    print(n, "covered degrees (clockwise from 12 o'clock):", runs)
