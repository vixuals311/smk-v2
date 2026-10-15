exec(open("D:/SMK/SMKV2/smk-v2/results/h8.py").read())
def add_fuse(comp,fv,bg,put,n,fuse,row=0,suffix="",col=4):
    fv.Select()
    c=put(comp.AddTool(fuse,col,row*3),"%s_%s%s"%(n,fuse.split("SMK2_")[1],suffix),col,row*3); fv.Select()
    return c
def finish_chain(comp,fv,bg,put,n,tools):
    prev=bg.Output
    for i,c in enumerate(tools):
        m=put(comp.AddTool("Merge",8,i*3),"%s_Merge%d"%(n,i+1),8,i*3); fv.Select()
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(c.Output); prev=m.Output
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,12,(len(tools)-1)*3); mo.Input.ConnectTo(prev)
