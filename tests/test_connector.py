"""SMK2_Connector: Fuse CPU stage with a mocked Fusion API, and kernel-vs-oracle pixel parity (real kernel compiled with gcc)."""
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

MOCK = r'''
CT_SourceTool = 3
TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE = 1, 2, 3
Width, Height, Depth = 1920, 1080, 8
function FuRegisterClass() end
function Pixel(t) return t end
function Image(a) local o={Width=a.IMG_Width, Height=a.IMG_Height}; function o:Fill() end; return o end
LAST = nil
function DVIPComputeNode(req, k, src, pname, pdef)
  assert(pdef:find("float pts%[192%]") and src:find("__KERNEL__"))
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
src = open(os.path.join(ROOT, "dist/fuses/SMK2_Connector.fuse")).read()
check("no runtime require", "require(" not in src and "dofile(" not in src)
lua.execute(MOCK); lua.execute(src); lua.execute("Create()")
run = lua.eval("""function(t, over, pre, fail) FAIL=fail; LAST=nil
  local req={Time=t, over=over}; function req:IsPreCalc() return pre end; Process(req); return LAST, req.out end""")
def frame(t, pre=False, fail=False, **o):
    over = {k: (lua.table_from(v) if isinstance(v, dict) else v) for k, v in o.items()}
    return run(t, lua.table_from(over), pre, fail)
b, out = frame(60)
check("default (curve): path between the two points, many samples", b.n > 20 and near(b.pts[1], 480, 0.5) and near(b.pts[2], 540, 0.5) and near(b.pts[2 * b.n - 1], 1440, 0.5))
check("default end marks: dot at start, arrow at end", b.kindA == 1 and b.kindB == 2)
check("settled: fully drawn; opacity 1", near(b.trim, 1, 1e-3) and b.opacity == 1)
b0, _ = frame(0, InEngine=0.0); check("frame 0: nothing drawn yet (draw-on)", near(b0.trim, 0, 1e-6))
check("last frame: un-drawn by the Out", frame(119, OutEngine=0.0)[0].trim < 0.02)
check("Out off: stays drawn", frame(119, HasOut=0.0)[0].trim > 0.99)
b, _ = frame(60, Mode=1.0); check("straight: 2 points, length = 960 px", b.n == 2 and near(b.total, 960, 0.5))
b, _ = frame(60, Mode=1.0, AMag=3.0); check("magnet Right on a 0.2-wide box: start moves to the edge + gap (480+192+6)", near(b.pts[1], 678, 0.5))
b, _ = frame(60, Mode=1.0, AMag=1.0); check("magnet Auto toward the other end exits the right edge", near(b.pts[1], 678, 0.5) and near(b.pts[2], 540, 0.5))
b, _ = frame(60, Mode=3.0, H1={"X": 0.4, "Y": 0.9}, H2={"X": 0.6, "Y": 0.1}); ys = [b.pts[2 * i] for i in range(1, b.n + 1)]
check("bezier handles bend the line (above and below the start height)", max(ys) > 540 + 60 and min(ys) < 540 - 60)
b, _ = frame(60, Mode=4.0, N=2.0, P1={"X": 0.4, "Y": 0.9}, P2={"X": 0.6, "Y": 0.1}); xs = [(b.pts[2 * i - 1], b.pts[2 * i]) for i in range(1, b.n + 1)]
check("spline passes through the editable points", min(math.hypot(x - 0.4 * 1920, y - 0.9 * 1080) for x, y in xs) < 1.0 and min(math.hypot(x - 0.6 * 1920, y - 0.1 * 1080) for x, y in xs) < 1.0)
check("spline with 0 points falls back to a curve", frame(60, Mode=4.0, N=0.0)[0].n > 20)
b, _ = frame(60, GradOn=0.0); check("gradient off: end colour = line colour", list(b.colB.values()) == list(b.colA.values()))
b, _ = frame(60, GradOn=1.0); check("gradient on: end colour differs", list(b.colB.values()) != list(b.colA.values()))
b, _ = frame(60, Dash=20.0, DGap=10.0); check("dash lengths in px@1920", near(b.dash, 20, 1e-6) and near(b.dgap, 10, 1e-6))
b, _ = frame(60, PulseOn=1.0); check("pulses on a drawn line", b.pul[4] > 0 or b.pul[8] > 0 or b.pul[12] > 0)
b, _ = frame(10, PulseOn=1.0, InEngine=0.0); check("no pulses while drawing on", b.pul[4] == 0 and b.pul[8] == 0)
check("no pulses when off", all(v == 0 for v in [frame(60)[0].pul[i] for i in range(1, 13)]))
b, _ = frame(60, Thick=10.0); check("thickness px@1920", near(b.thick, 10, 1e-6))
check("stagger delays the draw", frame(12, InEngine=0.0, Index=5.0, Stagger=0.1)[0].trim < frame(12, InEngine=0.0)[0].trim)
check("PreCalc skips the GPU", frame(10, pre=True)[0] is None)
check("GPU failure => transparent, no crash", frame(10, fail=True)[1] is not None)

# ---------------- kernel parity
cc = shutil.which("gcc") or shutil.which("cc")
if not cc: print("connector kernel parity: SKIPPED (no C compiler)")
else:
    fuse = open(os.path.join(ROOT, "dist/fuses/SMK2_Connector.fuse")).read()
    kernel = re.search(r"SMK2ConnSource = \[\[(.*?)\]\]", fuse, re.S).group(1)
    W, H = 128, 72
    random.seed(5)
    def scen():
        n = random.randint(2, 40)
        P = [(random.uniform(10, 118), random.uniform(8, 64)) for _ in range(n)]
        cum, tot = [0.0], 0.0
        for i in range(1, n): tot += math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); cum.append(tot)
        mk = lambda: random.choice([(0, [0] * 9), (1, [random.uniform(10, 118), random.uniform(8, 64), random.uniform(3, 9)] + [0] * 6),
              (2, [0, 0, 0] + [random.uniform(10, 118), random.uniform(8, 64), random.uniform(10, 118), random.uniform(8, 64), random.uniform(10, 118), random.uniform(8, 64)])])
        ka, ma = mk(); kb, mb = mk()
        pul = []
        for _ in range(3): pul += [random.uniform(10, 118), random.uniform(8, 64), random.uniform(2, 8), random.choice([0, 0.5, 1.0])]
        flat = [v for q in P for v in q] + [0.0] * (192 - 2 * n)
        return dict(n=n, kindA=ka, kindB=kb, total=tot, thick=random.uniform(1, 8), trim=random.choice([1, 0.7, 0.3, 1]), dash=random.choice([0, 0, 12]),
                    dgap=random.uniform(4, 10), gradOn=random.choice([0, 1]), opacity=random.choice([1, 0.6]), pts=flat, cum=cum + [tot] * (96 - n),
                    mkA=ma, mkB=mb, pul=pul, pulCol=[random.random() for _ in range(3)] + [random.choice([1, 0.8])],
                    colA=[random.random() for _ in range(3)] + [1], colB=[random.random() for _ in range(3)] + [random.choice([1, 0.7])])
    scens = [scen() for _ in range(8)]
    F = lambda v: (lambda s: s if ("." in s or "e" in s) else s + ".0")(f"{float(v):.9g}") + "f"
    A = lambda a: "{" + ",".join(F(v) for v in a) + "}"
    ci = lambda s: (f"{{ {{{W},{H}}}, {s['n']}, {s['kindA']}, {s['kindB']}, {F(s['total'])}, {F(s['thick'])}, {F(s['trim'])}, {F(s['dash'])}, {F(s['dgap'])}, "
                    f"{F(s['gradOn'])}, {F(s['opacity'])}, {A(s['pts'])}, {A(s['cum'])}, {A(s['mkA'])}, {A(s['mkB'])}, {A(s['pul'])}, {A(s['pulCol'])}, {A(s['colA'])}, {A(s['colB'])} }}")
    fields = re.search(r"SMK2ConnParams = \[\[(.*?)\]\]", fuse, re.S).group(1).replace("\n", " ")
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
typedef struct {{ {fields} }} SMK2ConnParams;
static int gx, gy;
{kernel}
int main() {{
  static float4 img[{W*H}];
  static SMK2ConnParams S[] = {{ {",".join(ci(s) for s in scens)} }};
  for (int i = 0; i < {len(scens)}; ++i) for (gy = 0; gy < {H}; ++gy) for (gx = 0; gx < {W}; ++gx) {{
    SMK2ConnKernel(&S[i], img);
    float4 c = img[gy*{W}+gx]; printf("%d %d %d %.6f %.6f %.6f %.6f\\n", i, gx, gy, c.x, c.y, c.z, c.w); }}
  return 0; }}
"""
    d = tempfile.mkdtemp(); open(d + "/k.c", "w").write(c)
    r = subprocess.run([cc, "-O1", "-o", d + "/k", d + "/k.c", "-lm"], capture_output=True, text=True)
    if r.returncode: print(r.stderr[:2000]); print("connector kernel parity: COMPILE FAILED"); sys.exit(1)
    out = subprocess.run([d + "/k"], capture_output=True, text=True).stdout.split("\n")
    core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
    mod = re.search(r"-- SMK2_MOD_BEGIN\n(.*?)-- SMK2_MOD_END", open(os.path.join(ROOT, "src/core/smk_connector.lua")).read(), re.S).group(1)
    lua2 = LuaRuntime(unpack_returned_tuples=True)
    smk = lua2.execute("local smk = (function()\n" + core + "\nend)()\n" + mod + "\nreturn smk")
    T = lua2.table_from
    def tab(s):
        mkt = lambda kind, a: T(dict(kind=kind, cx=a[0], cy=a[1], r=a[2], tri=T(a[3:9])))
        return T(dict(n=s["n"], pts=T(s["pts"]), cum=T(s["cum"]), total=s["total"], thick=s["thick"], trim=s["trim"], dash=s["dash"], dgap=s["dgap"],
                      gradOn=s["gradOn"], opacity=s["opacity"], mkA=mkt(s["kindA"], s["mkA"]), mkB=mkt(s["kindB"], s["mkB"]),
                      pul=T([T(s["pul"][i * 4:i * 4 + 4]) for i in range(3)]), pulCol=T(s["pulCol"]), colA=T(s["colA"]), colB=T(s["colB"])))
    TT = [tab(s) for s in scens]
    worst, n = 0.0, 0
    for line in out:
        if not line: continue
        i, x, y, *cv = line.split(); i, x, y = int(i), int(x), int(y); cv = list(map(float, cv))
        o = list(smk.connShade(TT[i], x, y)); n += 1
        worst = max(worst, max(abs(a - b) for a, b in zip(cv, o)))
    ok = n == len(scens) * W * H and worst < 3e-3
    check(f"connector kernel parity: {n} pixels, max |kernel - oracle| = {worst:.2e}", ok); print(f"connector kernel parity: {n} pixels, max |kernel - oracle| = {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
print(f"connector: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
