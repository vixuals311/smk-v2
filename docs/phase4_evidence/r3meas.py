import glob,sys
from PIL import Image
def run(d60,d119,ys,names,half=55):
    a=Image.open(glob.glob(d60+'/*.png')[0]).convert('RGB'); bg=a.getpixel((3,3)); pa=a.load()
    fs=sorted(glob.glob(d119+'/*.png')); pb=Image.open(fs[-1]).convert('RGB').load()
    worst=0
    for y,n in zip(ys,names):
        cy=int(1080*(1-y))
        ink=sum(1 for x in range(100,1900,2) for yy in range(cy-half,cy+half,2) if pa[x,yy][0]-bg[0]>60)
        m=max(pb[x,yy][0]-bg[0] for x in range(100,1900,2) for yy in range(cy-half-30,cy+half+30,2))/(255-bg[0])
        worst=max(worst,m); print("  %-28s ink@rest %5d | last-frame alpha %.2f"%(n,ink,m))
    print("  max last-frame alpha:",round(worst,2))
if __name__=="__main__":
    run(sys.argv[1],sys.argv[2],eval(sys.argv[3]),eval(sys.argv[4]))
