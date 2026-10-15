exec(open("D:/SMK/SMKV2/smk-v2/results/h11.py").read())
import json as _json, threading
def snap_comp(c):
    out={}
    for t in c.GetToolList(False).values():
        conn=0; spl=0
        try:
            for i in t.GetInputList().values():
                try:
                    if i.GetConnectedOutput() is not None: conn+=1
                except Exception: pass
        except Exception: pass
        out[t.Name]=[t.ID,conn]
    return out
def h12_snapshot(outfile,prefix="H1_"):
    pj=resolve.GetProjectManager().GetCurrentProject(); res={}
    names=[pj.GetTimelineByIndex(i).GetName() for i in range(1,pj.GetTimelineCount()+1)]
    names=[x for x in names if x.startswith(prefix)]
    for nm in names:
        try:
            c=goto(nm); time.sleep(0.5); res[nm]=snap_comp(c)
        except Exception as e: res[nm]="ERR "+repr(e)[:150]
        _json.dump(res,open(outfile,"w"))
    res["DONE"]=True; _json.dump(res,open(outfile,"w"))
def h12_render(outfile,prefix="H1_",frames=(3,12,60,116)):
    pj=resolve.GetProjectManager().GetCurrentProject(); res={}
    names=[pj.GetTimelineByIndex(i).GetName() for i in range(1,pj.GetTimelineCount()+1)]
    names=[x for x in names if x.startswith(prefix)]
    for nm in names:
        short=nm[3:]; row=[]
        try:
            c=goto(nm); time.sleep(0.5)
            for f in frames:
                d="p12_h12_%s_f%d"%(short,f); shutil.rmtree(R+d,ignore_errors=True)
                st=render_res(d,f,f,1920,1080,wait=12); row.append(st[0])
        except Exception as e: row.append("ERR "+repr(e)[:150])
        res[nm]=row; _json.dump(res,open(outfile,"w"))
    res["DONE"]=True; _json.dump(res,open(outfile,"w"))
