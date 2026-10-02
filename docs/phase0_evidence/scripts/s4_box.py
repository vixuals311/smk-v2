import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB'); W,H=im.size; px=im.load()
xs=[x for x in range(W) if px[x,H//2][0]>200]; ys=[y for y in range(H) if px[W//2,y][0]>200]
print(sys.argv[1], "orange x",(min(xs),max(xs)) if xs else None,"y",(min(ys),max(ys)) if ys else None, "center",px[W//2,H//2], "corner", px[5,5])
