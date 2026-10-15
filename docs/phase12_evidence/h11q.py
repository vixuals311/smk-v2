exec(open("D:/SMK/SMKV2/smk-v2/results/h15.py").read())
def H11q_run(outfile):
    res={}
    n="H11_Source"
    def step(k,f):
        try: res[k]=f()
        except Exception as e: res[k]="ERR "+repr(e)[:200]
        _json.dump(res,open(outfile,"w"))
    pm=resolve.GetProjectManager()
    def r(d):
        shutil.rmtree(R+d,ignore_errors=True); return render_res(d,40,40,1920,1080,wait=15)
    pj=pm.GetCurrentProject(); old=[pj.GetTimelineByIndex(i) for i in range(1,pj.GetTimelineCount()+1) if pj.GetTimelineByIndex(i).GetName()=="H11_PasteTarget"]
    goto(n)
    if old: pj.GetMediaPool().DeleteTimelines(old)
    names=[n+"_Card",n+"_Look",n+"_StatCard_Renamed",n+"_Text",n+"_LongShadow"]
    # ---- copy/paste into a second comp
    def paste_other():
        t2="H11_PasteTarget"
        comp2,fv2,bg2,put2=setup_res(t2,"H11_PasteTarget - what: tools pasted from H11_Source (Copy/Paste). Look for: same render as the source, no red nodes, expressions intact.",bgc=BG)
        # re-select the source comp
        goto(n); cs=resolve.Fusion().GetCurrentComp()
        cs.CurrentFrame.FlowView.Select()
        tl=[cs.FindTool(x) for x in names]
        cs.Copy(tl)
        goto(t2); c2=resolve.Fusion().GetCurrentComp(); c2.CurrentFrame.FlowView.Select()
        c2.Paste(); time.sleep(1)
        got=sorted(x.Name for x in c2.GetToolList(False).values())
        return got
    step("paste_other_tools",paste_other)
    def connect_and_render():
        c2=resolve.Fusion().GetCurrentComp(); fv2=c2.CurrentFrame.FlowView; t2="H11_PasteTarget"
        tools={x.Name:x for x in c2.GetToolList(False).values()}
        bg2=tools[t2+"_Background"]; prev=bg2.Output; i=0
        order=[n+"_Look",n+"_StatCard_Renamed",n+"_LongShadow"]
        # reconnect: pasted tools keep internal connections; chain them with merges
        outs=[]
        for nm in order:
            tool=tools[nm]; fv2.SetPos(tool,8,i*3); i+=1
        for j,nm in enumerate(order):
            fv2.Select(); m=c2.AddTool("Merge",12,j*3); m.SetAttrs({"TOOLS_Name":"%s_Merge%d"%(t2,j+1)}); fv2.SetPos(m,12,j*3); fv2.Select()
            m.Background.ConnectTo(prev); m.Foreground.ConnectTo(src_out(tools[nm])); prev=m.Output
        mo=c2.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":t2+"_MediaOut"}); fv2.SetPos(mo,16,6); mo.Input.ConnectTo(prev)
        pm.SaveProject()
        return r("p12_h11_paste")
    step("paste_other_render",connect_and_render)
    def dump_inputs(compx,toolname,skip=("Image",)):
        t=compx.FindTool(toolname); return {i.Name:str(t.GetInput(i.ID,0)) for i in t.GetInputList().values() if i.ID not in skip and not i.ID.startswith("Image")}
    def cmp_inputs():
        c2=resolve.Fusion().GetCurrentComp(); a=goto(n); da={nm:dump_inputs(a,nm) for nm in (n+"_Look",n+"_StatCard_Renamed")}
        b=goto("H11_PasteTarget"); db={nm:dump_inputs(b,nm) for nm in (n+"_Look",n+"_StatCard_Renamed")}
        diff={nm:[k for k in da[nm] if da[nm][k]!=db[nm].get(k)] for nm in da}
        return {"n_inputs":{k:len(v) for k,v in da.items()},"differences":diff}
    step("paste_other_inputs",cmp_inputs)
    # ---- duplicate in same comp
    def dup():
        cs=goto(n); cs.CurrentFrame.FlowView.Select()
        before=set(x.Name for x in cs.GetToolList(False).values())
        cs.Copy([cs.FindTool(n+"_StatCard_Renamed"),cs.FindTool(n+"_Look")]); cs.CurrentFrame.FlowView.Select(); cs.Paste(); time.sleep(1)
        new=sorted(set(x.Name for x in cs.GetToolList(False).values())-before)
        return new
    step("duplicate_new_tools",dup)
    def dup_check():
        cs=goto(n); new=[x for x in cs.GetToolList(False).values() if x.Name.startswith(n+"_StatCard_Renamed") and x.Name!=n+"_StatCard_Renamed" or (x.Name.startswith(n+"_Look") and x.Name!=n+"_Look")]
        info={}
        for x in new:
            info[x.Name]={"id":x.ID,"n_inputs":len(x.GetInputList())}
            for oc in ("SMK2_Look",):
                pass
        # compare with originals
        o1=len(cs.FindTool(n+"_StatCard_Renamed").GetInputList()); o2=len(cs.FindTool(n+"_Look").GetInputList())
        info["orig"]={"stat":o1,"look":o2}
        return info
    step("duplicate_info",dup_check)
    pm.SaveProject()
    res["DONE"]=True; _json.dump(res,open(outfile,"w"))
