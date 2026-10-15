import glob,os,sys
pat=sys.argv[1]
for d in sorted(glob.glob('p8bench/'+pat)):
    fs=sorted(glob.glob(d+'/*.png')); m=[os.path.getmtime(f) for f in fs]
    print(os.path.basename(d),len(fs),round((max(m)-min(m))/(len(fs)-1)*1000,1) if len(fs)>1 else None)
