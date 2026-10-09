import glob,sys
from PIL import Image
def run(bright,dark,regions,label):
    b=Image.open(glob.glob(bright+'/*.png')[0]).convert('RGB').load(); d=Image.open(glob.glob(dark+'/*.png')[0]).convert('RGB').load()
    Bb,Bd=0.9*255,0.1*255
    for nm,(x0,y0,x1,y1) in regions:
        neg=over=inc=n=0; mn=999; mx=-999
        for y in range(y0,y1):
            for x in range(x0,x1):
                cb,cd=b[x,y],d[x,y]; al=[1-(cb[c]-cd[c])/(Bb-Bd) for c in range(3)]
                if max(al)-min(al)>0.02: inc+=1
                a=sum(al)/3
                for c in range(3):
                    f=cd[c]-(1-a)*Bd; mn=min(mn,f)
                    if f<-2.5: neg+=1
                    if f>a*255+2.5: over+=1; mx=max(mx,f-a*255)
                n+=1
        print("%s %-14s px %d: alpha-inconsistent %d, fg<0 %d (min %.1f), fg>alpha %d (max excess %.1f)"%(label,nm,n,inc,neg,mn,over,mx))
if __name__=="__main__":
    run('p8_r6_bright','p8_r6_dark',[("default",(100,150,860,930)),("size30 depth4",(1000,150,1800,930))],"R6")
