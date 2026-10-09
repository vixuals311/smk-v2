import sys,glob,json,math; sys.path.insert(0,'.')
from conn import *
W,H=1920,1080
names=["Off","Auto","Top","Right","Bottom","Left"]
def run(d,cells,label):
    px=Image.open(glob.glob(d+'/*.png')[0]).convert('RGB').load()
    worst=0
    for k,(cx,cy,tx,ty,mag,aw,ah,gap) in enumerate(cells):
        hw,hh=aw*W/2,ah*W/2
        ex=magnet((cx,cy),hw,hh,mag,(tx,ty),gap)
        ix,iy=ex[0],H-ex[1]
        pts,core=blobs(px,W,H,int(ix)-30,int(ix)+30,int(iy)-30,int(iy)+30)
        c=centroid(core)
        err=math.hypot(c[0]-ix,c[1]-iy)
        # direction check: ink in annulus 25-45 around exit vs ideal curve
        pa=ex; pb=(tx,ty); dist=math.hypot(pb[0]-pa[0],pb[1]-pa[1]); kk=0.45*dist
        # outward normal
        if mag==1:
            dx,dy=tx-cx,ty-cy; txx=hw/max(abs(dx),1e-9); tyy=hh/max(abs(dy),1e-9)
            n=((1 if dx>=0 else -1),0) if txx<tyy else (0,(1 if dy>=0 else -1))
        else: n={0:(0,0),2:(0,1),3:(1,0),4:(0,-1),5:(-1,0)}[mag]
        da=n if mag else ((pb[0]-pa[0])/dist,(pb[1]-pa[1])/dist)
        db=((pa[0]-pb[0])/dist,(pa[1]-pb[1])/dist)
        P=[pa,(pa[0]+da[0]*kk,pa[1]+da[1]*kk),(pb[0]+db[0]*kk,pb[1]+db[1]*kk),pb]
        ref=[]
        for i in range(2001):
            t=i/2000;u=1-t
            ref.append((u**3*P[0][0]+3*u*u*t*P[1][0]+3*u*t*t*P[2][0]+t**3*P[3][0], H-(u**3*P[0][1]+3*u*u*t*P[1][1]+3*u*t*t*P[2][1]+t**3*P[3][1])))
        sel=[(x,y) for y in range(max(0,int(iy)-50),min(H,int(iy)+51)) for x in range(int(ix)-50,int(ix)+51) if 25<=math.hypot(x+.5-ix,y+.5-iy)<=45 and blue(px[x,y])]
        rs=[q for q in ref if 25<=math.hypot(q[0]-ix,q[1]-iy)<=45]
        if sel and rs:
            mx=sum(p[0]+.5 for p in sel)/len(sel); my=sum(p[1]+.5 for p in sel)/len(sel)
            am=math.degrees(math.atan2(-(my-iy),mx-ix)); ae=math.degrees(math.atan2(-(sum(q[1] for q in rs)/len(rs)-iy),sum(q[0] for q in rs)/len(rs)-ix))
        else: am=ae=float('nan')
        worst=max(worst,err)
        print("%s #%d mag=%-6s box=%.2fx%.2f gap=%2d: expected exit (%.1f,%.1f) measured (%.1f,%.1f) err %.2f px | leave angle measured %.1f ideal %.1f"%(label,k,names[mag],aw,ah,gap,ix,iy,c[0],c[1],err,am,ae))
    print("worst exit error",round(worst,2))
run('k5_magnets',json.load(open('k5_cells.json')),'M')
run('k5_compass',json.load(open('k5c_cells.json')),'C')
