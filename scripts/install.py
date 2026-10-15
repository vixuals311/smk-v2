#!/usr/bin/env python3
"""Install SMK v2 into DaVinci Resolve (Fuses + macros). Works from a git checkout (builds first) and from an unzipped release (no build step).

  python install.py                 install
  python install.py --dry-run       show what would be copied / removed, change nothing
  python install.py --uninstall     remove the SMK2 folders this installer created
  python install.py --target DIR    use DIR as the Fusion support folder (contains Fuses/ and Macros/) instead of the default
  python install.py --include-spikes  (checkout only) also install the Phase 0-9 spike Fuses
A .drfx does not load Fuses (Phase 0 / S5), hence this installer. Restart Resolve afterwards."""
import argparse, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) if os.path.isfile(os.path.join(os.path.dirname(HERE), "build", "build.py")) else HERE   # checkout vs release
FOLDER = "SMK2"

def fusion_support_dir(target=None):
    """Folder that contains Fuses/ and Macros/."""
    if target: return os.path.abspath(os.path.expanduser(target))
    if sys.platform == "win32":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Blackmagic Design", "DaVinci Resolve", "Support", "Fusion")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion")
    return os.path.expanduser("~/.local/share/DaVinciResolve/Fusion")

def sources(root, include_spikes=False):
    """Returns (fuse_files, macro_files) as lists of absolute paths; supports checkout (dist/...) and release (fuses/, macros/) layouts."""
    def lst(*cands, ext):
        for c in cands:
            d = os.path.join(root, c)
            if os.path.isdir(d): return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(ext) and not f.startswith("._")]
        return []
    fuses = lst("dist/fuses", "fuses", ext=".fuse")
    if include_spikes: fuses += lst("dist/spikes", ext=".fuse")
    macros = lst("dist/templates", "macros", ext=".setting")
    return fuses, macros

def plan(root, target=None, include_spikes=False, uninstall=False):
    base = fusion_support_dir(target)
    fdst, mdst = os.path.join(base, "Fuses", FOLDER), os.path.join(base, "Macros", FOLDER)
    if uninstall:
        return [("remove", d) for d in (fdst, mdst) if os.path.isdir(d)]
    fuses, macros = sources(root, include_spikes)
    return [("copy", f, fdst) for f in fuses] + [("copy", m, mdst) for m in macros]

def run(actions, dry=False, out=print):
    for a in actions:
        if a[0] == "copy":
            out(("would install " if dry else "installed ") + os.path.basename(a[1]) + " -> " + a[2])
            if not dry: os.makedirs(a[2], exist_ok=True); shutil.copy(a[1], a[2])
        else:
            out(("would remove " if dry else "removed ") + a[1])
            if not dry: shutil.rmtree(a[1])
    return len(actions)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Install SMK v2 into DaVinci Resolve")
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--target", help="Fusion support folder (contains Fuses/ and Macros/)")
    ap.add_argument("--include-spikes", action="store_true"); ap.add_argument("--no-build", action="store_true")
    a = ap.parse_args(argv)
    if not a.uninstall and not a.no_build and os.path.isfile(os.path.join(ROOT, "build", "build.py")):
        if a.dry_run: print("(dry run: skipping build; using the existing dist/)")
        else: subprocess.check_call([sys.executable, os.path.join(ROOT, "build", "build.py")])
    acts = plan(ROOT, a.target, a.include_spikes, a.uninstall)
    if not acts:
        print("nothing to " + ("remove" if a.uninstall else "install") + " (no built files found; run build/build.py)" if not a.uninstall else "nothing to remove (SMK2 is not installed there)")
        return 0 if a.uninstall else 1
    run(acts, a.dry_run)
    print(("dry run only, nothing changed." if a.dry_run else "done.") + (" Restart Resolve." if not a.dry_run and not a.uninstall else ""))
    return 0

if __name__ == "__main__":
    sys.exit(main())
