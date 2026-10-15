#!/usr/bin/env python3
"""Generate docs/MANUAL.md from the sources: every Fuse's name/description/header notes and its Inspector controls (parsed from Create()),
and every generated macro's published controls (parsed from dist/templates/*.setting). Usage: python tools/gen_manual.py"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def split_args(s):
    """Split a Lua argument list at top-level commas."""
    out, depth, cur, q = [], 0, "", None
    for ch in s:
        if q:
            cur += ch
            if ch == q: q = None
        elif ch in "\"'": q = ch; cur += ch
        elif ch in "({[": depth += 1; cur += ch
        elif ch in ")}]": depth -= 1; cur += ch
        elif ch == "," and depth == 0: out.append(cur.strip()); cur = ""
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

def unq(s): return s.strip().strip("\"'")

def call_args(text, fn):
    """All top-level calls `fn(...)` -> list of argument lists."""
    res = []
    for m in re.finditer(rf"(?<![\w.:]){fn}\(", text):
        i, depth, q = m.end(), 1, None
        while i < len(text) and depth:
            ch = text[i]
            if q:
                if ch == q: q = None
            elif ch in "\"'": q = ch
            elif ch == "(": depth += 1
            elif ch == ")": depth -= 1
            i += 1
        res.append(split_args(text[m.end():i - 1]))
    return res

def parse_fuse(path):
    t = open(path, encoding="utf-8").read()
    info = {"file": os.path.basename(path)}
    m = re.search(r'REGS_Name = "([^"]+)"', t); info["name"] = m.group(1) if m else os.path.basename(path)[:-4]
    m = re.search(r'REGS_OpDescription = "([^"]+)"', t); info["desc"] = m.group(1) if m else ""
    notes = []
    for line in t.splitlines():
        if line.startswith("-- @include"): continue
        if line.startswith("--"): notes.append(line[2:].strip().lstrip("—- ").strip())
        elif line.strip(): break
    info["notes"] = [n for n in notes if n]
    cm = re.search(r"function Create\(\)(.*?)\nend\n", t, re.S)
    body = cm.group(1) if cm else ""
    controls = []
    for a in call_args(body, "num"):
        if len(a) >= 5: controls.append(("slider", unq(a[1]), a[2], f"{a[3]} .. {a[4]}"))
    for a in call_args(body, "combo"):
        if len(a) >= 4: controls.append(("choice", unq(a[1]), a[2], " | ".join(re.findall(r'"([^"]*)"', a[3]))))
    for a in call_args(body, "check"):
        if len(a) >= 3: controls.append(("checkbox", unq(a[1]), a[2], "on/off"))
    for a in call_args(body, "color"):
        if len(a) >= 7: controls.append(("colour", unq(a[1]), f"{a[3]}, {a[4]}, {a[5]}, {a[6]}", "RGBA"))
    for m in re.finditer(r'self:AddInput\("([^"]+)",\s*"(\w+)",\s*\{(.*?)\}\)', body):
        nm, key, props = m.groups()
        if nm == "" or key in ("Image", "Reveal"): continue
        kind = "checkbox" if "CheckboxControl" in props else "choice" if "ComboControl" in props else "slider"
        d = re.search(r"INP_Default = ([^,}\s]+)", props)
        controls.append((kind, nm, d.group(1) if d else "", ""))
    if re.search(r"phaseControls\(", body): controls.append(("group", "In / Hold / Out motion", "", "timing, engine and amount controls per phase (see the motion reference)"))
    info["controls"] = controls
    info["inputs"] = [("Image", "main image")] + ([("Reveal (optional)", "what shows under the page")] if '"Reveal"' in body else [])
    return info

def parse_macro(path):
    t = open(path, encoding="utf-8").read()
    name = os.path.basename(path)[:-8]
    ctrls = []
    for m in re.finditer(r"InstanceInput \{(.*?)\n\t*\}", t, re.S):
        blk = m.group(1)
        n = re.search(r'Name = "([^"]+)"', blk); pg = re.search(r'Page = "([^"]+)"', blk)
        if n: ctrls.append((pg.group(1) if pg else "", n.group(1)))
    return name, ctrls

def generate():
    fuses = [parse_fuse(os.path.join(ROOT, "src/fuses", f)) for f in sorted(os.listdir(os.path.join(ROOT, "src/fuses"))) if f.endswith(".lua")]
    version = open(os.path.join(ROOT, "VERSION")).read().strip()
    out = [f"# SMK v2 manual (v{version})", "", "_Generated from the sources by `tools/gen_manual.py` — do not edit by hand._", "",
           "## Install", "", "Windows: run `install.bat`. macOS: run `install.command`. Any OS: `python3 install.py` (`--dry-run`, `--uninstall`, `--target <Fusion folder>`). Restart Resolve.",
           "Fuses: Effects ▸ Fuses ▸ SMK v2. Macros: Effects ▸ Tools ▸ Macros ▸ SMK2.", "",
           "## Conventions", "",
           "- **Seconds, clip-relative** timing: everything starts at the clip's first frame and ends with it; frame rate does not change the look.",
           "- **Sizes are px @1920**: the same value looks identical at 1080p, vertical and 4K.",
           "- **Angles:** positive = counter-clockwise. **Colours** are straight RGBA pickers.",
           "- **In / Hold / Out:** each phase has its own engine (Ease, Spring, Bounce, Elastic, Overshoot, Inertia) and its own timing; Index × Stagger delays each copy.", "",
           "## Fuses", ""]
    for f in fuses:
        out += [f"### {f['name']}", "", f["desc"] + ("." if f["desc"] and not f["desc"].endswith(".") else ""), ""]
        for n in f["notes"][:6]: out.append(f"> {n}")
        if f["notes"]: out.append("")
        out.append("**Inputs:** " + ", ".join(f"{a} ({b})" for a, b in f["inputs"])); out.append("")
        if f["controls"]:
            out += ["| Control | Type | Default | Range / options |", "|---|---|---|---|"]
            for kind, nm, d, r in f["controls"]: out.append(f"| {nm} | {kind} | {d} | {r.replace('|', '/') if kind != 'choice' else r.replace('|', '/')} |")
            out.append("")
    out += ["## Macros", ""]
    tdir = os.path.join(ROOT, "dist/templates")
    for fn in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        if not fn.endswith(".setting"): continue
        name, ctrls = parse_macro(os.path.join(tdir, fn))
        out += [f"### {name}", "", f"{len(ctrls)} published controls.", ""]
        pages = {}
        for pg, n in ctrls: pages.setdefault(pg or "Controls", []).append(n)
        for pg, ns in pages.items(): out.append(f"- **{pg}:** " + ", ".join(ns))
        out.append("")
    out += ["## Known limits", "", "See `docs/DEFERRED_WORK.md` in the repository. Viewer playback speed on the first (uncached) pass depends on your GPU; cached playback is much faster.", ""]
    return "\n".join(out)

if __name__ == "__main__":
    text = generate(); open(os.path.join(ROOT, "docs/MANUAL.md"), "w", newline="\n", encoding="utf-8").write(text)
    print("manual:", len(text.splitlines()), "lines")
