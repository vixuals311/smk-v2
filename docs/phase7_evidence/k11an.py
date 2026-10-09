import sys,glob,math; sys.path.insert(0,'.')
from PIL import Image
def bez(P,t):
    u=1-t; return (u**3*P[0][0]+3*u*u*t*P[1][0]+3*u*t*t*P[2][0]+t**3*P[3][0],u**3*P[0][1]+3*u*u*t*P[1][1]+3*u*t*t*P[2][1]+t**3*P[3][1])
def curve_ctrl(pa,pb,bend=0.45):
    d=math.hypot(pb[0]-pa[0],pb[1]-pa[1]); k=bend*d; ux,uy=(pb[0]-pa[0])/d,(pb[1]-pa[1])/d
    return [pa,(pa[0]+ux*k,pa[1]+uy*k),(pb[0]-ux*k,pb[1]-uy*k),pb]
def spline_segs(P,tn=1/6):
    segs=[]
    for i in range(len(P)-1):
        p0,p1,p2,p3=P[max(i-1,0)],P[i],P[i+1],P[min(i+2,len(P)-1)]
        segs.append([p1,(p1[0]+(p2[0]-p0[0])*tn,p1[1]+(p2[1]-p0[1])*tn),(p2[0]-(p3[0]-p1[0])*tn,p2[1]-(p3[1]-p1[1])*tn),p2])
    return segs
def dense(segs,n=1500): return [bez(s,j/n) for s in segs for j in range(n+1)]
def poly_dev(segs_sample, segs_true):
    """max distance of true dense curve from the sampled polyline (what the Fuse draws)"""
    pass
def seg_dist(poly,x,y):
    m=1e18
    for a,b in zip(poly,poly[1:]):
        ex,ey=b[0]-a[0],b[1]-a[1]; l=ex*ex+ey*ey; t=max(0,min(1,((x-a[0])*ex+(y-a[1])*ey)/l)) if l>0 else 0
        m=min(m,(x-(a[0]+t*ex))**2+(y-(a[1]+t*ey))**2)
    return math.sqrt(m)
def build(W,H):
    Wf,Hf=W,H
    P=lambda x,y:(x*Wf,y*Hf)
    c=curve_ctrl(P(0.05,0.95),P(0.95,0.7))
    b=[P(0.1,0.45),P(0.95,0.62),P(0.05,0.62),P(0.9,0.45)]
    pts=[P(0.05,0.15)]+[P(0.05+0.15*(k+1),0.15+(0.07 if k%2==0 else -0.07)) for k in range(6)]+[P(0.95,0.15)]
    return {"Curve":[c],"Bezier":[b],"Spline":spline_segs(pts)}
def sample_poly(segs,mode,N):
    """the exact 64-sample (or spline) polyline the Fuse draws, y up"""
    if mode!="Spline": s=segs[0]; return [bez(s,i/63) for i in range(64)]
    per=max(3,math.floor(90/len(segs))); out=[]
    for i,s in enumerate(segs):
        for j in range(0 if i==0 else 1,per+1): out.append(bez(s,j/per))
    return out
if __name__=="__main__":
    for tag,W,H in (("1080p",1920,1080),("1080x1920",1080,1920),("4K",3840,2160)):
        im=Image.open(glob.glob('k11_%s/*.png'%tag)[0]).convert('RGB'); px=im.load()
        S=build(W,H); print(tag,W,H)
        for name,segs in S.items():
            tr=dense(segs); smp=sample_poly(segs,name,64)
            facet=max(seg_dist(smp,x,y) for x,y in tr[::25])   # distance of true curve from drawn polyline
            # rendered ink distance to true curve (image y down -> flip)
            trd=[(x,H-y) for x,y in tr]
            cell=24; grid={}
            for k,(x,y) in enumerate(trd): grid.setdefault((int(x//cell),int(y//cell)),[]).append((x,y))
            worst=0; n=0
            for v in range(0,H,3):
                for u in range(0,W,3):
                    p=px[u,v]
                    if p[2]-p[0]>60:
                        cx,cy=int(u//cell),int(v//cell); best=1e9
                        for dx in (-1,0,1):
                            for dy in (-1,0,1):
                                for (x,y) in grid.get((cx+dx,cy+dy),()): best=min(best,math.hypot(u+.5-x,v+.5-y))
                        if best<1e9: worst=max(worst,best); n+=1
            thick=3*W/1920
            print("  %-6s polyline(64pt)-vs-true-curve max deviation %.3f px; rendered ink px farthest from true centreline %.2f px (half thickness %.1f); sampled ink px %d"%(name,facet,worst,thick/2,n))
