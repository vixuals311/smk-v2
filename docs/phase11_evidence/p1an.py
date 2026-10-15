import glob,sys
from PIL import Image
W,H=1920,1080
fs=sorted(glob.glob(sys.argv[1]+'/*.png')); print(len(fs))
bg=(26,31,51)
def cards(n=4,gap=0.015,h=0.07,cy0=0.72,cx=0.5,w=0.34,asp=W/H):
    out=[]
    for i in range(n):
        cy=cy0-i*(h+gap)*asp
        out.append((int(cx*W-w*W/2),int((1-cy)*H-h*W/2),int(cx*W+w*W/2),int((1-cy)*H+h*W/2)))
    return out
reg=cards()
first=[None]*4; last=[None]*4; cnt={}
for k,f in enumerate(fs):
    px=Image.open(f).convert('RGB').load()
    tot=0
    for i,(x0,y0,x1,y1) in enumerate(reg):
        ink=sum(1 for y in range(y0+10,y1-10,6) for x in range(x0+20,x1-20,12) if max(abs(px[x,y][c]-bg[c]) for c in range(3))>12)
        if ink>20:
            if first[i] is None: first[i]=k
            last[i]=k
        tot+=ink
    cnt[k]=tot
print("regions",reg)
print("first ink frame per card",first,"last ink frame per card",last)
print("last frame ink (sampled px over the 4 card regions):",cnt[len(fs)-1],"; frame 0:",cnt[0])
