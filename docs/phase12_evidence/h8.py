exec(open("D:/SMK/SMKV2/smk-v2/results/h7.py").read())
def setup_res(name, note, w=1920, h=1080, fps=None, bgc=(0.5,0.5,0.5)):
    pm=resolve.GetProjectManager(); p=pm.GetCurrentProject(); mp=p.GetMediaPool()
    t=mp.CreateEmptyTimeline(name); p.SetCurrentTimeline(t)
    if fps or w!=1920 or h!=1080:
        t.SetSetting("useCustomSettings","1")
        if fps: t.SetSetting("timelineFrameRate",str(fps))
        if (w,h)!=(1920,1080): t.SetSetting("timelineResolutionWidth",str(w)); t.SetSetting("timelineResolutionHeight",str(h))
    it=t.InsertFusionCompositionIntoTimeline(); it.RenameFusionCompByName(it.GetFusionCompNameList()[0], name)
    resolve.OpenPage("fusion"); time.sleep(2)
    comp=resolve.Fusion().GetCurrentComp(); fv=comp.CurrentFrame.FlowView
    if fps: comp.SetPrefs("Comp.FrameFormat.Rate",fps)
    if (w,h)!=(1920,1080): comp.SetPrefs("Comp.FrameFormat.Width",w); comp.SetPrefs("Comp.FrameFormat.Height",h)
    def put(tool,nm,x,y): tool.SetAttrs({"TOOLS_Name":nm}); fv.SetPos(tool,x,y); return tool
    nt=put(comp.AddTool("Note",0,-3),name+"_Note",0,-3); nt.Comments=note
    bg=put(comp.AddTool("Background",0,0),name+"_Background",0,0)
    bg.TopLeftRed,bg.TopLeftGreen,bg.TopLeftBlue,bg.TopLeftAlpha=bgc[0],bgc[1],bgc[2],1
    return comp,fv,bg,put
def add_cursor(comp,fv,bg,put,name,row=0,suffix=""):
    fv.Select()
    c=put(comp.AddTool("Fuse.SMK2_Cursor",4,row*3),"%s_Cursor%s"%(name,suffix),4,row*3); fv.Select()
    return c
def finish(comp,fv,bg,put,name,cursors):
    prev=bg.Output
    for i,c in enumerate(cursors):
        m=put(comp.AddTool("Merge",8,i*3),"%s_Merge%d"%(name,i+1),8,i*3); fv.Select()
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(c.Output); prev=m.Output
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":name+"_MediaOut"}); fv.SetPos(mo,12,(len(cursors)-1)*3); mo.Input.ConnectTo(prev)
def render_res(d,a,b,w,h,prefix="r_",wait=8):
    p=resolve.GetProjectManager().GetCurrentProject(); t=p.GetCurrentTimeline(); s=t.GetStartFrame()
    p.SetCurrentRenderFormatAndCodec("PNG","RGB8")
    p.SetRenderSettings({"FormatWidth":w,"FormatHeight":h,"SelectAllFrames":False,"MarkIn":s+a,"MarkOut":s+b,"TargetDir":"D:/SMK/SMKV2/smk-v2/results/"+d,"CustomName":prefix})
    jid=p.AddRenderJob(); p.StartRendering(jid); tt=time.time()
    while p.IsRenderingInProgress() and time.time()-tt<wait: time.sleep(0.1)
    return p.GetRenderJobStatus(jid)["JobStatus"], s
