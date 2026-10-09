import glob
from PIL import Image
def load(d): 
    fs=sorted(glob.glob(d+'/r_*.png')); return [Image.open(f).convert('RGB') for f in fs]
def white(px,x0,x1,y0,y1,step=1):
    n=0; xs=[];ys=[]
    for y in range(y0,y1,step):
        for x in range(x0,x1,step):
            p=px[x,y]
            if p[0]>215 and p[1]>215 and p[2]>215: n+=1; xs.append(x); ys.append(y)
    return n,xs,ys
def card(px,W,H,step=2):
    n=0; xs=[];ys=[]
    for y in range(0,H,step):
        for x in range(0,W,step):
            p=px[x,y]
            if p[0]<90 and p[2]>p[0]+25: n+=1; xs.append(x); ys.append(y)
    return n,xs,ys
