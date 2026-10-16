#!/usr/bin/env python3
"""Build the Edit-page bundle dist/SMK2_Titles_v<VERSION>.drfx: every generator macro as a complete title (macro group + MediaOut) under Edit/Titles/SMK2/.
Double-click installs it into the Effects Library (Phase 0 S5). A .drfx does NOT carry Fuses: install them with install.py first (the macros need them).
Usage: python build/make_drfx.py"""
import os, re, sys, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import make_macros
VERSION = open(os.path.join(ROOT, "VERSION")).read().strip()
SKIP = {"SMK2_Callout"}          # parked by the owner; still shipped as a macro, not as a title

def title_name(macro):
    """SMK2_StatCard_Neon -> 'SMK2 StatCard Neon' (what the Effects Library shows is the file name)."""
    return macro.replace("_", " ")

def build():
    out = os.path.join(ROOT, "dist"); os.makedirs(out, exist_ok=True)
    zp = os.path.join(out, f"SMK2_Titles_v{VERSION}.drfx")
    names = []
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for name, fn in make_macros.MACROS.items():
            if name in SKIP: continue
            text = fn().render(title=True)
            zi = zipfile.ZipInfo(f"Edit/Titles/SMK2/{title_name(name)}.setting", (2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, text.encode("utf-8")); names.append(name)
    return zp, names

if __name__ == "__main__":
    zp, names = build(); print("drfx:", os.path.relpath(zp, ROOT), len(names), "titles")
