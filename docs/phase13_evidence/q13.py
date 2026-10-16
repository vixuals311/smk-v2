exec(open("D:/SMK/SMKV2/smk-v2/results/h15.py").read())
import json as _json, threading, time, os, shutil
R="D:/SMK/SMKV2/smk-v2/results/"
def mpool():
    pj=resolve.GetProjectManager().GetCurrentProject(); return pj, pj.GetMediaPool()
def find_clip(prefix):
    pj,mp=mpool(); return [x for x in mp.GetRootFolder().GetClipList() if x.GetName().startswith(prefix)][0]
def del_tl(name):
    pj,mp=mpool(); ts=[pj.GetTimelineByIndex(i) for i in range(1,pj.GetTimelineCount()+1) if pj.GetTimelineByIndex(i).GetName()==name]
    if ts:
        keep=[pj.GetTimelineByIndex(i) for i in range(1,pj.GetTimelineCount()+1) if pj.GetTimelineByIndex(i).GetName()!=name]
        if keep: pj.SetCurrentTimeline(keep[0])
        mp.DeleteTimelines(ts)
def clip_comp(name, clip, mark, note, fps=None):
    """timeline with one clip (mark=(in,out) or None), comp on the clip; returns comp,fv,mi,put"""
    pj,mp=mpool(); del_tl(name)
    clip.ClearMarkInOut("all") if hasattr(clip,"ClearMarkInOut") else None
    if mark: clip.SetMarkInOut(mark[0],mark[1],"all")
    tl=mp.CreateEmptyTimeline(name); pj.SetCurrentTimeline(tl)
    if globals().get('QSTART_TC'): print('setstart',tl.SetStartTimecode(globals()['QSTART_TC']))
    mp.AppendToTimeline([clip]); it=tl.GetItemListInTrack("video",1)[0]
    it.AddFusionComp(); resolve.OpenPage("fusion"); time.sleep(3)
    comp=resolve.Fusion().GetCurrentComp(); fv=comp.CurrentFrame.FlowView
    def put(tool,nm,x,y): tool.SetAttrs({"TOOLS_Name":nm}); fv.SetPos(tool,x,y); return tool
    nt=put(comp.AddTool("Note",0,-3),name+"_Note",0,-3); nt.Comments=note
    mi=comp.FindTool("MediaIn1"); mi.SetAttrs({"TOOLS_Name":name+"_MediaIn"}); fv.SetPos(mi,0,0)
    fv.Select(); bg=put(comp.AddTool("Background",0,3),name+"_Background",0,3); bg.TopLeftRed,bg.TopLeftGreen,bg.TopLeftBlue,bg.TopLeftAlpha=0.2,0.2,0.25,1; fv.Select()
    mb=put(comp.AddTool("Merge",2,1),name+"_MergeBase",2,1); fv.Select(); mb.Background.ConnectTo(bg.Output); mb.Foreground.ConnectTo(mi.Output)
    return comp,fv,mb,put,it
def chain_products(comp,fv,put,n,mi,kinds):
    prev=mi.Output; tools=[]  # mi = base merge
    for i,k in enumerate(kinds):
        nm="%s_%s"%(n,k.replace("SMK2_","").replace("Fuse.",""))
        if k.startswith("SMK2_"): g=add_macro(comp,fv,put,n,k,i,nm)
        else: fv.Select(); g=put(comp.AddTool(k,4,i*3),nm,4,i*3); fv.Select()
        m=put(comp.AddTool("Merge",8,i*3),"%s_Merge%d"%(n,i+1),8,i*3); fv.Select()
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(src_out(g)); prev=m.Output; tools.append(g)
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,12,(len(kinds)-1)*3); mo.Input.ConnectTo(prev)
    return tools
def add_probes(comp,fv,put,n,row0):
    """Text+ showing comp.RenderStart/End/GlobalStart/End and a Motion-modifier probe (value drops to 0 at the clip end a Fuse computes)"""
    fv.Select(); t=put(comp.AddTool("TextPlus",16,row0*3),n+"_RangeText",16,row0*3); fv.Select()
    t.StyledText="x"; t.Size=0.05; t.Center=[0.5,0.05]
    try:
        t.StyledText.SetExpression('string.format("RS=%s RE=%s GS=%s GE=%s", tostring(comp.RenderStart), tostring(comp.RenderEnd), tostring(comp.GlobalStart), tostring(comp.GlobalEnd))')
    except Exception as e: print("expr err",e)
    fv.Select(); b=put(comp.AddTool("Background",16,row0*3+3),n+"_MotionProbe",16,row0*3+3); fv.Select()
    b.TopLeftRed.AddModifier if False else None
    b.AddModifier("TopLeftRed","Fuse.SMK2_Motion")
    return t,b
def probe_values(comp,b,t,frames):
    out={"text":None,"motion":{}}
    try: out["text"]=t.GetInput("StyledText",0)
    except Exception as e: out["text"]="ERR "+str(e)
    for f in frames:
        try: out["motion"][f]=b.GetInput("TopLeftRed",f)
        except Exception as e: out["motion"][f]="ERR"
    return out
Q1KINDS=["SMK2_StatCard","Fuse.SMK2_Shape","SMK2_TextLetter","SMK2_CardStack","Fuse.SMK2_Connector","Fuse.SMK2_Cursor","SMK2_ProgressRing"]
def Q_run(name,clipname,mark,kinds,frames,outfile,note,extra=None):
    res={}
    def step(k,f):
        try: res[k]=f()
        except Exception as e: res[k]="ERR "+repr(e)[:250]
        _json.dump(res,open(outfile,"w"),default=str)
    clip=find_clip(clipname)
    comp,fv,mb,put,it=clip_comp(name,clip,mark,note)
    tools=chain_products(comp,fv,put,name,mb.Output and mb,kinds) if False else None
    mo=None
    # chain from base merge output
    prev=mb.Output; ts=[]
    for i,k in enumerate(kinds):
        nm="%s_%s"%(name,k.replace("SMK2_","").replace("Fuse.",""))
        if k.startswith("SMK2_"): g=add_macro(comp,fv,put,name,k,i+1,nm)
        else: fv.Select(); g=put(comp.AddTool(k,4,(i+1)*3),nm,4,(i+1)*3); fv.Select()
        m=put(comp.AddTool("Merge",8,(i+1)*3),"%s_Merge%d"%(name,i+1),8,(i+1)*3); fv.Select()
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(src_out(g)); prev=m.Output; ts.append(g)
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":name+"_MediaOut"}); fv.SetPos(mo,12,(len(kinds))*3); mo.Input.ConnectTo(prev)
    t,b=add_probes(comp,fv,put,name,1)
    resolve.GetProjectManager().SaveProject()
    pj=resolve.GetProjectManager().GetCurrentProject()
    step("item",lambda:{"name":it.GetName(),"start":it.GetStart(),"end":it.GetEnd(),"dur":it.GetDuration()})
    step("attrs",lambda:{k:v for k,v in comp.GetAttrs().items() if "Start" in k or "End" in k})
    step("probe",lambda: probe_values(comp,b,t,list(range(0,24))+list(range(24,130,6))))
    bgn=comp.FindTool(name+"_Background"); bgn.TopLeftRed=bgn.GetInput("TopLeftRed")+0.001
    for f in frames:
        d="p13_%s_f%d"%(name,f); shutil.rmtree(R+d,ignore_errors=True)
        step("render_f%d"%f,lambda: render_res(d,f,f,1920,1080,wait=15))
    res["DONE"]=True; _json.dump(res,open(outfile,"w"),default=str)
def Q3_run(name,clipname,mark,outfile,note,frames=(0,5,10,30,60,79),pre=None):
    res={}
    def step(k,f):
        try: res[k]=f()
        except Exception as e: res[k]="ERR "+repr(e)[:250]
        _json.dump(res,open(outfile,"w"),default=str)
    clip=find_clip(clipname)
    comp,fv,mb,put,it=clip_comp(name,clip,mark,note)
    kinds=["Fuse.SMK2_Shape","SMK2_StatCard"]
    prev=mb.Output; ts=[]
    for i,k in enumerate(kinds):
        nm="%s_%s"%(name,k.replace("SMK2_","").replace("Fuse.",""))
        if k.startswith("SMK2_"): g=add_macro(comp,fv,put,name,k,i+1,nm)
        else: fv.Select(); g=put(comp.AddTool(k,4,(i+1)*3),nm,4,(i+1)*3); fv.Select()
        m=put(comp.AddTool("Merge",8,(i+1)*3),"%s_Merge%d"%(name,i+1),8,(i+1)*3); fv.Select()
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(src_out(g)); prev=m.Output; ts.append(g)
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":name+"_MediaOut"}); fv.SetPos(mo,12,len(kinds)*3+3); mo.Input.ConnectTo(prev)
    t,b=add_probes(comp,fv,put,name,3)
    mb.Blend=0   # MediaIn hidden: the Background (red driven by the Motion probe) is the base, so pixel (5,5) red = Motion value at the rendered time
    bg=comp.FindTool(name+"_Background"); bg.AddModifier("TopLeftRed","Fuse.SMK2_Motion")
    if pre: pre(comp)
    resolve.GetProjectManager().SaveProject()
    step("item",lambda:{"name":it.GetName(),"start":it.GetStart(),"end":it.GetEnd(),"dur":it.GetDuration(),"left":it.GetLeftOffset(),"right":it.GetRightOffset()})
    step("attrs",lambda:{k:v for k,v in comp.GetAttrs().items() if "Start" in k or "End" in k})
    step("probe_text",lambda: t.GetInput("StyledText",0))
    def rr(tag):
        for f in frames:
            d="p13_%s_%s_f%d"%(name,tag,f); shutil.rmtree(R+d,ignore_errors=True)
            res["render_%s_f%d"%(tag,f)]=render_res(d,f,f,1920,1080,wait=15)[0]; _json.dump(res,open(outfile,"w"),default=str)
    rr("default")
    sh=comp.FindTool(name+"_Shape")
    step("shape_clip_len_inputs",lambda:[ (i.ID,i.Name) for i in sh.GetInputList().values() if "Clip" in i.Name or "Clip" in i.ID])
    sh.SetInput("ClipLen",2.0,0)
    rr("shape_cliplen2")
    res["DONE"]=True; _json.dump(res,open(outfile,"w"),default=str)
def Q4_run(outfile):
    res={}
    def step(k,f):
        try: res[k]=f()
        except Exception as e: res[k]="ERR "+repr(e)[:250]
        _json.dump(res,open(outfile,"w"),default=str)
    pm=resolve.GetProjectManager()
    def late(comp,start,n=120):
        comp.SetAttrs({"COMPN_GlobalStart":start,"COMPN_GlobalEnd":start+n-1,"COMPN_RenderStart":start,"COMPN_RenderEnd":start+n-1})
        a=comp.GetAttrs(); return {k:a[k] for k in a if "Start" in k or "End" in k}
    for tag,start in (("0",0),("90000",90000)):
        n="Q4_textplus_%s"%tag
        del_tl(n)
        comp,fv,bg,put=setup_res(n,"%s - what: Text+ only over a Background, comp Global/Render range set to start at %s by SetAttrs. Checks whether the HOST itself renders a late start."%(n,tag),bgc=BG)
        t=add_text(comp,fv,put,n,0,"HOST",0.5,0.5,0.15,name=n+"_TextPlus")
        m=put(comp.AddTool("Merge",8,0),n+"_Merge1",8,0); fv.Select(); m.Background.ConnectTo(bg.Output); m.Foreground.ConnectTo(src_out(t))
        mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,12,0); mo.Input.ConnectTo(m.Output)
        step(n+"_attrs",lambda: late(comp,start))
        pm.SaveProject()
        for f in (5,30,60,100):
            d="p13_%s_f%d"%(n,f); shutil.rmtree(R+d,ignore_errors=True)
            res["%s_f%d"%(n,f)]=render_res(d,f,f,1920,1080,wait=15); _json.dump(res,open(outfile,"w"),default=str)
    for tag,start in (("0",0),("90000",90000)):
        n="Q4_smk_%s"%tag
        del_tl(n)
        comp,fv,bg,put=setup_res(n,"%s - what: Shape, Animator (fed by a Text+) and TextLetter macro, comp range start %s by SetAttrs."%(n,tag),bgc=BG)
        s1=card(comp,fv,put,n,0,0.25,0.7,w=0.2,h=0.14,col=(0.9,0.5,0.2),name=n+"_Shape"); s1.SetInput("InDur",0.3,0)
        t=add_text(comp,fv,put,n,1,"ANIM",0.7,0.7,0.1,name=n+"_TextPlus")
        fv.Select(); an=put(comp.AddTool("Fuse.SMK2_Animator",8,3),n+"_Animator",8,3); fv.Select(); an.Image.ConnectTo(src_out(t))
        g=add_macro(comp,fv,put,n,"SMK2_TextLetter",2,n+"_TextLetter"); g.SetInput("UIT_Text_Center",[0.5,0.3],0)
        end_chain(comp,fv,put,n,bg,[s1,an,g])
        step(n+"_attrs",lambda: late(comp,start))
        pm.SaveProject()
        for f in (5,30,60,100):
            d="p13_%s_f%d"%(n,f); shutil.rmtree(R+d,ignore_errors=True)
            res["%s_f%d"%(n,f)]=render_res(d,f,f,1920,1080,wait=15); _json.dump(res,open(outfile,"w"),default=str)
    res["DONE"]=True; _json.dump(res,open(outfile,"w"),default=str)
def Q7_run(outfile):
    res={}
    n="Q7_relief_quality"; del_tl(n)
    comp,fv,bg,put=setup_res(n,"%s - what: Relief Size 80 / Depth 12 on a Shape ring at Quality 0 (Draft), 1 (Normal), 2 (High), three side-by-side rows. Look for blocks / tiling."%n,bgc=BG)
    srcs=[]
    for i,cx in enumerate((0.2,0.5,0.8)):
        s=card(comp,fv,put,n,i,cx,0.5,w=0.2,h=0.2,col=(0.85,0.85,0.9),name="%s_Ring_Q%d"%(n,i)); s.SetInput("Shape",2,0); s.SetInput("Thick",24,0); s.SetInput("SCA",0,0)
        srcs.append(s)
    fx=fx_chain(comp,fv,bg,put,n,srcs,"Fuse.SMK2_Relief",names=["%s_Relief_Q%d"%(n,i) for i in range(3)])
    for i,f in enumerate(fx):
        f.SetInput("Size",80,0); f.SetInput("Depth",12,0); f.SetInput("Quality",i,0)
    resolve.GetProjectManager().SaveProject()
    for fr in (40,):
        d="p13_Q7_f%d"%fr; shutil.rmtree(R+d,ignore_errors=True); res["render"]=render_res(d,fr,fr,1920,1080,wait=15)
    # also Size 8 Depth 2 defaults for reference
    for f in fx: f.SetInput("Size",8,0); f.SetInput("Depth",2,0)
    d="p13_Q7_default_f40"; shutil.rmtree(R+d,ignore_errors=True); res["render_default"]=render_res(d,40,40,1920,1080,wait=15)
    # Q0 vs Q2 isolated renders (one relief visible at a time) for the mean diff
    for f in fx: f.SetInput("Size",80,0); f.SetInput("Depth",12,0)
    res["DONE"]=True; _json.dump(res,open(outfile,"w"),default=str)

def run_h1q(kinds, frames=(3,12,60,116)):
    pm=resolve.GetProjectManager(); out=[]
    for kind in kinds:
        short=kind[5:] if kind.startswith("SMK2_") else kind
        n="H1_"+short
        if kind=="Motion" or kind=="MotionRig":
            comp,fv,bg,put=setup_res(n,"%s - what: Text+ with the SMK2 %s modifier on %s, defaults, over a plain background. Look for: no error; image not empty at the four frames."%(n,kind,"Size" if kind=="Motion" else "the Merge Blend"),bgc=BG)
            t=text_src(comp,fv,put,n,0)
            mrg=put(comp.AddTool("Merge",12,0),n+"_Merge1",12,0); fv.Select(); mrg.Background.ConnectTo(bg.Output); mrg.Foreground.ConnectTo(src_out(t))
            mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,16,0); mo.Input.ConnectTo(mrg.Output)
            fv.Select()
            if kind=="Motion": t.AddModifier("Size","Fuse.SMK2_Motion"); t.SetInput("Size",0.12,0) if False else None
            else: mrg.AddModifier("Blend","Fuse.SMK2_MotionRig")
        else:
            comp,tools=build_product(n,kind,"%s - what: %s with defaults over a plain background (image Fuses are fed by a Text+). Look for: no error, non-empty output at the four frames."%(n,kind))
        pm.SaveProject()
        c=goto(n); c.FindTool(n+"_Background").TopLeftRed=0.2
        row=[kind]
        for f in frames:
            d="p13_h1_%s_f%d"%(short,f); rm(d)
            st=render_res(d,f,f,1920,1080,wait=10)
            row.append(st[0])
        out.append(row)
    return out

def q8_thread(kinds,outfile):
    def run():
        out=[]
        for k in kinds:
            try: out+=run_h1q([k])
            except Exception as e: out.append([k,"ERR "+repr(e)[:150]])
            _json.dump(out,open(outfile,"w"),default=str)
        _json.dump(out+[["DONE"]],open(outfile,"w"),default=str)
    th=threading.Thread(target=run,daemon=True); th.start(); return th
