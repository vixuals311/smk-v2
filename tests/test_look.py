"""SMK2_Look: reference pixel function, Fuse CPU stage (mock), and kernel-vs-oracle parity (real kernel compiled with gcc, nearest-texel source shim)."""
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

core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
mod = re.search(r"-- SMK2_MOD_BEGIN\n(.*?)-- SMK2_MOD_END", open(os.path.join(ROOT, "src/core/smk_look.lua")).read(), re.S).group(1)
lua = LuaRuntime(unpack_returned_tuples=True)
smk = lua.execute("local smk = (function()\n" + core + "\nend)()\n" + mod + "\nreturn smk")
T = lua.table_from
W, H = 128, 72

def make_img(kind="rect", color=(1.0, 1.0, 1.0)):
    img = [[(0.0, 0.0, 0.0, 0.0)] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if kind == "rect" and 44 <= x < 84 and 26 <= y < 46: img[y][x] = (color[0], color[1], color[2], 1.0)
    return img
def src_fn(img):
    return lua.eval("function(img, W, H) return function(sx, sy) local ix = math.min(math.max(math.floor(sx), 0), W - 1) local iy = math.min(math.max(math.floor(sy), 0), H - 1) local p = img[iy + 1][ix + 1] return p[1], p[2], p[3], p[4] end end")(
        T([T([T(list(p)) for p in row]) for row in img]), W, H)
def P(**k):
    d = dict(size=[W, H], glowOn=0, glowSamples=48, glowSrc=0, glowBehind=0, outOn=0, shineOn=0, gradOn=0, glowR=20, glowI=1, glowThr=0.6, outW=4,
             shC=1, shS=0, shPos=0, shW=6, shSoft=4, shI=1, gC=1, gS=0, gExt=64, gAmt=1, opacity=1,
             glowCol=[0.2, 0.4, 1, 1], outCol=[1, 0, 0, 1], shCol=[1, 1, 1, 1], gA=[1, 0, 0, 1], gB=[0, 0, 1, 1])
    d.update(k); t = lua.table()
    for key, v in d.items(): t[key] = T(v) if isinstance(v, list) else v
    return t
rect = src_fn(make_img()); px = lambda p, x, y, s=rect: tuple(smk.lookShade(p, x, y, s))
check("no effects: output = source", px(P(), 60, 36) == (1.0, 1.0, 1.0, 1.0) and px(P(), 5, 5)[3] == 0)
# glow
g = P(glowOn=1)
check("glow (alpha): halo outside the object, none far away, strongest at the edge", 0.02 < px(g, 40, 36)[3] < 1 and px(g, 4, 4)[3] == 0 and px(g, 43, 36)[3] > px(g, 36, 36)[3] > px(g, 28, 36)[3])
check("glow additive brightens the object", px(g, 60, 36)[0] > 1.0 or px(g, 60, 36)[2] >= 1.0)
gb = P(glowOn=1, glowBehind=1); check("glow behind leaves the object untouched", px(gb, 60, 36) == (1.0, 1.0, 1.0, 1.0) and px(gb, 40, 36)[3] > 0.02)
check("glow colour tint (blue-ish halo)", px(g, 40, 36)[2] > px(g, 40, 36)[0])
dark = src_fn(make_img(color=(0.1, 0.1, 0.1))); bright = src_fn(make_img(color=(1, 1, 1)))
gl = P(glowOn=1, glowSrc=1, glowThr=0.5)
check("brightness glow: bright object glows, dark one does not", px(gl, 40, 36, bright)[3] > 0.02 and px(gl, 40, 36, dark)[3] < 1e-6)
check("glow intensity scales the halo", px(P(glowOn=1, glowI=2), 40, 36)[3] > px(P(glowOn=1, glowI=0.5), 40, 36)[3])
# outline
o = P(outOn=1, outW=6)
check("outline ring outside the object only", px(o, 41, 36)[0] > 0.9 and px(o, 41, 36)[3] > 0.9 and px(o, 20, 36)[3] < 1e-6 and px(o, 60, 36) == (1.0, 1.0, 1.0, 1.0))
# shine
sh = P(shineOn=1, shC=1, shS=0, shPos=0, shW=6, shSoft=4, shI=1, shCol=[1, 0.5, 0, 1])
check("shine band adds light inside the band, on the object only", px(sh, 64, 36)[1] > 1.2 * 0.9 and px(sh, 50, 36) == (1.0, 1.0, 1.0, 1.0) and px(sh, 64, 10)[3] == 0)
check("shine position moves the band", px(P(shineOn=1, shPos=-16, shCol=[1, 0.5, 0, 1]), 48, 36)[0] > 1.0 and px(P(shineOn=1, shPos=-16), 64, 36)[0] == 1.0)
# gradient
gr = P(gradOn=1, gC=1, gS=0, gExt=64); l_, r_ = px(gr, 46, 36), px(gr, 82, 36)
check("gradient overlay: left reddish, right bluish, alpha unchanged, outside untouched", l_[0] > l_[2] and r_[2] > r_[0] and near(l_[3], 1) and px(gr, 5, 5)[3] == 0)
check("gradient amount 0 = no change", px(P(gradOn=1, gAmt=0), 60, 36) == (1.0, 1.0, 1.0, 1.0))
check("opacity multiplies all channels", near(px(P(opacity=0.5), 60, 36)[3], 0.5) and near(px(P(opacity=0.5), 60, 36)[0], 0.5))

# ---------------- Fuse CPU stage
MOCK = r'''
CT_Tool = 2
TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE = 1, 2, 3
function FuRegisterClass() end
function Pixel(t) return t end
IMG = {Width=1920, Height=1080}
function Image(a) local o={Width=a.IMG_Like and a.IMG_Like.Width, Height=a.IMG_Like and a.IMG_Like.Height}; function o:Fill() end; return o end
LAST = nil
function DVIPComputeNode(req, k, src, pname, pdef)
  assert(pdef:find("float glowCol%[4%]") and src:find("__KERNEL__"))
  local n = {block={}}
  function n:GetParamBlock() return self.block end
  function n:SetParamBlock(b) LAST = b end
  function n:AddSampler() end; function n:AddInput() end; function n:AddOutput() end
  function n:RunSession() return not FAIL end
  return n
end
function self_input(t, id)
  local o = {id=id, t=t}
  function o:GetValue(req)
    if self.id == "Image" then if NOIMG then return nil end return IMG end
    return {Value = (req.over and req.over[self.id]) or self.t.INP_Default}
  end
  return o
end
self = {Comp={RenderStart=0, RenderEnd=119}}
function self.Comp:GetPrefs() return 24 end
function self:AddInput(name, id, t) return self_input(t, id) end
function self:AddOutput(name, id, t) local o={id=id}; function o:Set(req,v) req.out=v end; return o end
'''
lua.execute(MOCK)
src = open(os.path.join(ROOT, "dist/fuses/SMK2_Look.fuse")).read()
check("no runtime require", "require(" not in src and "dofile(" not in src)
lua.execute(src); lua.execute("Create()")
run = lua.eval("""function(t, over, pre, fail, noimg) FAIL=fail; NOIMG=noimg; LAST=nil
  local req={Time=t, over=over}; function req:IsPreCalc() return pre end; Process(req); return LAST, req.out end""")
def frame(t, pre=False, fail=False, noimg=False, **o): return run(t, T(o), pre, fail, noimg)
b, out = frame(12); check("defaults: glow on, 48 samples, px@1920 radius", b.glowOn == 1 and b.glowSamples == 48 and near(b.glowR, 40, 1e-6) and b.outOn == 0 and b.shineOn == 0)
check("glow quality maps to sample counts", [frame(12, GlowQ=float(i))[0].glowSamples for i in range(4)] == [24, 48, 96, 160])
check("sizes are px@1920 (outline 6 -> 6; at 3840 would double)", near(frame(12, OutW=6.0)[0].outW, 6, 1e-6))
# shine auto sweep: before the delay off-screen, half time centred, after the sweep off-screen
ext = abs(math.cos(math.radians(25))) * 960 + abs(math.sin(math.radians(25))) * 540
b_pre, _ = frame(0, ShineOn=1.0, ShineDelay=0.5, ShineDur=1.0); b_mid, _ = frame(24, ShineOn=1.0, ShineDelay=0.5, ShineDur=1.0); b_post, _ = frame(int(2.5 * 24), ShineOn=1.0, ShineDelay=0.5, ShineDur=1.0)
check("shine sweep: off-screen before the delay", b_pre.shPos > ext * 2)
check("shine sweep: centred at half time (symmetric ease)", abs(b_mid.shPos) < 0.01 * ext)
check("shine sweep: off-screen after the sweep", b_post.shPos > ext * 2)
b_a, _ = frame(16, ShineOn=1.0, ShineDelay=0.5, ShineDur=1.0); b_b, _ = frame(30, ShineOn=1.0, ShineDelay=0.5, ShineDur=1.0)
check("shine sweeps left -> right along its axis (position increases)", b_b.shPos > b_a.shPos)
b_r1, _ = frame(24, ShineOn=1.0, ShineDelay=0.5, ShineDur=1.0, ShineRepeat=2.0); b_r2, _ = frame(24 + 48, ShineOn=1.0, ShineDelay=0.5, ShineDur=1.0, ShineRepeat=2.0)
check("repeat: second sweep passes the centre again", abs(b_r1.shPos) < 0.01 * ext and abs(b_r2.shPos) < 0.01 * ext)
check("manual shine position scales with the frame", near(frame(12, ShineOn=1.0, ShineAuto=0.0, ShinePos=0.0)[0].shPos, 0, 1e-6))
check("PreCalc skips the GPU", frame(10, pre=True)[0] is None)
check("GPU failure passes the input through", frame(10, fail=True)[1] is not None)
check("no input image: nil output", frame(10, noimg=True)[1] is None)

# ---------------- kernel parity
cc = shutil.which("gcc") or shutil.which("cc")
if not cc: print("look kernel parity: SKIPPED (no C compiler)")
else:
    fuse = open(os.path.join(ROOT, "dist/fuses/SMK2_Look.fuse")).read()
    kernel = re.search(r"SMK2LookSource = \[\[(.*?)\]\]", fuse, re.S).group(1)
    random.seed(21)
    img = [[(0.0, 0.0, 0.0, 0.0)] * W for _ in range(H)]
    for _ in range(5):                                           # random premultiplied soft blobs
        cx, cy, rx, ry = random.uniform(20, 108), random.uniform(15, 57), random.uniform(6, 22), random.uniform(5, 14)
        cr, cg, cb, ca = random.random(), random.random(), random.random(), random.choice([1.0, 0.8, 0.5])
        for y in range(H):
            for x in range(W):
                d = math.hypot((x + .5 - cx) / rx, (y + .5 - cy) / ry)
                if d < 1:
                    a = ca * min(1.0, (1 - d) * 4)
                    o = img[y][x]; k = 1 - a
                    img[y][x] = (cr * a + o[0] * k, cg * a + o[1] * k, cb * a + o[2] * k, a + o[3] * k)
    def scen():
        gq = random.choice([24, 48, 96])
        ang = random.uniform(0, 6.28); ga = random.uniform(0, 6.28)
        return dict(glowOn=random.choice([0, 1, 1]), glowSamples=gq, glowSrc=random.choice([0, 1]), glowBehind=random.choice([0, 1]), outOn=random.choice([0, 1]),
                    shineOn=random.choice([0, 1]), gradOn=random.choice([0, 1]), glowR=random.uniform(6, 30), glowI=random.uniform(0.5, 2), glowThr=random.uniform(0.2, 0.7),
                    outW=random.uniform(1, 8), shC=math.cos(ang), shS=math.sin(ang), shPos=random.uniform(-60, 60), shW=random.uniform(2, 14), shSoft=random.uniform(0, 10),
                    shI=random.uniform(0.3, 1.5), gC=math.cos(ga), gS=math.sin(ga), gExt=abs(math.cos(ga)) * 64 + abs(math.sin(ga)) * 36 + 1e-4, gAmt=random.uniform(0.3, 1),
                    opacity=random.choice([1, 0.7]), glowCol=[random.random() for _ in range(3)] + [random.choice([1, 0.8])], outCol=[random.random() for _ in range(3)] + [1],
                    shCol=[random.random() for _ in range(3)] + [1], gA=[random.random() for _ in range(3)] + [1], gB=[random.random() for _ in range(3)] + [random.choice([1, 0.6])])
    scens = [scen() for _ in range(6)]
    F = lambda v: (lambda s: s if ("." in s or "e" in s) else s + ".0")(f"{float(v):.9g}") + "f"
    A = lambda a: "{" + ",".join(F(v) for v in a) + "}"
    order = ["glowOn", "glowSamples", "glowSrc", "glowBehind", "outOn", "shineOn", "gradOn"]
    forder = ["glowR", "glowI", "glowThr", "outW", "shC", "shS", "shPos", "shW", "shSoft", "shI", "gC", "gS", "gExt", "gAmt", "opacity"]
    ci = lambda s: ("{ {%d,%d}, " % (W, H) + ", ".join(str(s[k]) for k in order) + ", " + ", ".join(F(s[k]) for k in forder) + ", " +
                    ", ".join(A(s[k]) for k in ["glowCol", "outCol", "shCol", "gA", "gB"]) + " }")
    fields = re.search(r"SMK2LookParams = \[\[(.*?)\]\]", fuse, re.S).group(1).replace("\n", " ")
    flat_img = ",".join(F(v) for row in img for p in row for v in p)
    c = f"""
#include <math.h>
#include <stdio.h>
typedef struct {{ float x,y,z,w; }} float4;
static float4 make_float4(float x,float y,float z,float w){{float4 r={{x,y,z,w}};return r;}}
#define __KERNEL__ static
#define __CONSTANTREF__ const
#define __TEXTURE2D__ const float*
#define __TEXTURE2D_WRITE__ float4*
#define DEFINE_KERNEL_ITERATORS_XY(x,y) int x=gx, y=gy
#define _tex2DVec4Write(dst,x,y,c) (dst)[(y)*{W}+(x)] = (c)
static float4 _tex2DVecN(const float* s, float u, float v, int n) {{
  int ix = (int)floorf(u * {W}.0f), iy = (int)floorf(v * {H}.0f);
  if (ix < 0) ix = 0; if (ix > {W-1}) ix = {W-1}; if (iy < 0) iy = 0; if (iy > {H-1}) iy = {H-1};
  const float* q = s + 4 * (iy * {W} + ix); return make_float4(q[0], q[1], q[2], q[3]); }}
typedef struct {{ {fields} }} SMK2LookParams;
static int gx, gy;
static const float IMG[] = {{ {flat_img} }};
{kernel}
int main() {{
  static float4 out[{W*H}];
  static SMK2LookParams S[] = {{ {",".join(ci(s) for s in scens)} }};
  for (int i = 0; i < {len(scens)}; ++i) for (gy = 0; gy < {H}; ++gy) for (gx = 0; gx < {W}; ++gx) {{
    SMK2LookKernel(&S[i], IMG, out);
    float4 c = out[gy*{W}+gx]; printf("%d %d %d %.6f %.6f %.6f %.6f\\n", i, gx, gy, c.x, c.y, c.z, c.w); }}
  return 0; }}
"""
    d = tempfile.mkdtemp(); open(d + "/k.c", "w").write(c)
    r = subprocess.run([cc, "-O1", "-o", d + "/k", d + "/k.c", "-lm"], capture_output=True, text=True)
    if r.returncode: print(r.stderr[:2500]); print("look kernel parity: COMPILE FAILED"); sys.exit(1)
    out = subprocess.run([d + "/k"], capture_output=True, text=True).stdout.split("\n")
    sfn = src_fn(img)
    def tab(s):
        t = lua.table(); t.size = T([W, H])
        for k, v in s.items(): t[k] = T(v) if isinstance(v, list) else v
        return t
    TT = [tab(s) for s in scens]
    bad, n, worst = 0, 0, 0.0
    for line in out:
        if not line: continue
        i, x, y, *cv = line.split(); i, x, y = int(i), int(x), int(y); cv = list(map(float, cv))
        o = list(smk.lookShade(TT[i], x, y, sfn)); n += 1
        df = max(abs(a - b) for a, b in zip(cv, o)); worst = max(worst, df)
        if df > 3e-3: bad += 1
    frac = bad / max(n, 1)
    ok = n == len(scens) * W * H and frac < 0.003
    check(f"look kernel parity: {n} pixels, {bad} differ by > 3e-3 ({frac:.4%}), max {worst:.2e}", ok)
    print(f"look kernel parity: {n} pixels, {bad} differ by > 3e-3 ({frac:.4%}), max diff {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
print(f"look: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
