exec(open("D:/SMK/SMKV2/smk-v2/results/h14.py").read())
import threading, json as _json
def build_inst(n,kind,count,note,w=1920,h=1080,fps=60):
    comp,fv,bg,put=setup_res(n,note,w=w,h=h,fps=fps,bgc=BG)
    outs=[]
    cols=min(count,5)
    for i in range(count):
        cx=0.1+0.8*((i%cols)/max(cols-1,1)); cy=0.85-0.7*((i//cols)/max((count-1)//cols,1)) if count>cols else 0.5
        nm="%s_%s%02d"%(n,kind.replace("SMK2_",""),i+1)
        if kind.startswith("SMK2_"):
            g=add_macro(comp,fv,put,n,kind,i,nm)
            try:
                if kind=="SMK2_TextLetter": g.SetInput("UIT_Ctrl_Text","ABCDEFGHIJKL",0); g.SetInput("UIT_Text_Center",[cx,cy],0); g.SetInput("UIT_Text_Size",0.05,0)
                elif kind=="SMK2_UIBlock": g.SetInput("Shape_CX",cx,0); g.SetInput("Shape_CY",cy,0); g.SetInput("Shape_W",0.12,0); g.SetInput("Shape_H",0.06,0) if False else None
                elif kind=="SMK2_StatCard": g.SetInput("UIS_Card_CX",cx,0); g.SetInput("UIS_Card_CY",cy,0); g.SetInput("UIS_Card_W",0.15,0)
                elif kind=="SMK2_CardStack": g.SetInput("UIL_S1_CX",cx,0); g.SetInput("UIL_S1_CY",cy,0); g.SetInput("UIL_S1_W",0.15,0); g.SetInput("UIL_S1_H",0.03,0)
            except Exception as e: pass
            outs.append(g)
        else:
            if n.startswith("H9S_"): t=card(comp,fv,put,n,i,cx,cy,w=0.09 if count>1 else 0.2,h=0.09 if count>1 else 0.2,col=(0.9,0.9,0.95),name="%s_Card%02d"%(n,i+1))
            else: t=add_text(comp,fv,put,n,i,"SMK",cx,cy,0.06,name="%s_Text%02d"%(n,i+1))
            if kind=="Card": outs.append(t)
            else:
                fv.Select(); f=put(comp.AddTool("Fuse.SMK2_"+kind,8,i*3),nm,8,i*3); fv.Select(); f.Image.ConnectTo(src_out(t)); outs.append(f)
    end_chain(comp,fv,put,n,bg,outs)
    return comp
def inst_run(specs,w=1920,h=1080,rtag="1080p",maxwait=150,prefix="H9S_"):
    pm=resolve.GetProjectManager(); out=[]
    for kind,count in specs:
        short=kind.replace("SMK2_","")
        n="%s%s_x%d_%s"%(prefix,short,count,rtag)
        pj=pm.GetCurrentProject()
        ex=any(pj.GetTimelineByIndex(i).GetName()==n for i in range(1,pj.GetTimelineCount()+1))
        if not ex:
            build_inst(n,kind,count,"%s - what: %d instances of %s, 60 fps cold 300-frame benchmark at %dx%d (each instance has its own source)."%(n,count,kind,w,h),w=w,h=h)
            pm.SaveProject()
        c=goto(n)
        while pm.GetCurrentProject().IsRenderingInProgress(): time.sleep(1)
        time.sleep(2); goto(n); time.sleep(1)
        a=bench2(n,"a",w,h,maxwait=maxwait); b=bench2(n,"b",w,h,maxwait=maxwait)
        out.append((short,count,rtag,a[3],b[3],a[2],b[2]))
    return out
def inst_thread(specs,outfile,**kw):
    def run():
        out=[]
        for s in specs:
            try: out+=inst_run([s],**kw)
            except Exception as e: out.append((s[0],s[1],"ERR",str(e)[:120]))
            _json.dump(out,open(outfile,"w"))
        _json.dump(out+[("DONE",)],open(outfile,"w"))
    th=threading.Thread(target=run,daemon=True); th.start(); return th
