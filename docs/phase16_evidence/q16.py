import os, time, json, shutil
R = "D:/Softwares/SMK v2/docs/phase16_evidence/renders/"
os.makedirs(R, exist_ok=True)
BG = (0.2, 0.2, 0.25)

def proj():
    return resolve.GetProjectManager().GetCurrentProject()

def new_comp(name, note=None, bgc=BG):
    """one timeline + one Fusion comp per check; returns (comp, flow, bg, put)"""
    p = proj(); mp = p.GetMediaPool()
    tl = mp.CreateEmptyTimeline(name)
    p.SetCurrentTimeline(tl)
    item = tl.InsertFusionCompositionIntoTimeline()
    resolve.OpenPage("fusion"); time.sleep(1.5)
    comp = item.GetFusionCompByIndex(1)
    comp.SetAttrs({"COMPN_RenderStart": 0, "COMPN_RenderEnd": 119})
    fv = comp.CurrentFrame.FlowView
    fv.Select()
    def put(t, nm, x, y):
        t.SetAttrs({"TOOLS_Name": nm}); fv.SetPos(t, x, y); return t
    bg = put(comp.AddTool("Background", 0, 0), name + "_Background", 0, 0)
    bg.TopLeftRed = bgc[0]; bg.TopLeftGreen = bgc[1]; bg.TopLeftBlue = bgc[2]; bg.TopLeftAlpha = 1
    mo = comp.FindTool("MediaOut1"); mo.SetAttrs({"TOOLS_Name": name + "_MediaOut"})
    if note:
        nt = put(comp.AddTool("Note", 0, -2), name + "_Note", 0, -2); nt.Comments = note
    return comp, fv, bg, put

def goto(name):
    p = proj()
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        if t.GetName() == name:
            p.SetCurrentTimeline(t)
            return t.GetTimelineItemsInTrack("video", 1)[0] if False else t
    return None

def comp_of(name):
    t = goto(name)
    resolve.OpenPage("fusion"); time.sleep(1.5)
    item = t.GetItemListInTrack("video", 1)[0]
    return item.GetFusionCompByIndex(1)

def render(tag, f0, f1, wait=60):
    """render timeline range f0..f1 (frames relative to start) as PNG sequence into R/tag; returns status"""
    p = proj(); d = R + tag; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    tl = p.GetCurrentTimeline(); s = tl.GetStartFrame()
    p.DeleteAllRenderJobs()
    p.SetRenderSettings({"SelectAllFrames": False, "MarkIn": s + f0, "MarkOut": s + f1, "TargetDir": d, "CustomName": tag,
                         "FormatWidth": 1920, "FormatHeight": 1080, "ExportVideo": True, "ExportAudio": False})
    p.SetCurrentRenderFormatAndCodec("png", "RGB16") if False else p.SetCurrentRenderFormatAndCodec("png", "RGB8")
    jid = p.AddRenderJob()
    p.StartRendering(jid)
    t0 = time.time()
    while p.IsRenderingInProgress() and time.time() - t0 < wait:
        time.sleep(0.2)
    st = p.GetRenderJobStatus(jid)
    return st.get("JobStatus"), round(time.time() - t0, 2), sorted(os.listdir(d))

MAC = "C:/Users/muham/AppData/Roaming/Blackmagic Design/DaVinci Resolve/Support/Fusion/Macros/SMK2/"
FUSES = ["Animator","Motion","MotionRig","Shape","Cursor","Connector","Look","Relief","Reflection","PageCurl","Bloom","LongShadow"]
MACROS = ["Callout","CardStack","ClickDemo","ProgressBar","ProgressRing","StatCard","TextLetter","TextLine","TextWord","UIBlock"]
for b in ("CardStack","ClickDemo","StatCard","UIBlock"):
    for s in ("Glass","Neon","Soft"): MACROS.append(b+"_"+s)

def out_of(t):
    for a in ("Output", "MainOutput1"):
        o = getattr(t, a, None)
        if o is not None: return o
    return None

def text_src(comp, fv, put, n, x=0, y=3):
    fv.Select(); t = put(comp.AddTool("TextPlus", x, y), n + "_Text", x, y)
    t.StyledText = "SMK"; t.Size = 0.2; fv.Select(); return t

def build_tool(kind, n=None):
    """H1-style comp for one tool; returns (comp, main_tool)"""
    short = kind
    n = n or "S1_" + short
    comp, fv, bg, put = new_comp(n, "%s - what: %s with defaults over a plain background (image Fuses fed by a Text+). Look for: no error, output at frames 3/12/60/116." % (n, kind))
    mrg = put(comp.AddTool("Merge", 12, 0), n + "_Merge", 12, 0); fv.Select()
    mrg.Background.ConnectTo(bg.Output)
    mo = comp.FindTool(n + "_MediaOut"); fv.SetPos(mo, 16, 0); mo.Input.ConnectTo(mrg.Output)
    main = None
    if kind in ("Motion", "MotionRig"):
        t = text_src(comp, fv, put, n, 4, 0); mrg.Foreground.ConnectTo(t.Output)
        if kind == "Motion": t.AddModifier("Size", "Fuse.SMK2_Motion")
        else: mrg.AddModifier("Blend", "Fuse.SMK2_MotionRig")
        main = t
    elif kind in ("Shape", "Cursor", "Connector"):
        main = put(comp.AddTool("Fuse.SMK2_" + kind, 4, 0), n + "_" + kind, 4, 0); fv.Select(); mrg.Foreground.ConnectTo(main.Output)
    elif kind in FUSES:
        t = text_src(comp, fv, put, n, 0, 3)
        main = put(comp.AddTool("Fuse.SMK2_" + kind, 6, 3), n + "_" + kind, 6, 3); fv.Select()
        main.Input.ConnectTo(t.Output) if hasattr(main, "Input") and main.Input is not None else main.Image.ConnectTo(t.Output)
        mrg.Foreground.ConnectTo(main.Output)
    else:
        fv.Select()
        comp.Execute('comp:Paste(bmd.readfile("%s"))' % (MAC + "SMK2_" + kind + ".setting")); time.sleep(0.5)
        main = comp.FindTool("SMK2_" + kind)
        fv.SetPos(main, 4, 0); main.SetAttrs({"TOOLS_Name": n + "_" + kind}); fv.Select()
        mrg.Foreground.ConnectTo(out_of(main))
    return comp, main

def render_frames(tag, frames, wait=120):
    p = proj(); tl = p.GetCurrentTimeline(); s = tl.GetStartFrame(); ids = []
    p.DeleteAllRenderJobs()
    for f in frames:
        d = R + tag + "_f%d" % f; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        p.SetRenderSettings({"SelectAllFrames": False, "MarkIn": s + f, "MarkOut": s + f, "TargetDir": d, "CustomName": "f%d" % f,
                             "FormatWidth": 1920, "FormatHeight": 1080, "ExportVideo": True, "ExportAudio": False})
        p.SetCurrentRenderFormatAndCodec("png", "RGB8")
        ids.append(p.AddRenderJob())
    p.StartRendering(ids)
    t0 = time.time()
    while p.IsRenderingInProgress() and time.time() - t0 < wait: time.sleep(0.2)
    return [p.GetRenderJobStatus(j).get("JobStatus") for j in ids]

import threading
def run_smoke(kinds, outfile):
    def go():
        out = {}
        for k in kinds:
            try:
                comp, main = build_tool(k)
                proj().SaveProject() if False else None
                st = render_frames("S1_" + k, (3, 12, 60, 116))
                out[k] = st
            except Exception as e:
                out[k] = "ERR " + repr(e)[:200]
            json.dump(out, open(outfile, "w"))
        out["DONE"] = 1; json.dump(out, open(outfile, "w"))
    th = threading.Thread(target=go, daemon=True); th.start(); return th

def del_tl(names):
    p = proj(); mp = p.GetMediaPool(); ds = []
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        if t.GetName() in names: ds.append(t)
    return mp.DeleteTimelines(ds), len(ds)
