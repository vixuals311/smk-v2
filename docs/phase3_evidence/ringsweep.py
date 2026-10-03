import sys, glob, math
from PIL import Image
def sweep(path, cx=960, cy=540, r=140, step=1):
    im=Image.open(path).convert('RGB'); px=im.load(); n=0
    for d in range(0,360,step):
        a=math.radians(d); x=int(round(cx+r*math.sin(a))); y=int(round(cy-r*math.cos(a)))
        R,G,B=px[x,y]
        if B>200 and R<130 and G>100: n+=1
    return n*step
if __name__=="__main__":
    for f in sys.argv[2:]:
        g=glob.glob(f'{sys.argv[1]}*{86400+int(f)}.png')
        print(f, sweep(g[0]) if g else None)
