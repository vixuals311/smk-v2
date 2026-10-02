import zipfile,os,sys
src,out=sys.argv[1],sys.argv[2]
z=zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED)
for r,_,fs in os.walk(src):
    for f in fs:
        p=os.path.join(r,f); z.write(p, os.path.relpath(p,src).replace(os.sep,'/'))
z.close(); print(zipfile.ZipFile(out).namelist())
