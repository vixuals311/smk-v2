#!/usr/bin/env python3
"""Build the release zip: dist/release/SMK2_v<VERSION>.zip (+ .sha256). Layout inside:
  SMK2_v<VERSION>/{fuses/*.fuse, macros/*.setting, install.py, install.bat, install.command, README.txt, LICENSE, NOTICE, MANUAL.md, VERSION, SHA256SUMS}
No ._* / __MACOSX / .DS_Store / Thumbs.db metadata; no machine paths (CustomData.Path) in macros. Usage: python build/package.py"""
import hashlib, os, re, shutil, subprocess, sys, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = open(os.path.join(ROOT, "VERSION")).read().strip()
JUNK = re.compile(r"(^\._|^\.DS_Store$|^Thumbs\.db$|^__MACOSX$)")

INSTALL_BAT = r"""@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul && (py -3 install.py %* & goto :done)
where python >nul 2>nul && (python install.py %* & goto :done)
echo Python 3 was not found. Install it from python.org, or copy the files in "fuses" to %%APPDATA%%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Fuses\SMK2
echo and the files in "macros" to ...\Fusion\Macros\SMK2
:done
pause
"""
INSTALL_COMMAND = """#!/bin/bash
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then python3 install.py "$@"; else
  echo "Python 3 was not found. Copy the files in 'fuses' to ~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Fuses/SMK2 and 'macros' to .../Fusion/Macros/SMK2"; fi
read -n 1 -s -r -p "Press any key to close"
"""
README = """SMK v2 (Fusion SaaS Motion Kit) {v}

INSTALL
  Windows: double-click install.bat
  macOS:   double-click install.command (if macOS blocks it: right-click > Open, or run `chmod +x install.command`)
  Any OS:  python3 install.py        (options: --dry-run, --uninstall, --target <Fusion folder>)
Then restart DaVinci Resolve. Fuses appear under Effects > Fuses > SMK v2, macros under Effects > Tools > Macros > SMK2.
EDIT PAGE (optional): double-click SMK2_Titles_v{v}.drfx and confirm; the products then appear under Effects > Titles > SMK2 (drag onto the timeline). Install the Fuses first: a .drfx cannot carry them. Without the Fuses every title opens with "Warning: Unknown tool found ... Fuse.SMK2_Shape" (click OK, install the Fuses, restart Resolve).
UNINSTALL: python3 install.py --uninstall   (removes only the SMK2 folders)
Manual: MANUAL.md.  Licence: LICENSE.  Credits: NOTICE.  Integrity: SHA256SUMS.
"""

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def clean_macro(text):
    """Drop machine-specific CustomData paths."""
    return re.sub(r'\n[ \t]*CustomData = \{[^{}]*Path = "[^"]*"[^{}]*\},?', "", text)

def build_release():
    subprocess.check_call([sys.executable, os.path.join(ROOT, "build", "build.py")], stdout=subprocess.DEVNULL)
    subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "gen_manual.py")], stdout=subprocess.DEVNULL)
    subprocess.check_call([sys.executable, os.path.join(ROOT, "build", "make_drfx.py")], stdout=subprocess.DEVNULL)
    rel = os.path.join(ROOT, "dist", "release"); name = f"SMK2_v{VERSION}"; stage = os.path.join(rel, name)
    shutil.rmtree(rel, ignore_errors=True); os.makedirs(os.path.join(stage, "fuses")); os.makedirs(os.path.join(stage, "macros"))
    for f in sorted(os.listdir(os.path.join(ROOT, "dist/fuses"))):
        if f.endswith(".fuse") and not JUNK.match(f): shutil.copy(os.path.join(ROOT, "dist/fuses", f), os.path.join(stage, "fuses", f))
    tdir = os.path.join(ROOT, "dist/templates")
    for f in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        if f.endswith(".setting") and not JUNK.match(f):
            open(os.path.join(stage, "macros", f), "w", newline="\n").write(clean_macro(open(os.path.join(tdir, f)).read()))
    shutil.copy(os.path.join(ROOT, "scripts/install.py"), stage)
    shutil.copy(os.path.join(ROOT, "dist", f"SMK2_Titles_v{VERSION}.drfx"), stage)
    open(os.path.join(stage, "install.bat"), "w", newline="\r\n").write(INSTALL_BAT)
    open(os.path.join(stage, "install.command"), "w", newline="\n").write(INSTALL_COMMAND)
    open(os.path.join(stage, "README.txt"), "w", newline="\n").write(README.format(v=VERSION))
    for f in ("LICENSE", "NOTICE", "VERSION"): shutil.copy(os.path.join(ROOT, f), stage)
    shutil.copy(os.path.join(ROOT, "docs/MANUAL.md"), os.path.join(stage, "MANUAL.md"))
    files = sorted(os.path.relpath(os.path.join(d, x), stage).replace(os.sep, "/") for d, _, fs in os.walk(stage) for x in fs)
    open(os.path.join(stage, "SHA256SUMS"), "w", newline="\n").write("".join(f"{sha256(os.path.join(stage, f))}  {f}\n" for f in files))
    files.append("SHA256SUMS")
    zp = os.path.join(rel, name + ".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(files):
            zi = zipfile.ZipInfo(f"{name}/{f}", (2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = ((0o755 if f in ("install.command", "install.py") else 0o644) << 16)
            z.writestr(zi, open(os.path.join(stage, f), "rb").read())
    open(zp + ".sha256", "w").write(f"{sha256(zp)}  {name}.zip\n")
    return zp

if __name__ == "__main__":
    z = build_release(); print("release:", os.path.relpath(z, ROOT), "sha256", sha256(z)[:16] + "...")
