import time, os
exec(open("D:/SMK/SMKV2/smk-v2/results/h5.py").read())
TXT="SMK TEXT DEMO"
def build12(name, note, fps=60, text=TXT, count=13, kind="SMK2_TextLetter"):
    comp,fv,bg=setup(name,note,fps=fps)
    gs=add_rows(comp,fv,bg,name,[kind]); g=gs[0]
    g.SetInput("Follower_Text",text,0); g.SetInput("UIT_Ctrl_Count",count,0); g.SetInput("UIT_Ctrl_Blur",4,0)
    bg.TopLeftRed=0.1
    return comp,fv,bg,g
FINALS={"UIT_Dist":"UIT_Ctrl.SlideDist*a","UIT_Opacity":"math.max(0,math.min(1,1-(1-UIT_Ctrl.Fade)*a))","UIT_Scale":"math.max(0.0001,1+(UIT_Ctrl.Scale-1)*a)","UIT_AngleZ":"UIT_Ctrl.Rot*a","UIT_Blur":"UIT_Ctrl.Blur*a"}
def spring_expr(final):
    return ('(function() local r=comp:GetPrefs("Comp.FrameFormat.Rate") local t=(time-comp.RenderStart)/r local ti=t-UIT_Ctrl.InDelay local a=1 '
            'if ti>=0 then local k=math.max(UIT_Ctrl.Stiff,1) local w=math.sqrt(k) local z=math.min(0.999,math.max(0.05,UIT_Ctrl.Damp/(2*w))) '
            'local wd=w*math.sqrt(1-z*z) a=math.exp(-z*w*ti)*(math.cos(wd*ti)+z*w/wd*math.sin(wd*ti)) end return %s end)()'%final)
def trivial_expr(final):
    return '(function() local a=math.max(0,1-(time-comp.RenderStart)/12) return %s end)()'%final
def bench(nm, tag, frames=300, outdir="s10"):
    p=resolve.GetProjectManager().GetCurrentProject()
    t=[p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==nm][0]
    p.SetCurrentTimeline(t); time.sleep(1); resolve.OpenPage("fusion"); time.sleep(1.5)
    comp=resolve.Fusion().GetCurrentComp(); a=t.GetStartFrame()
    bg=comp.FindTool(nm+"_Background"); v=bg.GetInput("TopLeftRed"); bg.TopLeftRed=v+0.001
    d="D:/SMK/SMKV2/smk-v2/results/%s/%s_%s"%(outdir,nm,tag); os.makedirs(d,exist_ok=True)
    p.SetCurrentRenderFormatAndCodec("PNG","RGB8")
    p.SetRenderSettings({"FormatWidth":1920,"FormatHeight":1080,"SelectAllFrames":False,"MarkIn":a,"MarkOut":a+frames-1,"TargetDir":d,"CustomName":"r_"})
    jid=p.AddRenderJob(); p.StartRendering(jid); return d

def chain(comp, amt_body_expr=None):
    """Rewire the macro's 5 Calculations into the linked chain (Y3). amt_body_expr: full expression returning `a`, or None to reuse macro's long body."""
    fo=comp.FindTool("UIT_Follower")
    fo.AddModifier("MiterLimit1","Calculation"); amt=fo.MiterLimit1.GetConnectedOutput().GetTool()
    if amt_body_expr is None:
        full=comp.FindTool("UIT_Opacity").FirstOperand.GetExpression(); body=full[len("(function() "):full.rindex("return ")]
        amt_body_expr="(function() "+body+"return a end)()"
    amt.FirstOperand.SetExpression(amt_body_expr); amt.SecondOperand=0
    out=amt.GetOutputList()[1]
    d=comp.FindTool("UIT_Dist"); d.FirstOperand.SetExpression(None); d.FirstOperand.ConnectTo(out); d.SecondOperand.SetExpression("UIT_Ctrl.SlideDist"); d.Operator=2
    for n,e in (("UIT_AngleZ","UIT_Ctrl.Rot"),("UIT_Blur","UIT_Ctrl.Blur")):
        c=comp.FindTool(n); c.FirstOperand.SetExpression(None); c.FirstOperand.ConnectTo(out); c.SecondOperand.SetExpression(e); c.Operator=2
    for inp,n,e,op in (("MiterLimit2","UIT_Opacity","(1-UIT_Ctrl.Fade)",5),("MiterLimit3","UIT_Scale","(UIT_Ctrl.Scale-1)",0)):
        fo.AddModifier(inp,"Calculation"); h=fo[inp].GetConnectedOutput().GetTool()
        h.FirstOperand.ConnectTo(out); h.SecondOperand.SetExpression(e); h.Operator=2
        c=comp.FindTool(n); c.FirstOperand.SetExpression(None); c.FirstOperand.ConnectTo(h.GetOutputList()[1]); c.SecondOperand=1; c.Operator=op
    return amt
