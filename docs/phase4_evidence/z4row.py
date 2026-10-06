import glob,sys
from PIL import Image
YS=[0.9,0.75,0.6,0.45,0.2]; N=["SMK TEXT DEMO","ONE TWO THREE","HELLO","A","3-line text"]
def run(d):
    fs=sorted(glob.glob(d+'/r_*.png')); bg=Image.open(fs[0]).convert('RGB').getpixel((3,3))
    fr=[Image.open(f).convert('RGB').load() for f in fs]
    for r,(y,nm) in enumerate(zip(YS,N)):
        cy=int(1080*(1-y)); half=160 if r==4 else 75
        a=[]
        for px in fr:
            m=0
            for x in range(300,1700,2):
                for yy in range(cy-half,cy+half,2):
                    v=px[x,yy][0]-bg[0]
                    if v>m: m=v
            a.append(m/(255-bg[0]))
        pk=max(a); first=next(f for f in range(40,len(a)) if a[f]<0.97*pk)
        gone=next((f for f in range(first,len(a)) if a[f]<0.03),None)
        print("  %-14s last-frame alpha %.2f | whole-row Out starts frame %d | whole row gone at frame %s (%s frames before last)"%(nm,a[-1],first,gone,119-gone if gone is not None else "n/a"))
for d in sys.argv[1:]:
    print(d); run(d)
