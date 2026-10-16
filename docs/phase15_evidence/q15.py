exec(open('D:/SMK/SMKV2/smk-v2/results/q14.py',encoding='utf-8').read())
def run_h1r(kinds, frames=(3,12,60,116)):
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
            d="p15_h1_%s_f%d"%(short,f); rm(d)
            st=render_res(d,f,f,1920,1080,wait=10)
            row.append(st[0])
        out.append(row)
    return out

def rc4_thread(kinds,outfile):
    def run():
        out=[]
        for k in kinds:
            try: out+=run_h1r([k])
            except Exception as e: out.append([k,"ERR "+repr(e)[:150]])
            _json.dump(out,open(outfile,"w"),default=str)
        _json.dump(out+[["DONE"]],open(outfile,"w"),default=str)
    th=threading.Thread(target=run,daemon=True); th.start(); return th

def rc4_bypass(outfile):
    """RC4b: for each image Fuse render f60 normally and with the Fuse bypassed (TOOLB_PassThrough) in its H1 comp"""
    res={}
    for k in ["Animator","Look","Relief","Reflection","PageCurl","Bloom","LongShadow"]:
        n="H1_"+k
        try:
            c=goto(n); tool=c.FindTool(n+"_"+k)
            tool.SetAttrs({"TOOLB_PassThrough":True})
            bg=c.FindTool(n+"_Background"); bg.TopLeftRed=bg.GetInput("TopLeftRed")+0.001
            d="p15_h1byp_%s_f60"%k; shutil.rmtree(R+d,ignore_errors=True); res[k]=render_res(d,60,60,1920,1080,wait=12)[0]
            tool.SetAttrs({"TOOLB_PassThrough":False})
        except Exception as e: res[k]="ERR "+repr(e)[:150]
        _json.dump(res,open(outfile,"w"),default=str)
    res["DONE"]=1; _json.dump(res,open(outfile,"w"),default=str)

def RC5_build():
    n="RC5_demo"
    note=("RC5_demo - what: a customer-style 5 s product-launch comp built only from the SMK2 release install: TextLetter title, CardStack list, "
          "StatCard with count-up, two UIBlocks joined by a Connector (travelling pulses) with a Cursor that clicks the second block, Look + Bloom + LongShadow on that block, and a ProgressRing.")
    comp,fv,bg,put=setup_res(n,note,bgc=(0.07,0.08,0.13))
    def noteat(txt,x,y):
        nt=put(comp.AddTool("Note",x,y),"%s_Note_%s"%(n,txt.split()[0]),x,y); nt.Comments=txt; fv.Select(); return nt
    rows=[]   # (source tool, row)
    # row 0: title
    noteat("Title: TextLetter (letters animate in)",4,-1.5)
    t=add_macro(comp,fv,put,n,"SMK2_TextLetter",0,n+"_Title_TextLetter")
    t.SetInput("UIT_Ctrl_Text","Product Launch Dashboard",0); t.SetInput("UIT_Text_Center",[0.5,0.9],0); t.SetInput("UIT_Text_Size",0.07,0)
    # row 1: card stack
    noteat("List: CardStack (4 staggered cards)",4,1.5)
    cs=add_macro(comp,fv,put,n,"SMK2_CardStack",1,n+"_List_CardStack")
    cs.SetInput("UIL_S1_CX",0.15,0); cs.SetInput("UIL_S1_CY",0.7,0); cs.SetInput("UIL_S1_W",0.2,0); cs.SetInput("UIL_S1_H",0.06,0)
    # row 2: stat card
    noteat("KPI: StatCard with count-up",4,4.5)
    sc=add_macro(comp,fv,put,n,"SMK2_StatCard",2,n+"_KPI_StatCard"); sc.SetInput("UIS_Card_CX",0.85,0); sc.SetInput("UIS_Card_CY",0.72,0); sc.SetInput("UIS_Card_W",0.2,0)
    # row 3: block A
    noteat("Flow: block A (UIBlock)",4,7.5)
    ba=add_macro(comp,fv,put,n,"SMK2_UIBlock",3,n+"_Flow_BlockA"); ba.SetInput("Shape_CX",0.42,0); ba.SetInput("Shape_CY",0.45,0); ba.SetInput("Shape_W",0.14,0); ba.SetInput("Shape_H",0.07,0)
    # row 4: block B + effects
    noteat("Flow: block B (UIBlock) then Look glow, Bloom, Long Shadow",4,10.5)
    bb=add_macro(comp,fv,put,n,"SMK2_UIBlock",4,n+"_Flow_BlockB"); bb.SetInput("Shape_CX",0.70,0); bb.SetInput("Shape_CY",0.45,0); bb.SetInput("Shape_W",0.14,0); bb.SetInput("Shape_H",0.07,0)
    fx=[]; prev=bb
    for k,(nm,x) in enumerate((("Look",8),("Bloom",12),("LongShadow",16))):
        fv.Select(); f=put(comp.AddTool("Fuse.SMK2_"+nm,x,12),"%s_Flow_%s"%(n,nm),x,12); fv.Select(); f.Image.ConnectTo(src_out(prev)); prev=f; fx.append(f)
    # row 5: connector
    noteat("Link: Connector A to B (pulses on)",4,13.5)
    fv.Select(); co=put(comp.AddTool("Fuse.SMK2_Connector",4,15),n+"_Link_Connector",4,15); fv.Select()
    co.SetInput("AP",[0.42,0.45],0); co.SetInput("BP",[0.70,0.45],0); co.SetInput("AW",0.14,0); co.SetInput("AH",0.07,0); co.SetInput("BW",0.14,0); co.SetInput("BH",0.07,0); co.SetInput("PulseOn",1,0)
    # row 6: progress ring
    noteat("Status: ProgressRing",4,16.5)
    pr=add_macro(comp,fv,put,n,"SMK2_ProgressRing",6,n+"_Status_ProgressRing"); pr.SetInput("Shape_CX",0.5,0); pr.SetInput("Shape_CY",0.18,0); pr.SetInput("Shape_W",0.08,0)
    # row 7: cursor (top layer)
    noteat("Click: Cursor moves to block B and clicks",4,19.5)
    fv.Select(); cu=put(comp.AddTool("Fuse.SMK2_Cursor",4,21),n+"_Click_Cursor",4,21); fv.Select()
    cu.SetInput("N",2,0); cu.SetInput("P1",[0.2,0.2],0); cu.SetInput("P2",[0.70,0.45],0); cu.SetInput("K2",1,0); cu.SetInput("M2",1.2,0)
    order=[(cs,3),(sc,6),(ba,9),(prev,12),(co,15),(pr,18),(t,0),(cu,21)]   # bottom -> top; merges x=24, y = source row
    prevo=bg.Output
    for i,(s,y) in enumerate(order):
        fv.Select(); m=put(comp.AddTool("Merge",24,y),"%s_Merge%d"%(n,i+1),24,y); fv.Select()
        m.Background.ConnectTo(prevo); m.Foreground.ConnectTo(src_out(s)); prevo=m.Output
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,28,21); mo.Input.ConnectTo(prevo)
    resolve.GetProjectManager().SaveProject()
    return n
def RC5_run(outfile):
    res={}
    try: res["built"]=RC5_build()
    except Exception as e:
        import traceback; res["build_err"]=traceback.format_exc()[-600:]; _json.dump(res,open(outfile,"w"),default=str); return
    _json.dump(res,open(outfile,"w"),default=str)
    n="RC5_demo"; pj=resolve.GetProjectManager().GetCurrentProject()
    d=bench2(n,"png",1920,1080,frames=120,maxwait=120); res["png_bench"]=d; _json.dump(res,open(outfile,"w"),default=str)
    d2=bench2(n,"png2",1920,1080,frames=120,maxwait=120); res["png_bench2"]=d2; _json.dump(res,open(outfile,"w"),default=str)
    tl=pj.GetCurrentTimeline(); a=tl.GetStartFrame()
    od=R+"p15_rc5_mp4"; shutil.rmtree(od,ignore_errors=True); os.makedirs(od,exist_ok=True)
    res["fmt"]=str(pj.SetCurrentRenderFormatAndCodec("mp4","H264"))
    pj.SetRenderSettings({"FormatWidth":1920,"FormatHeight":1080,"SelectAllFrames":False,"MarkIn":a,"MarkOut":a+119,"TargetDir":od,"CustomName":"rc5_demo"})
    jid=pj.AddRenderJob(); t0=time.time(); pj.StartRendering(jid)
    while pj.IsRenderingInProgress() and time.time()-t0<120: time.sleep(0.5)
    res["mp4_status"]=pj.GetRenderJobStatus(jid); res["mp4_files"]=os.listdir(od); _json.dump(res,open(outfile,"w"),default=str)
    resolve.GetProjectManager().SaveProject(); res["DONE"]=1; _json.dump(res,open(outfile,"w"),default=str)
