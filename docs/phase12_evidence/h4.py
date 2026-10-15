import time
def mk(name, note, fps=None, text="SMK TEXT DEMO", bgc=(0.1,0.12,0.2)):
    pm=resolve.GetProjectManager(); p=pm.GetCurrentProject(); mp=p.GetMediaPool()
    t=mp.CreateEmptyTimeline(name); p.SetCurrentTimeline(t)
    if fps: t.SetSetting("useCustomSettings","1"); t.SetSetting("timelineFrameRate",str(fps))
    it=t.InsertFusionCompositionIntoTimeline(); it.RenameFusionCompByName(it.GetFusionCompNameList()[0], name)
    resolve.OpenPage("fusion"); time.sleep(2)
    comp=resolve.Fusion().GetCurrentComp(); fv=comp.CurrentFrame.FlowView
    if fps: comp.SetPrefs("Comp.FrameFormat.Rate",fps)
    def put(tool,nm,x,y): tool.SetAttrs({"TOOLS_Name":nm}); fv.SetPos(tool,x,y); return tool
    nt=put(comp.AddTool("Note",0,-3),name+"_Note",0,-3); nt.Comments=note
    bg=put(comp.AddTool("Background",0,0),name+"_Background",0,0)
    bg.TopLeftRed,bg.TopLeftGreen,bg.TopLeftBlue,bg.TopLeftAlpha=bgc[0],bgc[1],bgc[2],1
    fv.Select()
    tx=put(comp.AddTool("TextPlus",0,3),name+"_Text",4,3); tx.StyledText=text; tx.Size=0.1; tx.Font="Open Sans"; tx.Style="Bold"
    fv.Select()
    m=put(comp.AddTool("Merge",8,0),name+"_Merge",8,0); m.Background.ConnectTo(bg.Output); m.Foreground.ConnectTo(tx.Output)
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":name+"_MediaOut"}); fv.SetPos(mo,12,0); mo.Input.ConnectTo(m.Output)
    return comp,fv,tx
def render(name_dir, a, b, prefix="r_", wait=8):
    p=resolve.GetProjectManager().GetCurrentProject(); t=p.GetCurrentTimeline(); s=t.GetStartFrame()
    p.SetCurrentRenderFormatAndCodec("PNG","RGB8")
    p.SetRenderSettings({"FormatWidth":1920,"FormatHeight":1080,"SelectAllFrames":False,"MarkIn":s+a,"MarkOut":s+b,"TargetDir":"D:/SMK/SMKV2/smk-v2/results/"+name_dir,"CustomName":prefix})
    jid=p.AddRenderJob(); p.StartRendering(jid); tt=time.time()
    while p.IsRenderingInProgress() and time.time()-tt<wait: time.sleep(0.1)
    return p.GetRenderJobStatus(jid)["JobStatus"], s

def mkrows(name, note, rows, fps=None, bgc=(0.1,0.12,0.2)):
    """rows: list of dict(text, order, dtype, delay, size, y, bind=[ids], motion=dict, mod=dict)"""
    pm=resolve.GetProjectManager(); p=pm.GetCurrentProject(); mp=p.GetMediaPool()
    t=mp.CreateEmptyTimeline(name); p.SetCurrentTimeline(t)
    if fps: t.SetSetting("useCustomSettings","1"); t.SetSetting("timelineFrameRate",str(fps))
    it=t.InsertFusionCompositionIntoTimeline(); it.RenameFusionCompByName(it.GetFusionCompNameList()[0], name)
    resolve.OpenPage("fusion"); time.sleep(2)
    comp=resolve.Fusion().GetCurrentComp(); fv=comp.CurrentFrame.FlowView
    if fps: comp.SetPrefs("Comp.FrameFormat.Rate",fps)
    def put(tool,nm,x,y): tool.SetAttrs({"TOOLS_Name":nm}); fv.SetPos(tool,x,y); return tool
    nt=put(comp.AddTool("Note",0,-3),name+"_Note",0,-3); nt.Comments=note
    bg=put(comp.AddTool("Background",0,0),name+"_Background",0,0)
    bg.TopLeftRed,bg.TopLeftGreen,bg.TopLeftBlue,bg.TopLeftAlpha=bgc[0],bgc[1],bgc[2],1
    prev=bg.Output; out=[]
    for i,r in enumerate(rows):
        fv.Select()
        tx=put(comp.AddTool("TextPlus",0,3*(i+1)),"%s_Text%d"%(name,i+1),4,3*i)
        tx.StyledText=r["text"]; tx.Size=r.get("size",0.05); tx.Font="Open Sans"; tx.Style="Bold"; tx.Center=[0.5,r["y"]]
        fv.Select()
        tx.AddModifier("StyledText","StyledTextFollower"); mod=tx.StyledText.GetConnectedOutput().GetTool()
        mod.Order=r.get("order",1); mod.DelayType=r.get("dtype",1); mod.Delay=r.get("delay",2.4)
        for k,v in r.get("mod",{}).items(): mod.SetInput(k,v,0)
        mos=[]
        for b in r.get("bind",[]):
            mod.AddModifier(b,"Fuse.SMK2_Motion"); m=mod[b].GetConnectedOutput().GetTool()
            for k,v in r.get("motion",{}).items(): m.SetInput(k,v,0)
            mos.append(m)
        mg=put(comp.AddTool("Merge",8,3*i),"%s_Merge%d"%(name,i+1),8,3*i)
        mg.Background.ConnectTo(prev); mg.Foreground.ConnectTo(tx.Output); prev=mg.Output
        out.append((tx,mod,mos))
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":name+"_MediaOut"}); fv.SetPos(mo,12,3*(len(rows)-1)); mo.Input.ConnectTo(prev)
    return comp,fv,bg,out

def bench(nm, tag):
    import os
    p=resolve.GetProjectManager().GetCurrentProject()
    t=[p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==nm][0]
    p.SetCurrentTimeline(t); time.sleep(1); resolve.OpenPage("fusion"); time.sleep(1.5)
    comp=resolve.Fusion().GetCurrentComp(); a=t.GetStartFrame()
    bg=comp.FindTool(nm+"_Background"); v=bg.GetInput("TopLeftRed"); bg.TopLeftRed=v+0.001
    d="D:/SMK/SMKV2/smk-v2/results/s8/e9/%s_%s"%(nm,tag); os.makedirs(d,exist_ok=True)
    p.SetCurrentRenderFormatAndCodec("PNG","RGB8")
    p.SetRenderSettings({"FormatWidth":1920,"FormatHeight":1080,"SelectAllFrames":False,"MarkIn":a,"MarkOut":a+299,"TargetDir":d,"CustomName":"r_"})
    jid=p.AddRenderJob(); t0=time.time(); p.StartRendering(jid); open(d+"_start.txt","w").write(repr(t0)); return d
