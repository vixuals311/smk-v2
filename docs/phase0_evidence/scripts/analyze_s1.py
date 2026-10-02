import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert("RGB"); W,H=im.size; px=im.load()
print(sys.argv[1], "size",W,H)
chk=int(sys.argv[2])
# gradient: R ~ x/W, G ~ y/H (or flipped), B ~ .5 ; sample cell-centres to avoid checker darkening
def at(x,y): return px[x,y]
print("corners", at(8,8), at(W-9,8), at(8,H-9), at(W-9,H-9))
# detect cell width/height along centre row/col via brightness transitions of B channel (0.5*k)
def runs(vals):
    r=[];c=1
    for a,b in zip(vals,vals[1:]):
        if abs(a-b)>20: r.append(c); c=1
        else: c+=1
    r.append(c); return r
row=[px[x,H//2][2] for x in range(W)]; col=[px[W//2,y][2] for y in range(H)]
rr=runs(row); cr=runs(col)
print("horizontal run lengths (first 12):", rr[:12]); print("vertical run lengths (first 12):", cr[:12])
print("blue mean", sum(row)/len(row))
