exec(open("D:/SMK/SMKV2/smk-v2/results/h9.py").read())
def src_out(t): return list(t.GetOutputList().values())[0]
def look_chain(comp,fv,bg,put,n,sources,looks=True):
    """sources: list of tools placed by caller at x=4,y=row*3. Adds Look at x=8, Merge x=12, MediaOut x=16. returns looks"""
    prev=bg.Output; out=[]
    for i,s in enumerate(sources):
        fv.Select()
        if looks:
            L=put(comp.AddTool("Fuse.SMK2_Look",8,i*3),"%s_Look%d"%(n,i+1),8,i*3); fv.Select()
            L.Image.ConnectTo(src_out(s)); out.append(L); o=L.Output
        else: o=src_out(s)
        m=put(comp.AddTool("Merge",12,i*3),"%s_Merge%d"%(n,i+1),12,i*3); fv.Select()
        m.Background.ConnectTo(prev); m.Foreground.ConnectTo(o); prev=m.Output
    mo=comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name":n+"_MediaOut"}); fv.SetPos(mo,16,(len(sources)-1)*3); mo.Input.ConnectTo(prev)
    return out
def add_text(comp,fv,put,n,row,txt,cx,cy,size=0.15,col=(1,1,1),name=None):
    fv.Select()
    t=put(comp.AddTool("TextPlus",4,row*3),name or "%s_Text%d"%(n,row+1),4,row*3); fv.Select()
    t.StyledText=txt; t.Font="Open Sans"; t.Style="Bold"; t.Size=size; t.Center=[cx,cy]
    t.Red1,t.Green1,t.Blue1=col
    return t
def add_macro(comp,fv,put,n,kind,row,name):
    fv.Select(); before=set(x.Name for x in comp.GetToolList(False).values())
    comp.Execute('comp:Paste(bmd.readfile("%s"))'%(MAC%kind)); time.sleep(0.8)
    g=[x for x in comp.GetToolList(False).values() if x.ID=="GroupOperator" and x.Name not in before][0]
    put(g,name,4,row*3); fv.Select(); return g
