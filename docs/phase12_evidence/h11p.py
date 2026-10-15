exec(open("D:/SMK/SMKV2/smk-v2/results/h15.py").read())
def H11_run(outfile):
    res={}
    def step(k,f):
        try: res[k]=f()
        except Exception as e: res[k]="ERR "+repr(e)[:200]
        _json.dump(res,open(outfile,"w"))
    pm=resolve.GetProjectManager()
    n="H11_Source"
    comp,fv,bg,put=setup_res(n,"H11_Source - what: Shape card -> Look (glow) , StatCard macro, Text+ -> LongShadow, merged over a background; source for copy/paste/duplicate/rename/undo/save-as checks. Look for: identical renders after each operation.",bgc=BG)
    c=card(comp,fv,put,n,0,0.25,0.7,w=0.2,h=0.14,col=(0.9,0.5,0.2),name=n+"_Card")
    fv.Select(); lk=put(comp.AddTool("Fuse.SMK2_Look",8,0),n+"_Look",8,0); fv.Select(); lk.Image.ConnectTo(src_out(c)); lk.SetInput("GlowR",60,0) if False else None
    g=add_macro(comp,fv,put,n,"SMK2_StatCard",1,n+"_StatCard"); g.SetInput("UIS_Card_CX",0.7,0); g.SetInput("UIS_Card_CY",0.65,0); g.SetInput("UIS_Card_W",0.22,0)
    t=add_text(comp,fv,put,n,2,"COPY",0.3,0.25,0.12,name=n+"_Text")
    fv.Select(); ls=put(comp.AddTool("Fuse.SMK2_LongShadow",8,6),n+"_LongShadow",8,6); fv.Select(); ls.Image.ConnectTo(src_out(t))
    end_chain(comp,fv,put,n,bg,[lk,g,ls])
    pm.SaveProject()
    def r(d,comp_name=None):
        shutil.rmtree(R+d,ignore_errors=True); return render_res(d,40,40,1920,1080,wait=15)
    step("src_render",lambda: r("p12_h11_src"))
    names=[n+"_Card",n+"_Look",n+"_StatCard",n+"_Text",n+"_LongShadow"]
    step("src_inputs",lambda: {"look":len(lk.GetInputList()),"stat":len(g.GetInputList())})
    # ---- copy/paste into a second comp
    def paste_other():
        t2="H11_PasteTarget"
        comp2,fv2,bg2,put2=setup_res(t2,"H11_PasteTarget - what: tools pasted from H11_Source (Copy/Paste). Look for: same render as the source, no red nodes, expressions intact.",bgc=BG)
        # re-select the source comp
        goto(n); cs=resolve.Fusion().GetCurrentComp()
        cs.FlowView.Select()
        tl=[cs.FindTool(x) for x in names]
        cs.Copy(tl)
        goto(t2); c2=resolve.Fusion().GetCurrentComp(); c2.FlowView.Select()
        c2.Paste(); time.sleep(1)
        got=sorted(x.Name for x in c2.GetToolList(False).values())
        return got
    step("paste_other_tools",paste_other)
    def connect_and_render():
        c2=resolve.Fusion().GetCurrentComp(); fv2=c2.CurrentFrame.FlowView; t2="H11_PasteTarget"
        tools={x.Name:x for x in c2.GetToolList(False).values()}
        bg2=tools[t2+"_Background"]; prev=bg2.Output; i=0
        order=[n+"_Look",n+"_StatCard",n+"_LongShadow"]
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
        c2=resolve.Fusion().GetCurrentComp(); a=goto(n); da={nm:dump_inputs(a,nm) for nm in (n+"_Look",n+"_StatCard")}
        b=goto("H11_PasteTarget"); db={nm:dump_inputs(b,nm) for nm in (n+"_Look",n+"_StatCard")}
        diff={nm:[k for k in da[nm] if da[nm][k]!=db[nm].get(k)] for nm in da}
        return {"n_inputs":{k:len(v) for k,v in da.items()},"differences":diff}
    step("paste_other_inputs",cmp_inputs)
    # ---- duplicate in same comp
    def dup():
        cs=goto(n); cs.FlowView.Select()
        before=set(x.Name for x in cs.GetToolList(False).values())
        cs.Copy([cs.FindTool(n+"_StatCard"),cs.FindTool(n+"_Look")]); cs.FlowView.Select(); cs.Paste(); time.sleep(1)
        new=sorted(set(x.Name for x in cs.GetToolList(False).values())-before)
        return new
    step("duplicate_new_tools",dup)
    def dup_check():
        cs=goto(n); new=[x for x in cs.GetToolList(False).values() if x.Name.startswith(n+"_StatCard") and x.Name!=n+"_StatCard" or (x.Name.startswith(n+"_Look") and x.Name!=n+"_Look")]
        info={}
        for x in new:
            info[x.Name]={"id":x.ID,"n_inputs":len(x.GetInputList())}
            for oc in ("SMK2_Look",):
                pass
        # compare with originals
        o1=len(cs.FindTool(n+"_StatCard").GetInputList()); o2=len(cs.FindTool(n+"_Look").GetInputList())
        info["orig"]={"stat":o1,"look":o2}
        return info
    step("duplicate_info",dup_check)
    # ---- rename the macro (group) and re-render
    def rename():
        cs=goto(n); g=cs.FindTool(n+"_StatCard"); g.SetAttrs({"TOOLS_Name":n+"_StatCard_Renamed"}); time.sleep(0.5)
        ok=cs.FindTool(n+"_StatCard_Renamed") is not None
        # remove the duplicates so the render comparison is fair
        for x in list(cs.GetToolList(False).values()):
            if x.Name.startswith(n+"_StatCard1") or x.Name.startswith(n+"_Look1") or (x.Name.endswith("1") and x.Name.startswith(n+"_Look")) : x.Delete()
        return {"renamed_found":ok,"render":r("p12_h11_renamed")}
    step("rename",rename)
    # ---- undo / redo
    def undo():
        cs=goto(n); lk=cs.FindTool(n+"_Look"); ids=[i.ID for i in lk.GetInputList().values()]
        glow=[k for k in ids if "Glow" in k][:3]
        k=glow[0]; v0=lk.GetInput(k,0)
        out={"input":k,"before":v0}
        cs.StartUndo("h11 change"); lk.SetInput(k,(v0 or 0)+37 if isinstance(v0,(int,float)) else v0,0); cs.EndUndo(True)
        out["changed"]=lk.GetInput(k,0)
        cs.Undo(); time.sleep(0.5); out["after_undo"]=cs.FindTool(n+"_Look").GetInput(k,0)
        cs.Redo(); time.sleep(0.5); out["after_redo"]=cs.FindTool(n+"_Look").GetInput(k,0)
        cs.Undo(); time.sleep(0.5); out["after_undo2"]=cs.FindTool(n+"_Look").GetInput(k,0)
        # undo of delete
        cs.StartUndo("h11 delete"); tx=cs.FindTool(n+"_Text"); tx.Delete(); cs.EndUndo(True)
        out["deleted"]=cs.FindTool(n+"_Text") is None
        cs.Undo(); time.sleep(0.5); out["restored"]=cs.FindTool(n+"_Text") is not None
        out["render_after_undo"]=r("p12_h11_undo")
        return out
    step("undo",undo)
    pm.SaveProject()
    # ---- save as a different project (export / import under another name)
    def saveas():
        pr=pm.GetCurrentProject(); nm=pr.GetName(); path="D:/SMK/SMKV2/smk-v2/results/h11_phase12.drp"
        if os.path.exists(path): os.remove(path)
        ok1=pm.ExportProject(nm,path)
        ok2=pm.ImportProject(path,"SMK Phase12 Copy")
        ok3=pm.LoadProject("SMK Phase12 Copy")
        pj=pm.GetCurrentProject(); out={"export":ok1,"import":ok2,"load":bool(ok3),"project":pj.GetName() if pj else None}
        c=goto(n); out["tools"]=len(c.GetToolList(False)); out["look_inputs"]=len(c.FindTool(n+"_Look").GetInputList())
        out["render"]=r("p12_h11_copyproj")
        pm.SaveProject(); pm.LoadProject(nm); out["back"]=pm.GetCurrentProject().GetName()
        return out
    step("save_as",saveas)
    res["DONE"]=True; _json.dump(res,open(outfile,"w"))
