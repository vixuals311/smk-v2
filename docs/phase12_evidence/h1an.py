import glob,sys,json
from PIL import Image
def nb(d,bg=(51,51,64),step=4,thr=6):
    fs=glob.glob('p12_h1_'+d+'/*.png')
    if not fs: return None
    px=Image.open(fs[0]).convert('RGB').load(); W,H=Image.open(fs[0]).size
    n=tot=0
    for y in range(0,H,step):
        for x in range(0,W,step):
            e=max(abs(px[x,y][c]-bg[c]) for c in range(3))
            if e>thr: n+=1; tot+=e
    return n
if __name__=="__main__":
    for a in sys.argv[1:]:
        print(a,[nb('%s_f%d'%(a,f)) for f in (3,12,60,116)])
