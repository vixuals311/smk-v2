exec(open('D:/SMK/SMKV2/smk-v2/results/q13.py',encoding='utf-8').read())
def E9_run(outfile):
    res={}
    n="E9_relief_quality"; del_tl(n)
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
        d="p14_E9_f%d"%fr; shutil.rmtree(R+d,ignore_errors=True); res["render"]=render_res(d,fr,fr,1920,1080,wait=15)
    # also Size 8 Depth 2 defaults for reference
    for f in fx: f.SetInput("Size",8,0); f.SetInput("Depth",2,0)
    d="p14_E9_default_f40"; shutil.rmtree(R+d,ignore_errors=True); res["render_default"]=render_res(d,40,40,1920,1080,wait=15)
    # Q0 vs Q2 isolated renders (one relief visible at a time) for the mean diff
    for f in fx: f.SetInput("Size",80,0); f.SetInput("Depth",12,0)
    for sz in (16,24,32,48,64):
        for f in fx: f.SetInput("Size",sz,0); f.SetInput("Depth",12,0)
        bg2=comp.FindTool(n+"_Background"); bg2.TopLeftRed=bg2.GetInput("TopLeftRed")+0.001
        d="p14_E9_size%d_f40"%sz; shutil.rmtree(R+d,ignore_errors=True); res["size%d"%sz]=render_res(d,40,40,1920,1080,wait=15)[0]; _json.dump(res,open(outfile,"w"),default=str)
    res["DONE"]=True; _json.dump(res,open(outfile,"w"),default=str)


def run_h1e(kinds, frames=(3,12,60,116)):
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
            d="p14_h1_%s_f%d"%(short,f); rm(d)
            st=render_res(d,f,f,1920,1080,wait=10)
            row.append(st[0])
        out.append(row)
    return out

def e10_thread(kinds,outfile):
    def run():
        out=[]
        for k in kinds:
            try: out+=run_h1e([k])
            except Exception as e: out.append([k,"ERR "+repr(e)[:150]])
            _json.dump(out,open(outfile,"w"),default=str)
        _json.dump(out+[["DONE"]],open(outfile,"w"),default=str)
    th=threading.Thread(target=run,daemon=True); th.start(); return th
