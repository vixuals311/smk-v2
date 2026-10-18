import glob, sys, json
import numpy as np
from PIL import Image
R = "D:/Softwares/SMK v2/docs/phase16_evidence/renders/"
BGC = np.array([51, 51, 64])
def load(tag, f):
    fs = glob.glob("%s%s_f%d/*.png" % (R, tag, f))
    return np.asarray(Image.open(fs[0]).convert("RGB")).astype(int) if fs else None
def nb(a, step=4, thr=6):  # same method as Phase 12 h1an.py
    s = a[::step, ::step]; return int((np.abs(s - BGC).max(axis=2) > thr).sum())
def counts(tag, frames=(3, 12, 60, 116)):
    return [nb(load(tag, f)) if load(tag, f) is not None else None for f in frames]
if __name__ == "__main__":
    for t in sys.argv[1:]: print(t, counts(t))
