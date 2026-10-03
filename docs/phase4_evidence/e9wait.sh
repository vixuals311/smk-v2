d=$1
until [ $(ls $d 2>/dev/null | wc -l) -ge 300 ]; do sleep 1; done; sleep 2
python - <<P
import os,glob
fs=sorted(glob.glob("$d/r_*.png")); m=[os.path.getmtime(f) for f in fs]
print("$d", "ms/frame %.1f"%((max(m)-min(m))/(len(fs)-1)*1000))
P
