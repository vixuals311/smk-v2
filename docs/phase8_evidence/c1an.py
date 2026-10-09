import glob,sys
from PIL import Image
W,H=1920,1080
fs=sorted(glob.glob(sys.argv[1]+'/*.png')); print(len(fs),"frames")
bgp=Image.open(fs[-1]).convert('RGB').getpixel((5,5)); print("bg",bgp)
def prof(im):
    px=im.load(); cols=[]
    for x in range(0,W,8):
        ink=sum(1 for y in range(0,H,12) if max(abs(px[x,y][c]-bgp[c]) for c in range(3))>3)
        cols.append(ink)
    return cols
rows=[]
for k in range(0,len(fs),2):
    im=Image.open(fs[k]).convert('RGB'); c=prof(im); n=H//12
    cov=sum(c)/(len(c)*n)           # fraction of frame covered by anything
    filled=[x*8 for x,v in enumerate(c) if v>0.5*n]   # columns mostly covered
    rows.append((k,cov,min(filled) if filled else None,max(filled) if filled else None))
for r in rows[:30]: print("frame %3d coverage %.3f covered cols %s..%s"%r)
print("... last",rows[-1])
