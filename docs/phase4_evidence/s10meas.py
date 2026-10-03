import glob,sys
from PIL import Image
def letter_alpha(path, cy=540, half=70, x0=300, x1=1700):
    im=Image.open(path).convert('RGB'); px=im.load(); bg=px[3,3]
    cols=[x for x in range(x0,x1) if any(px[x,y][0]-bg[0]>8 for y in range(cy-half,cy+half,2))]
    if not cols: return []
    S=[];s=cols[0];p=cols[0]
    for x in cols[1:]:
        if x-p>1: S.append((s,p)); s=x
        p=x
    S.append((s,p))
    out=[]
    for a,b in S:
        m=0
        for x in range(a,b+1):
            for y in range(cy-half,cy+half,2): m=max(m,px[x,y][0]-bg[0])
        out.append(round(m/(255-bg[0]),2))
    return out
if __name__=="__main__":
    print(letter_alpha(glob.glob(sys.argv[1])[0]))
