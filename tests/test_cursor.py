"""SMK2_Cursor: Fuse CPU stage with a mocked Fusion API, and kernel-vs-oracle pixel parity (real kernel compiled with gcc)."""
import math, os, random, re, shutil, subprocess, sys, tempfile
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
def near(a, b, e=1e-3): return abs(a - b) <= e

# ---------------- Fuse CPU stage
MOCK = r'''
CT_SourceTool = 3
TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE = 1, 2, 3
Width, Height, Depth = 1920, 1080, 8
function FuRegisterClass() end
function Pixel(t) return t end
function Image(a) local o={Width=a.IMG_Width, Height=a.IMG_Height}; function o:Fill() end; return o end
LAST = nil
function DVIPComputeNode(req, k, src, pname, pdef)
  assert(pdef:find("float rip%[12%]") and src:find("__KERNEL__"))
  local n = {block={}}
  function n:GetParamBlock() return self.block end
  function n:SetParamBlock(b) LAST = b end
  function n:AddSampler() end; function n:AddOutput() end
  function n:RunSession() return not FAIL end
  return n
end
function self_input(t, id)
  local o = {id=id, t=t}
  function o:GetValue(req)
    local ov = req.over and req.over[self.id]
    if self.t.LINKID_DataType == "Point" then return ov or {X=self.t.INP_DefaultX, Y=self.t.INP_DefaultY} end
    return {Value = ov or self.t.INP_Default}
  end
  return o
end
self = {Comp={RenderStart=0, RenderEnd=119}}
function self.Comp:GetPrefs() return 24 end
function self:AddInput(name, id, t) return self_input(t, id) end
function self:AddOutput(name, id, t) local o={id=id}; function o:Set(req,v) req.out=v end; return o end
'''
lua = LuaRuntime(unpack_returned_tuples=True)
src = open(os.path.join(ROOT, "dist/fuses/SMK2_Cursor.fuse")).read()
check("no runtime require", "require(" not in src and "dofile(" not in src)
lua.execute(MOCK); lua.execute(src); lua.execute("Create()")
run = lua.eval("""function(t, over, pre, fail) FAIL=fail; LAST=nil
  local req={Time=t, over=over}; function req:IsPreCalc() return pre end; Process(req); return LAST, req.out end""")
def frame(t, pre=False, fail=False, **o): return run(t, lua.table_from(o), pre, fail)
b, out = frame(0); check("frame 0: invisible", b is not None and b.opacity < 1e-6)
b, _ = frame(14); check("t=0.58 s: first waypoint, visible", near(b.tip[1], 0.25 * 1920, 0.5) and near(b.tip[2], 0.65 * 1080, 0.5) and b.opacity > 0.9)
b, _ = frame(int(3.0 * 24)); check("later: at/after waypoint 2 positions are pixels", b.tip[1] > 0.4 * 1920)
b, _ = frame(72, ); check("size in px = frac*width", near(b.S, 0.03 * 1920, 0.5))
# arrival at waypoint 2: startDelay .4 + hold .3 + move 1.2 = 1.9 s -> frame 45.6; click delay .12 + press 0.18 -> press dip at ~2.1 s (frame 50)
b, _ = frame(50); check("press dip while clicking", b.press < 0.95)
b, _ = frame(54); check("ripple active after click (alpha > 0, radius in px)", b.rip[4] > 0 and b.rip[3] > 0 and near(b.rip[1], 0.7 * 1920, 0.5))
check("the last frame fades out", frame(119)[0].opacity < 1e-6)
b, _ = frame(60, N=2.0); check("waypoint count limits the path (2 points)", b.tip[1] > 0.5 * 1920)
check("PreCalc skips the GPU", frame(10, pre=True)[0] is None)
check("GPU failure => transparent, no crash", frame(10, fail=True)[1] is not None)
b, _ = frame(60, SX=20.0); check("px@1920 units scale with resolution (shadow x)", near(b.shadowOff[1], 20, 1e-3))
b, _ = frame(60, SY=10.0); check("shadow y 'down' is negative (y up)", b.shadowOff[2] < 0)

# ---------------- kernel parity
cc = shutil.which("gcc") or shutil.which("cc")
if not cc: print("cursor kernel parity: SKIPPED (no C compiler)")
else:
    fuse = open(os.path.join(ROOT, "dist/fuses/SMK2_Cursor.fuse")).read()
    kernel = re.search(r"SMK2CursorSource = \[\[(.*?)\]\]", fuse, re.S).group(1)
    W, H = 128, 72
    random.seed(11)
    def scen():
        rp = []
        for _ in range(3):
            rp += [random.uniform(20, 108), random.uniform(15, 57), random.uniform(5, 30), random.choice([0, 0, 0.4, 0.9])]
        return dict(tip=(random.uniform(20, 100), random.uniform(25, 60)), S=random.uniform(20, 55), press=random.choice([1, 1, 0.85, 0.7]),
                    bw=random.choice([0, 2, 3]), shadowOff=(random.uniform(-4, 4), random.uniform(-6, 2)), shadowBlur=random.uniform(0, 8),
                    ripThick=random.uniform(1, 6), opacity=random.choice([1, 0.6]), rip=rp,
                    fillCol=[random.random() for _ in range(3)] + [random.choice([1, 0.8])], borderCol=[random.random() for _ in range(3)] + [1],
                    shadowCol=[random.random() for _ in range(3)] + [random.choice([0, 0.5])], ripCol=[random.random() for _ in range(3)] + [random.choice([1, 0.7])])
    scens = [scen() for _ in range(8)]
    F = lambda v: (lambda s: s if ("." in s or "e" in s) else s + ".0")(f"{float(v):.9g}") + "f"
    A = lambda a: "{" + ",".join(F(v) for v in a) + "}"
    ci = lambda s: (f"{{ {{{W},{H}}}, {A(s['tip'])}, {F(s['S'])}, {F(s['press'])}, {F(s['bw'])}, {A(s['shadowOff'])}, {F(s['shadowBlur'])}, "
                    f"{F(s['ripThick'])}, {F(s['opacity'])}, {A(s['rip'])}, {A(s['fillCol'])}, {A(s['borderCol'])}, {A(s['shadowCol'])}, {A(s['ripCol'])} }}")
    fields = re.search(r"SMK2CursorParams = \[\[(.*?)\]\]", fuse, re.S).group(1).replace("\n", " ")
    c = f"""
#include <math.h>
#include <stdio.h>
typedef struct {{ float x,y,z,w; }} float4;
static float4 make_float4(float x,float y,float z,float w){{float4 r={{x,y,z,w}};return r;}}
#define __KERNEL__ static
#define __CONSTANTREF__ const
#define __TEXTURE2D_WRITE__ float4*
#define DEFINE_KERNEL_ITERATORS_XY(x,y) int x=gx, y=gy
#define _tex2DVec4Write(dst,x,y,c) (dst)[(y)*{W}+(x)] = (c)
typedef struct {{ {fields} }} SMK2CursorParams;
static int gx, gy;
{kernel}
int main() {{
  static float4 img[{W*H}];
  SMK2CursorParams S[] = {{ {",".join(ci(s) for s in scens)} }};
  for (int i = 0; i < {len(scens)}; ++i) for (gy = 0; gy < {H}; ++gy) for (gx = 0; gx < {W}; ++gx) {{
    SMK2CursorKernel(&S[i], img);
    float4 c = img[gy*{W}+gx]; printf("%d %d %d %.6f %.6f %.6f %.6f\\n", i, gx, gy, c.x, c.y, c.z, c.w); }}
  return 0; }}
"""
    d = tempfile.mkdtemp(); open(d + "/k.c", "w").write(c)
    r = subprocess.run([cc, "-O1", "-o", d + "/k", d + "/k.c", "-lm"], capture_output=True, text=True)
    if r.returncode: print(r.stderr[:2000]); print("cursor kernel parity: COMPILE FAILED"); sys.exit(1)
    out = subprocess.run([d + "/k"], capture_output=True, text=True).stdout.split("\n")
    core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
    mod = re.search(r"-- SMK2_MOD_BEGIN\n(.*?)-- SMK2_MOD_END", open(os.path.join(ROOT, "src/core/smk_cursor.lua")).read(), re.S).group(1)
    lua2 = LuaRuntime(unpack_returned_tuples=True)
    smk = lua2.execute("local smk = (function()\n" + core + "\nend)()\n" + mod + "\nreturn smk")
    T = lua2.table_from
    def tab(s):
        rip = T([T(s["rip"][i * 4:i * 4 + 4]) for i in range(3)])
        return T(dict(tip=T(list(s["tip"])), S=s["S"], press=s["press"], bw=s["bw"], shadowOff=T(list(s["shadowOff"])), shadowBlur=s["shadowBlur"],
                      ripThick=s["ripThick"], opacity=s["opacity"], rip=rip, fillCol=T(s["fillCol"]), borderCol=T(s["borderCol"]),
                      shadowCol=T(s["shadowCol"]), ripCol=T(s["ripCol"])))
    TT = [tab(s) for s in scens]
    worst, n = 0.0, 0
    for line in out:
        if not line: continue
        i, x, y, *cv = line.split(); i, x, y = int(i), int(x), int(y); cv = list(map(float, cv))
        o = list(smk.cursorShade(TT[i], x, y)); n += 1
        worst = max(worst, max(abs(a - b) for a, b in zip(cv, o)))
    ok = n == len(scens) * W * H and worst < 3e-3
    check(f"cursor kernel parity: {n} pixels, max |kernel - oracle| = {worst:.2e}", ok); print(f"cursor kernel parity: {n} pixels, max |kernel - oracle| = {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
print(f"cursor: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
