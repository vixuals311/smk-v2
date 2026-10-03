import glob,sys
from PIL import Image
d=sys.argv[1]; n0=int(sys.argv[2])
fs=sorted(glob.glob(d+'/r_*.png'))
bg=Image.open(fs[0]).convert('RGB').getpixel((3,3))
fr=[Image.open(f).convert('RGB').load() for f in fs]
# find letters from the earliest frame where they are fully visible: use max over frames per column
cols=set()
for px in fr:
    for x in range(300,1700):
        if x in cols: continue
        if any(px[x,y][0]-bg[0]>8 for y in range(470,610,2)): cols.add(x)
cols=sorted(cols); S=[];s=cols[0];p=cols[0]
for x in cols[1:]:
    if x-p>1: S.append((s,p)); s=x
    p=x
S.append((s,p))
def al(f,sg): 
    return max(fr[f][x,y][0]-bg[0] for x in range(sg[0],sg[1]+1) for y in range(470,610,2))/(255-bg[0])
res=[]
for sg in S:
    a=[al(f,sg) for f in range(len(fr))]
    out0=next((n0+k for k,v in enumerate(a) if v<0.97),None); gone=next((n0+k for k,v in enumerate(a) if v<0.03),None)
    res.append((out0,gone,round(a[-1],2)))
print(len(S),"letters; (Out start, gone, alpha on last rendered frame):",res)
