exec(open("D:/SMK/SMKV2/smk-v2/results/h8.py").read())
def bench13(nm,tag):
    import os
    p=resolve.GetProjectManager().GetCurrentProject()
    t=[p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==nm][0]
    p.SetCurrentTimeline(t); time.sleep(1); resolve.OpenPage("fusion"); time.sleep(1.5)
    comp=resolve.Fusion().GetCurrentComp(); a=t.GetStartFrame()
    bg=comp.FindTool(nm+"_Background"); v=bg.GetInput("TopLeftRed"); bg.TopLeftRed=v+0.001
    d="D:/SMK/SMKV2/smk-v2/results/l13/%s_%s"%(nm,tag); os.makedirs(d,exist_ok=True)
    p.SetCurrentRenderFormatAndCodec("PNG","RGB8")
    p.SetRenderSettings({"FormatWidth":1920,"FormatHeight":1080,"SelectAllFrames":False,"MarkIn":a,"MarkOut":a+299,"TargetDir":d,"CustomName":"r_"})
    jid=p.AddRenderJob(); p.StartRendering(jid); return d
