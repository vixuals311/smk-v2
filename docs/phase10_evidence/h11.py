exec(open("D:/SMK/SMKV2/smk-v2/results/h10.py").read())
import os,glob,shutil,json
def fx_chain(comp,fv,bg,put,n,sources,fuse,names=None):
    prev=bg.Output; out=[]
    for i,s in enumerate(sources):
        fv.Select()
        L=put(comp.AddTool(fuse,8,i*3),"%s_%s%d"%(n,fuse.split("SMK2_")[1],i+1) if not names else names[i],8,i*3); fv.Select()
        L.Image.ConnectTo(src_out(s)); out.append(L)
        m=put(comp.AddTool("Merge",12,i*3),"%s_Merge%d"%(n,i+1),12,i*3); fv.Select()
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(L.Output); prev=m.Output
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,16,(len(sources)-1)*3); mo.Input.ConnectTo(prev)
    return out
def card(comp,fv,put,n,i,cx,cy,w=0.16,h=0.14,col=(1,1,1),name=None,radius=0.1):
    fv.Select(); s=put(comp.AddTool("Fuse.SMK2_Shape",4,i*3),name or "%s_Card%d"%(n,i+1),4,i*3); fv.Select()
    s.SetInput("CX",cx,0); s.SetInput("CY",cy,0); s.SetInput("W",w,0); s.SetInput("H",h,0); s.SetInput("InDur",0,0); s.SetInput("SCA",0,0); s.SetInput("Radius",radius,0)
    s.SetInput("FillAR",col[0],0); s.SetInput("FillAG",col[1],0); s.SetInput("FillAB",col[2],0)
    return s
def goto(nm):
    p=resolve.GetProjectManager().GetCurrentProject()
    t=[p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==nm][0]
    p.SetCurrentTimeline(t); time.sleep(1); resolve.OpenPage("fusion"); time.sleep(2); return resolve.Fusion().GetCurrentComp()
def bench2(nm,tag,w,h,frames=300,maxwait=100):
    p=resolve.GetProjectManager().GetCurrentProject()
    t=[p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==nm][0]
    p.SetCurrentTimeline(t); time.sleep(1); resolve.OpenPage("fusion"); time.sleep(1.5)
    comp=resolve.Fusion().GetCurrentComp(); a=t.GetStartFrame()
    bg=comp.FindTool(nm+"_Background"); bg.TopLeftRed=bg.GetInput("TopLeftRed")+0.001
    d="D:/SMK/SMKV2/smk-v2/results/p8bench/%s_%s"%(nm,tag)
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d,exist_ok=True)
    p.SetCurrentRenderFormatAndCodec("PNG","RGB8")
    p.SetRenderSettings({"FormatWidth":w,"FormatHeight":h,"SelectAllFrames":False,"MarkIn":a,"MarkOut":a+frames-1,"TargetDir":d,"CustomName":"r_"})
    jid=p.AddRenderJob(); p.StartRendering(jid); tt=time.time()
    while p.IsRenderingInProgress() and time.time()-tt<maxwait: time.sleep(0.5)
    fs=sorted(glob.glob(d+"/r_*.png")); m=[os.path.getmtime(f) for f in fs]
    return nm,tag,len(fs),round((max(m)-min(m))/(len(fs)-1)*1000,1) if len(fs)>1 else None
def fp(comp,fuseid):
    return {t.Name:{i.Name:str(t.GetInput(i.ID,0)) for i in t.GetInputList().values() if i.ID!="Image"} for t in comp.GetToolList(False).values() if t.ID==fuseid}
