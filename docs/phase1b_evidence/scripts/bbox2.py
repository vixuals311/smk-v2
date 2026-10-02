import sys, glob, os
from PIL import Image
thr=int(sys.argv[2]) if len(sys.argv)>2 else 45
for f in sorted(glob.glob(sys.argv[1])):
    im=Image.open(f).convert('L'); bb=im.point(lambda v:255 if v>thr else 0).getbbox()
    print(os.path.basename(f), "bbox", bb, "cx", (bb[0]+bb[2])/2 if bb else None, "cy", (bb[1]+bb[3])/2 if bb else None, "w", (bb[2]-bb[0]) if bb else None, "maxlum", max(im.getdata()))
