import glob,sys
from PIL import Image
def an(d,step=4):
    im=Image.open(glob.glob(d+"/*.png")[0]).convert("RGB"); px=im.load(); b=px[5,5]; n=0
    for y in range(0,1080,step):
        for x in range(0,1920,step):
            if max(abs(px[x,y][c]-b[c]) for c in range(3))>6: n+=1
    return b[0],n
if __name__=="__main__":
    name=sys.argv[1]; tags=sys.argv[2].split(","); frames=[int(x) for x in sys.argv[3].split(",")]
    for tg in tags:
        print(tg,[ (f,)+an("p13_%s_%s_f%d"%(name,tg,f)) for f in frames])
