import glob,os,sys
base='p8bench/'
for d in sorted(glob.glob(base+'H9_*')):
    fs=sorted(glob.glob(d+'/r_*.png'))
    if len(fs)>1:
        m=[os.path.getmtime(f) for f in fs]; print(os.path.basename(d),len(fs),round((max(m)-min(m))/(len(fs)-1)*1000,1))
    else: print(os.path.basename(d),len(fs))
