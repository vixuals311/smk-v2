import glob
from PIL import Image
W,H=1920,1080
def lum(p): return (p[0]+p[1]+p[2])/3
im=Image.open(glob.glob('r2/*.png')[0]).convert('RGB'); px=im.load(); im.save('r2_dirs.png')
hw=int(0.12*1920/2); hh=int(0.10*1920/2)
for i,d in enumerate((0,90,135,225)):
    cx=int((0.5+i)/4*W); cy=540; base=lum(px[cx,cy])
    e={"left":lum(px[cx-hw+3,cy]),"right":lum(px[cx+hw-4,cy]),"top":lum(px[cx,cy-hh+3]),"bottom":lum(px[cx,cy+hh-4])}
    print("dir %3d: centre %.0f; edge delta left %+.0f right %+.0f top %+.0f bottom %+.0f"%(d,base,e['left']-base,e['right']-base,e['top']-base,e['bottom']-base))
im=Image.open(glob.glob('r3/*.png')[0]).convert('RGB'); px=im.load(); im.save('r3_size_depth.png')
hw=int(0.14*1920/2); hh=int(0.12*1920/2)
for i,lab in enumerate(["size2 d2","size8 d2","size30 d2","size8 d0","size8 d1","size8 d2","size8 d6"]):
    cols=4; cx=int((0.5+i%cols)/cols*W); cy=int((0.5+i//cols)/2*H)
    base=lum(px[cx,cy])
    lp=[lum(px[cx-hw+k,cy])-base for k in range(0,70)]; rp=[lum(px[cx+hw-1-k,cy])-base for k in range(0,70)]
    wl=max([k for k,v in enumerate(lp) if abs(v)>2] or [0])+1
    print("%-9s centre %.0f; lit(left) first px %+.0f max %+.0f width(>2) %d | shadow(right) first px %+.0f min %+.0f"%(lab,base,lp[0],max(lp),wl,rp[0],min(rp)))
