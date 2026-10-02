import sys, glob, os
from PIL import Image
for f in sorted(glob.glob(sys.argv[1])):
    im=Image.open(f).convert('RGB'); W,H=im.size
    g=im.convert('L'); bb=g.point(lambda v:255 if v>8 else 0).getbbox()
    mx=max(g.getdata())
    print(os.path.basename(f), "bbox", bb, "cx", (bb[0]+bb[2])/2 if bb else None, "maxlum", mx)
