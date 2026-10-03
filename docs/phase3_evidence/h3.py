import time
MAC="C:/Users/Sonu/AppData/Roaming/Blackmagic Design/DaVinci Resolve/Support/Fusion/Macros/SMK2/%s.setting"
def build(name, note, n=1, kind="SMK2_ProgressRing", bgc=(0.1,0.12,0.2), fps=None):
    pm=resolve.GetProjectManager(); p=pm.GetCurrentProject(); mp=p.GetMediaPool()
    t=mp.CreateEmptyTimeline(name); p.SetCurrentTimeline(t)
    if fps: t.SetSetting("useCustomSettings","1"); t.SetSetting("timelineFrameRate",str(fps))
    it=t.InsertFusionCompositionIntoTimeline(); it.RenameFusionCompByName(it.GetFusionCompNameList()[0], name)
    resolve.OpenPage("fusion"); time.sleep(2)
    comp=resolve.Fusion().GetCurrentComp(); fv=comp.CurrentFrame.FlowView
    def put(tool,nm,x,y): tool.SetAttrs({"TOOLS_Name":nm}); fv.SetPos(tool,x,y); return tool
    nt=put(comp.AddTool("Note",0,-3),name+"_Note",0,-3); nt.Comments=note
    bg=put(comp.AddTool("Background",0,0),name+"_Background",0,0)
    bg.TopLeftRed,bg.TopLeftGreen,bg.TopLeftBlue,bg.TopLeftAlpha=bgc[0],bgc[1],bgc[2],1
    prev=bg.Output; groups=[]; merges=[]
    for i in range(n):
        fv.Select(); before=set(x.Name for x in comp.GetToolList(False).values())
        comp.Execute('comp:Paste(bmd.readfile("%s"))'%(MAC%kind)); time.sleep(1.0)
        g=[x for x in comp.GetToolList(False).values() if x.ID=="GroupOperator" and x.Name not in before][0]
        put(g,"%s_%s%d"%(name,"Ring" if "Ring" in kind else "Bar",i+1),4,i*3-0); fv.Select()
        m=put(comp.AddTool("Merge",8,i*3),"%s_Merge%d"%(name,i+1),8,i*3)
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(list(g.GetOutputList().values())[0])
        prev=m.Output; groups.append(g); merges.append(m)
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":name+"_MediaOut"}); fv.SetPos(mo,12,(n-1)*3); mo.Input.ConnectTo(prev)
    return comp,fv,bg,groups,merges
