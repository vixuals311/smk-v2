import time
MAC="C:/Users/Sonu/AppData/Roaming/Blackmagic Design/DaVinci Resolve/Support/Fusion/Macros/SMK2/%s.setting"
def setup(name, note, fps=None, bgc=(0.1,0.12,0.2)):
    pm=resolve.GetProjectManager(); p=pm.GetCurrentProject(); mp=p.GetMediaPool()
    t=mp.CreateEmptyTimeline(name); p.SetCurrentTimeline(t)
    if fps: t.SetSetting("useCustomSettings","1"); t.SetSetting("timelineFrameRate",str(fps))
    it=t.InsertFusionCompositionIntoTimeline(); it.RenameFusionCompByName(it.GetFusionCompNameList()[0], name)
    resolve.OpenPage("fusion"); time.sleep(2)
    comp=resolve.Fusion().GetCurrentComp(); fv=comp.CurrentFrame.FlowView
    if fps: comp.SetPrefs("Comp.FrameFormat.Rate",fps)
    nt=comp.AddTool("Note",0,-3); nt.SetAttrs({"TOOLS_Name":name+"_Note"}); fv.SetPos(nt,0,-3); nt.Comments=note
    bg=comp.AddTool("Background",0,0); bg.SetAttrs({"TOOLS_Name":name+"_Background"}); fv.SetPos(bg,0,0)
    bg.TopLeftRed,bg.TopLeftGreen,bg.TopLeftBlue,bg.TopLeftAlpha=bgc[0],bgc[1],bgc[2],1
    return comp,fv,bg
def add_rows(comp,fv,bg,name,kinds,rowy=3):
    """kinds: list of macro names. returns groups"""
    prev=bg.Output; groups=[]
    for i,k in enumerate(kinds):
        fv.Select(); before=set(x.Name for x in comp.GetToolList(False).values())
        comp.Execute('comp:Paste(bmd.readfile("%s"))'%(MAC%k)); time.sleep(0.8)
        g=[x for x in comp.GetToolList(False).values() if x.ID=="GroupOperator" and x.Name not in before][0]
        g.SetAttrs({"TOOLS_Name":"%s_%s%d"%(name,k.replace("SMK2_",""),i+1)}); fv.SetPos(g,4,i*rowy); fv.Select()
        m=comp.AddTool("Merge",8,i*rowy); m.SetAttrs({"TOOLS_Name":"%s_Merge%d"%(name,i+1)}); fv.SetPos(m,8,i*rowy); fv.Select()
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(list(g.GetOutputList().values())[0]); prev=m.Output; groups.append(g)
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":name+"_MediaOut"}); fv.SetPos(mo,12,(len(kinds)-1)*rowy); mo.Input.ConnectTo(prev)
    return groups
def render(d,a,b,prefix="r_",wait=8):
    p=resolve.GetProjectManager().GetCurrentProject(); t=p.GetCurrentTimeline(); s=t.GetStartFrame()
    p.SetCurrentRenderFormatAndCodec("PNG","RGB8")
    p.SetRenderSettings({"FormatWidth":1920,"FormatHeight":1080,"SelectAllFrames":False,"MarkIn":s+a,"MarkOut":s+b,"TargetDir":"D:/SMK/SMKV2/smk-v2/results/"+d,"CustomName":prefix})
    jid=p.AddRenderJob(); p.StartRendering(jid); tt=time.time()
    while p.IsRenderingInProgress() and time.time()-tt<wait: time.sleep(0.1)
    return p.GetRenderJobStatus(jid)["JobStatus"], s

def bench(nm, tag, frames=300):
    import os
    p=resolve.GetProjectManager().GetCurrentProject()
    t=[p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==nm][0]
    p.SetCurrentTimeline(t); time.sleep(1); resolve.OpenPage("fusion"); time.sleep(1.5)
    comp=resolve.Fusion().GetCurrentComp(); a=t.GetStartFrame()
    bg=comp.FindTool(nm+"_Background"); v=bg.GetInput("TopLeftRed"); bg.TopLeftRed=v+0.001
    d="D:/SMK/SMKV2/smk-v2/results/w14/%s_%s"%(nm,tag); os.makedirs(d,exist_ok=True)
    p.SetCurrentRenderFormatAndCodec("PNG","RGB8")
    p.SetRenderSettings({"FormatWidth":1920,"FormatHeight":1080,"SelectAllFrames":False,"MarkIn":a,"MarkOut":a+frames-1,"TargetDir":d,"CustomName":"r_"})
    jid=p.AddRenderJob(); p.StartRendering(jid); return d
