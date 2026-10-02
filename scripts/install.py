#!/usr/bin/env python3
"""Install built SMK v2 Fuses into the Resolve user Fuses folder (Windows/macOS/Linux). Usage: python scripts/install.py [--include-spikes]
Phase 0 (S5): a .drfx does not load Fuses, so Fuses need this separate step."""
import os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def fuses_dir():
    if sys.platform == "win32":
        return os.path.join(os.environ["APPDATA"], "Blackmagic Design", "DaVinci Resolve", "Support", "Fusion", "Fuses")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Fuses")
    return os.path.expanduser("~/.local/share/DaVinciResolve/Fusion/Fuses")
if __name__ == "__main__":
    subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")])
    dst = os.path.join(fuses_dir(), "SMK2"); os.makedirs(dst, exist_ok=True)
    srcs = ["dist/fuses"] + (["dist/spikes"] if "--include-spikes" in sys.argv else [])
    for s in srcs:
        for f in sorted(os.listdir(os.path.join(ROOT, s))):
            if f.endswith(".fuse"): shutil.copy(os.path.join(ROOT, s, f), dst); print("installed", f)
    print("->", dst, "(restart Resolve)")
