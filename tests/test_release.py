"""Release packaging + installer: builds the zip, checks contents/hygiene/checksums, runs the installer from the unzipped release and from the checkout with --target."""
import hashlib, io, os, re, subprocess, sys, tempfile, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
py = sys.executable
subprocess.check_call([py, os.path.join(ROOT, "build/package.py")], stdout=subprocess.DEVNULL)
ver = open(os.path.join(ROOT, "VERSION")).read().strip(); name = f"SMK2_v{ver}"
zp = os.path.join(ROOT, "dist/release", name + ".zip")
z = zipfile.ZipFile(zp); names = z.namelist()
check("zip exists with a top-level folder", all(n.startswith(name + "/") for n in names))
rel = lambda n: n[len(name) + 1:]
files = {rel(n) for n in names}
fuses = {f for f in files if f.startswith("fuses/")}; macros = {f for f in files if f.startswith("macros/")}
check("all Fuses packaged", len(fuses) == len([f for f in os.listdir(os.path.join(ROOT, "src/fuses")) if f.endswith(".lua")]) and "fuses/SMK2_Bloom.fuse" in fuses and "fuses/SMK2_PageCurl.fuse" in fuses)
nm = len([f for f in os.listdir(os.path.join(ROOT, "dist/templates")) if f.endswith(".setting")])
check("macros packaged", len(macros) == nm and nm >= 22)
check("no spikes in the release", not any("Spike" in f for f in files))
for need in ("install.py", "install.bat", "install.command", "README.txt", "NOTICE", "MANUAL.md", "VERSION", "SHA256SUMS"): check("contains " + need, need in files)
check("no junk metadata", not any(re.search(r"(^|/)(\._|\.DS_Store|Thumbs\.db|__MACOSX)", n) for n in names))
sums = dict(l.split("  ", 1)[::-1] for l in z.read(f"{name}/SHA256SUMS").decode().strip().splitlines())
check("SHA256SUMS covers every file but itself and matches", set(sums) == files - {"SHA256SUMS"} and all(hashlib.sha256(z.read(f"{name}/{f}")).hexdigest() == h for f, h in sums.items()))
sidecar = open(zp + ".sha256").read().split()[0]
check("zip sidecar checksum", sidecar == hashlib.sha256(open(zp, "rb").read()).hexdigest())
check("install.command is executable in the zip", (z.getinfo(f"{name}/install.command").external_attr >> 16) & 0o111 != 0)
check("install.bat uses CRLF, install.command LF", b"\r\n" in z.read(f"{name}/install.bat") and b"\r\n" not in z.read(f"{name}/install.command"))
check("no machine paths in macros", not any(b"CustomData" in z.read(f"{name}/{m}") and b"Path =" in z.read(f"{name}/{m}") for m in macros))
check("clean room: no 'Neo' in shipped Fuses/macros/manual/NOTICE-excluded text", not any(re.search(r"neo[ _-]?edit|\bneo_", z.read(f"{name}/{f}").decode("utf8", "ignore"), re.I) for f in files if f.startswith(("fuses/", "macros/")) or f == "MANUAL.md"))
check("no runtime require in shipped Fuses", not any(re.search(r"\b(require|dofile|loadfile)\s*\(", z.read(f"{name}/{f}").decode()) for f in fuses))

def run_installer(script, *args):
    r = subprocess.run([py, script, *args], capture_output=True, text=True); return r.returncode, r.stdout
with tempfile.TemporaryDirectory() as tmp:
    z.extractall(tmp); inst = os.path.join(tmp, name, "install.py"); tgt = os.path.join(tmp, "Fusion")
    rc, out = run_installer(inst, "--target", tgt, "--dry-run")
    check("dry run changes nothing", rc == 0 and "would install" in out and not os.path.exists(tgt))
    rc, out = run_installer(inst, "--target", tgt)
    fd, md = os.path.join(tgt, "Fuses", "SMK2"), os.path.join(tgt, "Macros", "SMK2")
    check("release install copies Fuses and macros", rc == 0 and len(os.listdir(fd)) == len(fuses) and len(os.listdir(md)) == nm)
    open(os.path.join(tgt, "Fuses", "Other.fuse"), "w").write("x")
    rc, out = run_installer(inst, "--target", tgt, "--uninstall", "--dry-run")
    check("uninstall dry run keeps files", rc == 0 and os.path.isdir(fd) and "would remove" in out)
    rc, out = run_installer(inst, "--target", tgt, "--uninstall")
    check("uninstall removes only SMK2 folders", rc == 0 and not os.path.exists(fd) and not os.path.exists(md) and os.path.exists(os.path.join(tgt, "Fuses", "Other.fuse")))
    rc, out = run_installer(inst, "--target", tgt, "--uninstall")
    check("uninstall twice is harmless", rc == 0 and "nothing to remove" in out)
    # from the checkout (builds first)
    tgt2 = os.path.join(tmp, "Fusion2")
    rc, out = run_installer(os.path.join(ROOT, "scripts/install.py"), "--target", tgt2)
    check("checkout install works", rc == 0 and os.path.isdir(os.path.join(tgt2, "Fuses", "SMK2")) and any(f.endswith(".fuse") for f in os.listdir(os.path.join(tgt2, "Fuses", "SMK2"))))
    check("spikes only with --include-spikes", not any("Spike" in f for f in os.listdir(os.path.join(tgt2, "Fuses", "SMK2"))))
print(f"release: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
