exec(open("D:/SMK/SMKV2/smk-v2/results/h11.py").read())
MACROS=["SMK2_UIBlock","SMK2_ProgressRing","SMK2_ProgressBar","SMK2_TextLetter","SMK2_TextWord","SMK2_TextLine","SMK2_Callout","SMK2_CardStack","SMK2_StatCard","SMK2_ClickDemo"]
for b in ("UIBlock","CardStack","StatCard","ClickDemo"):
    for s in ("_Glass","_Neon","_Soft"): MACROS.append("SMK2_"+b+s)
FUSES=["Animator","Motion","MotionRig","Shape","Cursor","Connector","Look","Relief","Reflection","PageCurl","Bloom","LongShadow"]
BG=(0.2,0.2,0.25)
def end_chain(comp,fv,put,n,bg,srcs):
    prev=bg.Output
    for i,s in enumerate(srcs):
        m=put(comp.AddTool("Merge",12,i*3),"%s_Merge%d"%(n,i+1),12,i*3); fv.Select(); m.Background.ConnectTo(prev); m.Foreground.ConnectTo(src_out(s)); prev=m.Output
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,16,(len(srcs)-1)*3); mo.Input.ConnectTo(prev)
def text_src(comp,fv,put,n,row=0,txt="SMK",cx=0.5,cy=0.5,size=0.12):
    return add_text(comp,fv,put,n,row,txt,cx,cy,size,name="%s_TextPlus"%n)
def build_product(n,kind,note,w=1920,h=1080,fps=None):
    """one comp with one macro (kind) or Fuse (kind without SMK2_ prefix or full id) over a plain background; returns (comp,tools,msg)"""
    comp,fv,bg,put=setup_res(n,note,w=w,h=h,fps=fps,bgc=BG)
    tools=[]
    if kind.startswith("SMK2_"):
        g=add_macro(comp,fv,put,n,kind,0,n+"_"+kind[5:]); tools=[g]; end_chain(comp,fv,put,n,bg,[g])
    else:
        t=text_src(comp,fv,put,n,0)
        if kind in ("Shape","Cursor","Connector"):
            fv.Select(); f=put(comp.AddTool("Fuse.SMK2_"+kind,8,0),n+"_"+kind,8,0); fv.Select(); tools=[f]; end_chain(comp,fv,put,n,bg,[f])
        elif kind in ("Motion","MotionRig"):
            fv.Select(); mrg=put(comp.AddTool("Merge",12,0),n+"_Merge1",12,0); fv.Select(); mrg.Background.ConnectTo(bg.Output); mrg.Foreground.ConnectTo(src_out(t))
            mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,16,0); mo.Input.ConnectTo(mrg.Output)
            tools=[t,mrg]
            fv.Select()
            if kind=="Motion": t.AddModifier("Size","Fuse.SMK2_Motion")
            else: mrg.AddModifier("Blend","Fuse.SMK2_MotionRig")
        else:
            fv.Select(); f=put(comp.AddTool("Fuse.SMK2_"+kind,8,0),n+"_"+kind,8,0); fv.Select(); f.Image.ConnectTo(src_out(t)); tools=[f]; end_chain(comp,fv,put,n,bg,[f])
    return comp,tools
def nonbg(path,bg=None,step=4,thr=6):
    import glob
    from PIL import Image
    f=glob.glob(path+'/*.png')[0]; im=Image.open(f).convert('RGB'); px=im.load(); W,H=im.size
    b=bg or px[2,2]
    n=0; tot=0
    for y in range(0,H,step):
        for x in range(0,W,step):
            d=max(abs(px[x,y][c]-b[c]) for c in range(3))
            if d>thr: n+=1; tot+=d
    return n,tot
import shutil, os
R="D:/SMK/SMKV2/smk-v2/results/"
def rm(d): shutil.rmtree(R+d,ignore_errors=True)
def run_h1(kinds, frames=(3,12,60,116)):
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
            d="p12_h1_%s_f%d"%(short,f); rm(d)
            st=render_res(d,f,f,1920,1080,wait=10)
            row.append(st[0])
        out.append(row)
    return out
def build_matrix_comp(n,w,h,fps,note):
    comp,fv,bg,put=setup_res(n,note,w=w,h=h,fps=fps,bgc=BG)
    gs=[]
    for i,k in enumerate(["SMK2_UIBlock","SMK2_CardStack","SMK2_StatCard","SMK2_TextLetter","SMK2_ProgressRing","SMK2_ClickDemo"]):
        g=add_macro(comp,fv,put,n,k,i,"%s_%s"%(n,k[5:])); gs.append(g)
    g=gs[0]; g.SetInput("Shape_CX",0.15,0); g.SetInput("Shape_CY",0.8,0); g.SetInput("Shape_W",0.2,0)
    g=gs[1]; g.SetInput("UIL_S1_CX",0.5,0); g.SetInput("UIL_S1_CY",0.9,0); g.SetInput("UIL_S1_W",0.2,0); g.SetInput("UIL_S1_H",0.03,0); g.SetInput("UIL_L1_Size",0.012,0); g.SetInput("UIL_Ctrl_Gap",0.004,0)
    g=gs[2]; g.SetInput("UIS_Card_CX",0.85,0); g.SetInput("UIS_Card_CY",0.75,0); g.SetInput("UIS_Card_W",0.2,0)
    g=gs[3]; g.SetInput("UIT_Text_Center",[0.2,0.45],0)
    g=gs[5]; g.SetInput("UID_Card_CX",0.5,0); g.SetInput("UID_Card_CY",0.25,0)
    fv.Select(); co=put(comp.AddTool("Fuse.SMK2_Connector",4,18),n+"_Connector",4,18); fv.Select(); co.SetInput("AP",[0.1,0.1],0); co.SetInput("BP",[0.4,0.3],0); gs.append(co)
    t=add_text(comp,fv,put,n,7,"SHINE",0.8,0.3,0.1,name=n+"_TextPlus")
    fv.Select(); lk=put(comp.AddTool("Fuse.SMK2_Look",8,21),n+"_LookShine",8,21); fv.Select(); lk.Image.ConnectTo(src_out(t)); lk.SetInput("GlowOn",0,0); lk.SetInput("ShineOn",1,0); lk.SetInput("ShineAuto",1,0); gs.append(lk)
    end_chain(comp,fv,put,n,bg,gs)
    return comp
def build_res_comp(n,w,h,note,items=("Look","Bloom","LongShadow","Reflection","PageCurl","Relief","Shape","StatCard")):
    comp,fv,bg,put=setup_res(n,note,w=w,h=h,bgc=BG)
    srcs=[]; row=0
    asp=w/float(h)
    def cardat(i,cx,cy,col=(0.9,0.9,0.95)):
        s=card(comp,fv,put,n,i,cx,cy,w=0.08,h=0.08,col=col,radius=0.15); s.SetInput("SCA",0,0); s.SetInput("InDur",0,0); return s
    cells={"Look":(0.12,0.75),"Bloom":(0.37,0.75),"LongShadow":(0.62,0.75),"Reflection":(0.87,0.7),"Relief":(0.12,0.3),"Shape":(0.37,0.3)}
    # page curl first (bottom layer)
    if "PageCurl" in items:
        fv.Select(); pg=put(comp.AddTool("Background",4,row*3),n+"_PageSolid",4,row*3); fv.Select(); pg.TopLeftRed,pg.TopLeftGreen,pg.TopLeftBlue,pg.TopLeftAlpha=0.3,0.3,0.4,1
        fv.Select(); pc=put(comp.AddTool("Fuse.SMK2_PageCurl",8,row*3),n+"_PageCurl",8,row*3); fv.Select(); pc.Image.ConnectTo(src_out(pg)); pc.SetInput("Mode",2,0); pc.SetInput("Progress",0.35,0)
        srcs.append(pc); row+=1
    for k in ("Look","Bloom","LongShadow","Reflection","Relief"):
        if k not in items: continue
        cx,cy=cells[k]; s=cardat(row,cx,cy+(0.04*1920/h if k=="Reflection" else 0))
        fv.Select(); f=put(comp.AddTool("Fuse.SMK2_"+k,8,row*3),"%s_%s"%(n,k),8,row*3); fv.Select(); f.Image.ConnectTo(src_out(s))
        if k=="Bloom": f.SetInput("GlowR",300,0)
        if k=="LongShadow": f.SetInput("Length",1000,0)
        if k=="Reflection": f.SetInput("Base",cy-0.0,0)
        srcs.append(f); row+=1
    if "Shape" in items:
        cx,cy=cells["Shape"]; s=card(comp,fv,put,n,row,cx,cy,w=0.1,h=0.06,col=(0.9,0.5,0.2),radius=0.3,name=n+"_Shape"); s.SetInput("InDur",0,0); srcs.append(s); row+=1
    if "StatCard" in items:
        g=add_macro(comp,fv,put,n,"SMK2_StatCard",row,n+"_StatCard"); g.SetInput("UIS_Card_CX",0.75,0); g.SetInput("UIS_Card_CY",0.3,0); g.SetInput("UIS_Card_W",0.2,0); srcs.append(g); row+=1
    end_chain(comp,fv,put,n,bg,srcs)
    return comp
def build_h4(n,start=0,length=120,fps=60,note=""):
    comp,fv,bg,put=setup_res(n,note,fps=fps,bgc=BG)
    srcs=[]
    s=card(comp,fv,put,n,0,0.12,0.8,w=0.1,h=0.08,col=(0.9,0.5,0.2),radius=0.3,name=n+"_Shape"); srcs.append(s)   # default In/Out animation
    t=text_src(comp,fv,put,n,1,"ANIM",0.35,0.8,0.1)
    fv.Select(); a=put(comp.AddTool("Fuse.SMK2_Animator",8,3),n+"_Animator",8,3); fv.Select(); a.Image.ConnectTo(src_out(t)); a.SetInput("InEngine",1,0); a.SetInput("OutEngine",3,0); a.SetInput("InDur",0.6,0); srcs.append(a)
    g=add_macro(comp,fv,put,n,"SMK2_TextLetter",2,n+"_TextLetter"); g.SetInput("UIT_Text_Center",[0.6,0.8],0); srcs.append(g)
    g=add_macro(comp,fv,put,n,"SMK2_StatCard",3,n+"_StatCard"); g.SetInput("UIS_Card_CX",0.85,0); g.SetInput("UIS_Card_CY",0.8,0); g.SetInput("UIS_Card_W",0.18,0); srcs.append(g)
    fv.Select(); co=put(comp.AddTool("Fuse.SMK2_Connector",8,12),n+"_Connector",8,12); fv.Select(); co.SetInput("AP",[0.1,0.5],0); co.SetInput("BP",[0.4,0.55],0); co.SetInput("PulseOn",1,0); srcs.append(co)
    fv.Select(); cu=put(comp.AddTool("Fuse.SMK2_Cursor",8,15),n+"_Cursor",8,15); fv.Select(); srcs.append(cu)
    t2=text_src(comp,fv,put,n,6,"SHINE",0.65,0.5,0.1)
    fv.Select(); lk=put(comp.AddTool("Fuse.SMK2_Look",8,18),n+"_LookShine",8,18); fv.Select(); lk.Image.ConnectTo(src_out(t2)); lk.SetInput("GlowOn",0,0); lk.SetInput("ShineOn",1,0); lk.SetInput("ShineAuto",1,0); lk.SetInput("ShineRepeat",1.0,0); srcs.append(lk)
    s3=card(comp,fv,put,n,8,0.2,0.2,w=0.08,h=0.08,col=(0.2,0.7,0.4),radius=0.1,name=n+"_RippleCard"); s3.SetInput("InDur",0,0); s3.SetInput("SCA",0,0)
    fv.Select(); rf=put(comp.AddTool("Fuse.SMK2_Reflection",8,24),n+"_ReflectionRipple",8,24); fv.Select(); rf.Image.ConnectTo(src_out(s3)); rf.SetInput("Base",0.2,0); rf.SetInput("RippleAmp",8,0); rf.SetInput("RippleSpeed",1.0,0); srcs.append(rf)
    s4=card(comp,fv,put,n,9,0.5,0.25,w=0.08,h=0.08,col=(0.9,0.9,0.2),radius=0.1,name=n+"_ShadowCard"); s4.SetInput("InDur",0,0); s4.SetInput("SCA",0,0)
    fv.Select(); ls=put(comp.AddTool("Fuse.SMK2_LongShadow",8,27),n+"_LongShadow",8,27); fv.Select(); ls.Image.ConnectTo(src_out(s4)); ls.SetInput("Length",300,0); srcs.append(ls)
    fv.Select(); pgb=put(comp.AddTool("Background",4,30),n+"_PageSolid",4,30); fv.Select(); pgb.TopLeftRed,pgb.TopLeftGreen,pgb.TopLeftBlue,pgb.TopLeftAlpha=0.25,0.5,0.8,1
    fv.Select(); pc=put(comp.AddTool("Fuse.SMK2_PageCurl",8,30),n+"_PageCurl",8,30); fv.Select(); pc.Image.ConnectTo(src_out(pgb)); srcs.insert(0,pc)
    end_chain(comp,fv,put,n,bg,srcs)
    if start>0 or length!=120:
        comp.SetAttrs({"COMPN_GlobalStart":start,"COMPN_RenderStart":start,"COMPN_GlobalEnd":start+length-1,"COMPN_RenderEnd":start+length-1})
    return comp
IMGFUSES=["Animator","Look","Relief","Reflection","PageCurl","Bloom","LongShadow"]
def build_h7(n,case,note):
    comp,fv,bg,put=setup_res(n,note,bgc=BG)
    src=None
    if case=="noinput": src=None
    else:
        fv.Select(); b=put(comp.AddTool("Background",0,6),n+"_Source",0,6); fv.Select()
        if case=="1x1": b.UseFrameFormatSettings=0; b.Width=1; b.Height=1; b.TopLeftRed,b.TopLeftGreen,b.TopLeftBlue,b.TopLeftAlpha=1,0.5,0,1
        elif case=="transparent": b.TopLeftRed,b.TopLeftGreen,b.TopLeftBlue,b.TopLeftAlpha=1,0.5,0,0
        elif case=="big": b.UseFrameFormatSettings=0; b.Width=4000; b.Height=2500; b.TopLeftRed,b.TopLeftGreen,b.TopLeftBlue,b.TopLeftAlpha=0.9,0.5,0.1,1
        elif case=="aspect": b.TopLeftRed,b.TopLeftGreen,b.TopLeftBlue,b.TopLeftAlpha=0.9,0.5,0.1,1
        src=b
    outs=[]
    for i,k in enumerate(IMGFUSES):
        fv.Select(); f=put(comp.AddTool("Fuse.SMK2_"+k,8,3+i*3),"%s_%s"%(n,k),8,3+i*3); fv.Select()
        if src is not None: f.Image.ConnectTo(src_out(src))
        outs.append(f)
    end_chain(comp,fv,put,n,bg,outs)
    return comp
def build_h8(n,note):
    comp,fv,bg,put=setup_res(n,note,bgc=BG)
    srcs=[]; i=[0]
    def srccard(cx,cy):
        s=card(comp,fv,put,n,i[0],cx,cy,w=0.05,h=0.05,col=(0.9,0.9,0.95),radius=0.2,name="%s_src%d"%(n,i[0])); s.SetInput("InDur",0,0); s.SetInput("SCA",0,0); return s
    def fx(kind,params,label,cx,cy,extra=None):
        s=srccard(cx,cy); fv.Select(); f=put(comp.AddTool("Fuse.SMK2_"+kind,8,i[0]*3),"%s_%s_%s"%(n,kind,label),8,i[0]*3); fv.Select(); f.Image.ConnectTo(src_out(s))
        for k,v in params.items(): f.SetInput(k,v,0)
        i[0]+=1; srcs.append(f)
    cols=[0.1,0.3,0.5,0.7,0.9]
    plan=[("Look",dict(GlowR=0,OutOn=1,OutW=0,GlowQ=3),"zeroR"),("Look",dict(GlowR=300,GlowQ=3,OutOn=1,OutW=60,ShineOn=1,GradOn=1),"maxR"),
          ("Bloom",dict(GlowR=0),"R0"),("Bloom",dict(GlowR=400,GlowI=6),"R400"),("Bloom",dict(GlowR=4,GlowGamma=0.3),"R4"),
          ("LongShadow",dict(Length=0),"L0"),("LongShadow",dict(Length=1500,Curve=0.3),"L1500"),
          ("Reflection",dict(Length=0,Base=0.5),"L0"),("Reflection",dict(Length=2000,Blur0=40,BlurGrow=30,Quality=2,RippleAmp=40,Base=0.5),"max"),
          ("Relief",dict(Size=0,Depth=0),"zero"),("Relief",dict(Size=80,Depth=12,Quality=2),"max"),
          ("Animator",dict(InDur=0,OutDur=0,Stagger=1,Index=200),"dur0_idx200"),("Animator",dict(Stagger=0,Index=0,InDur=10,OutDur=10),"stagger0")]
    for k,(kind,params,label) in enumerate(plan):
        fx(kind,params,label,cols[k%5],0.85-0.17*(k//5))
    # Shape extremes (generator)
    for j,(label,p) in enumerate((("w0",dict(W=0,H=0,Radius=0.5,Thick=0)),("huge",dict(W=2,H=2,Radius=0.5,Thick=400)))):
        fv.Select(); sh=put(comp.AddTool("Fuse.SMK2_Shape",4,i[0]*3),"%s_Shape_%s"%(n,label),4,i[0]*3); fv.Select()
        for kk,vv in p.items(): sh.SetInput(kk,vv,0)
        sh.SetInput("CX",0.3+0.4*j,0); sh.SetInput("CY",0.15,0); srcs.append(sh); i[0]+=1
    # Connector: 6 spline points, zero length, thick 60 + dash 200/0
    cons=[dict(Mode=4,N=6,AP=[0.1,0.1],BP=[0.4,0.1],P1=[0.15,0.2],P2=[0.2,0.1],P3=[0.25,0.2],P4=[0.3,0.1],P5=[0.33,0.2],P6=[0.36,0.1],Thick=60),dict(AP=[0.5,0.1],BP=[0.5,0.1]),dict(Dash=200,DGap=0,EndSize=100,AP=[0.6,0.08],BP=[0.9,0.12],PulseOn=1,PulseCount=3)]
    for j,p in enumerate(cons):
        fv.Select(); co=put(comp.AddTool("Fuse.SMK2_Connector",4,i[0]*3),"%s_Connector_%d"%(n,j),4,i[0]*3); fv.Select()
        for kk,vv in p.items(): co.SetInput(kk,vv,0)
        srcs.append(co); i[0]+=1
    # Cursor: 8 waypoints
    fv.Select(); cu=put(comp.AddTool("Fuse.SMK2_Cursor",4,i[0]*3),n+"_Cursor_8wp",4,i[0]*3); fv.Select(); cu.SetInput("N",8,0)
    for k in range(1,9): cu.SetInput("P%d"%k,[0.1+0.1*k,0.5+0.1*((-1)**k)],0)
    srcs.append(cu); i[0]+=1
    end_chain(comp,fv,put,n,bg,srcs)
    return comp
def h9_run(items,tag_res=("1080p",1920,1080),maxwait=60):
    pm=resolve.GetProjectManager(); out=[]
    rtag,w,h=tag_res
    for kind in items:
        short=kind[5:] if kind.startswith("SMK2_") else kind
        n="H9_%s_%s"%(short,rtag)
        pj=resolve.GetProjectManager().GetCurrentProject()
        exists=any(pj.GetTimelineByIndex(i).GetName()==n for i in range(1,pj.GetTimelineCount()+1))
        if exists:
            cc=goto(n)
            if len(cc.GetToolList(False))<4:      # half-built comp from an interrupted call: delete and rebuild
                mp_=pj.GetMediaPool(); keep=[pj.GetTimelineByIndex(i) for i in range(1,pj.GetTimelineCount()+1) if pj.GetTimelineByIndex(i).GetName()=="tmp_keep"][0]
                pj.SetCurrentTimeline(keep); mp_.DeleteTimelines([pj.GetTimelineByIndex(i) for i in range(1,pj.GetTimelineCount()+1) if pj.GetTimelineByIndex(i).GetName()==n]); exists=False
        if exists: pass
        elif kind=="NoFx":
            comp,fv,bg,put=setup_res(n,"%s - what: baseline, a Text+ over a plain background, 60 fps cold 300-frame benchmark at %dx%d."%(n,w,h),w=w,h=h,fps=60,bgc=BG)
            t=text_src(comp,fv,put,n,0)
            m=put(comp.AddTool("Merge",12,0),n+"_Merge1",12,0); fv.Select(); m.Background.ConnectTo(bg.Output); m.Foreground.ConnectTo(src_out(t))
            mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,16,0); mo.Input.ConnectTo(m.Output)
        else:
            build_product(n,kind,"%s - what: %s alone with defaults over a plain background (image Fuses fed by a Text+), 60 fps cold 300-frame benchmark at %dx%d."%(n,kind,w,h),w=w,h=h,fps=60)
        if not exists: pm.SaveProject()
        goto(n)
        while resolve.GetProjectManager().GetCurrentProject().IsRenderingInProgress(): time.sleep(1)
        time.sleep(2); goto(n); time.sleep(1)
        for _try in range(3):
            if resolve.Fusion().GetCurrentComp().FindTool(n+"_Background"): break
            time.sleep(2); goto(n)
        a=bench2(n,"a",w,h,maxwait=maxwait); b=bench2(n,"b",w,h,maxwait=maxwait)
        out.append((kind,rtag,a[3],b[3],a[2],b[2]))
    return out
import threading, json as _json
def h9_thread(items,tag_res,outfile):
    def run():
        out=[]
        for kind in items:
            try:
                r=h9_run([kind],tag_res)
                out+=r
            except Exception as e:
                out.append((kind,tag_res[0],"ERR",str(e)[:120]))
            _json.dump(out,open(outfile,"w"))
        _json.dump(out+[("DONE",)],open(outfile,"w"))
    th=threading.Thread(target=run,daemon=True); th.start(); return th
