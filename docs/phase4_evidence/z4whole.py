import glob,sys
from PIL import Image
d=sys.argv[1]
fs=sorted(glob.glob(d+'/r_*.png')); bg=Image.open(fs[0]).convert('RGB').getpixel((3,3))
cy=int(1080*(1-0.2)); a=[]
for f in fs:
    px=Image.open(f).convert('RGB').load(); m=0
    for x in range(300,1700,2):
        for y in range(cy-130,cy+130,2):
            v=px[x,y][0]-bg[0]
            if v>m: m=v
    a.append(m/(255-bg[0]))
gone=next((i for i in range(60,len(a)) if a[i]<0.03),None); last_visible=max(i for i,v in enumerate(a) if v>=0.03)
print("3-line row whole-text alpha: last frame %.2f; whole text gone at frame %s; last frame with visible ink %s"%(a[-1],gone,last_visible))
