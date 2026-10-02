import sys, glob, os
from PIL import Image, ImageStat
pre=sys.argv[1]; base=int(sys.argv[2]); n=int(sys.argv[3])
for f in range(n):
    g=glob.glob(f'{pre}*{base+f}.png')
    if not g: print(f,'missing'); continue
    im=Image.open(g[0]).convert('L'); bb=im.point(lambda v:255 if v>10 else 0).getbbox()
    print(f, "left", bb[0] if bb else None, "right", bb[2] if bb else None, "meanlum", round(ImageStat.Stat(im).mean[0],1))
