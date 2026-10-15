exec(open("D:/SMK/SMKV2/smk-v2/results/h6.py").read())
def mkq(name, note, kind, texts, ys, params=None, fps=None, size=0.04, per=None):
    comp,fv,bg=setup(name,note,fps=fps)
    gs=add_rows(comp,fv,bg,name,[kind]*len(texts))
    for i,g in enumerate(gs):
        g.SetInput("UIT_Ctrl_Text",texts[i],0); g.SetInput("UIT_Text_Size",size,0); g.SetInput("UIT_Text_Center",[0.5,ys[i]],0)
        for k,v in (params or {}).items(): g.SetInput("UIT_Ctrl_"+k,v,0)
        for k,v in ((per or [{}]*len(texts))[i]).items(): g.SetInput("UIT_Ctrl_"+k,v,0)
    bg.TopLeftRed=0.1
    return comp,gs

FONTS=[("Open Sans","Bold"),("Open Sans","Regular"),("Open Sans","Light"),("Arial","Bold"),("Times New Roman","Bold"),("Impact","Regular"),("Verdana","Bold"),("Georgia","Bold")]
def cfg_fonts(comp,name,kind_short,fonts=FONTS):
    for i,(f,s) in enumerate(fonts):
        g=comp.FindTool("%s_%s%d"%(name,kind_short,i+1)); g.SetInput("UIT_Text_Font",f,0)
        t=comp.FindTool("UIT_Text"+("" if i==0 else "_%d"%i)); t.Style=s
