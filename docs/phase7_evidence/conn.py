import glob,math
from PIL import Image
def blue(p): return p[2]-p[0]>60
def blobs(px,W,H,x0,x1,y0,y1,k=2):
    pts=[(x,y) for y in range(max(0,y0),min(H,y1)) for x in range(max(0,x0),min(W,x1)) if blue(px[x,y])]
    ps=set(pts); core=[p for p in pts if all((p[0]+i,p[1]+j) in ps for i in range(-k,k+1) for j in range(-k,k+1))]
    return pts,core
def centroid(core): 
    return (sum(p[0] for p in core)/len(core)+0.5, sum(p[1] for p in core)/len(core)+0.5) if core else None
def magnet(c,hw,hh,mag,toward,gap):
    # port of smk.magnetPoint; y up coordinates in pixels
    if mag==0: return (c[0],c[1])
    if mag==2: nx,ny,px,py=0,1,c[0],c[1]+hh
    elif mag==3: nx,ny,px,py=1,0,c[0]+hw,c[1]
    elif mag==4: nx,ny,px,py=0,-1,c[0],c[1]-hh
    elif mag==5: nx,ny,px,py=-1,0,c[0]-hw,c[1]
    else:
        dx,dy=toward[0]-c[0],toward[1]-c[1]
        tx,ty=hw/max(abs(dx),1e-9),hh/max(abs(dy),1e-9); t=min(tx,ty); px,py=c[0]+dx*t,c[1]+dy*t
        if tx<ty: nx,ny=(1 if dx>=0 else -1),0
        else: nx,ny=0,(1 if dy>=0 else -1)
    return (px+nx*gap,py+ny*gap)
