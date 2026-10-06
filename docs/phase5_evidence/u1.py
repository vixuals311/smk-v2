import glob,sys
from PIL import Image
Y=[0.92,0.8,0.68,0.56,0.44,0.32,0.15]; N=["accents","emoji","SMK TEXT DEMO","ONE TWO THREE","HELLO","A","2-line accents"]
def run(d):
    fs=sorted(glob.glob(d+'/r_*.png')); bg=Image.open(fs[0]).convert('RGB').getpixel((3,3))
    fr=[Image.open(f).convert('RGB').load() for f in fs]
    for y,n in zip(Y,N):
        cy=int(1080*(1-y)); half=120 if n=="2-line accents" else 50
        a=[]
        for px in fr:
            m=0
            for x in range(300,1700,2):
                for yy in range(max(0,cy-half),cy+half,2):
                    v=px[x,yy][0]-bg[0]
                    if v>m: m=v
            a.append(m/(255-bg[0]))
        gone=next((f for f in range(60,len(a)) if a[f]<0.03),None)
        print("  %-15s last-frame alpha %.2f | whole row (last letter / its text) gone at frame %s (%s frames before last)"%(n,a[-1],gone,119-gone if gone is not None else "n/a"))
if __name__=="__main__": run(sys.argv[1])
