"""SMK2_Shape: oracle (smk.shade) pixel checks + Fuse CPU prep/dispatch with a mocked Fusion API."""
import math, os, re, subprocess, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
def near(a, b, e=1e-3): return abs(a - b) <= e

# ---------- oracle ----------
lua = LuaRuntime(unpack_returned_tuples=True)
core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
mod = re.search(r"-- SMK2_MOD_BEGIN\n(.*?)-- SMK2_MOD_END", open(os.path.join(ROOT, "src/core/smk_shape.lua")).read(), re.S).group(1)
smk = lua.execute("local smk = (function()\n" + core + "\nend)()\n" + mod + "\nreturn smk")
def P(**k):
    d = dict(size=(200, 100), shape=0, fillMode=0, borderPos=0, center=(100, 50), half=(60, 30), radius=0, thick=10, bw=0,
             cosA=1, sinA=0, gradC=1, gradS=0, trim=1, trimStart=0, shadowOff=(0, 0), shadowBlur=4, opacity=1,
             fillA=(1, 0, 0, 1), fillB=(0, 0, 1, 1), borderCol=(0, 1, 0, 1), shadowCol=(0, 0, 0, 0), trackCol=(0, 0, 1, 0), dotR=0)
    d.update(k)
    t = lua.table()
    for key, v in d.items(): t[key] = lua.table_from([*v]) if isinstance(v, tuple) else v
    return t
def px(p, x, y): return tuple(smk.shade(p, x, y))
c = px(P(), 100, 50); check("rect centre solid red", near(c[0], 1) and near(c[3], 1))
check("outside transparent", px(P(), 5, 5)[3] == 0)
# edge exactly at x=160 -> pixel 159 (centre 159.5) d=-0.5 -> cov 1, pixel 160 (160.5) d=0.5 -> 0
check("edge pixel coverage", near(px(P(), 159, 50)[3], 1) and near(px(P(), 160, 50)[3], 0))
r = P(radius=30, half=(60, 30)); check("pill corner is cut", px(r, 41, 21)[3] < 0.5 and px(r, 100, 50)[3] == 1)
check("circle via ellipse", px(P(shape=1, half=(30, 30)), 100, 50)[3] == 1 and px(P(shape=1, half=(30, 30)), 100 + 40, 50)[3] == 0)
# border
b = P(bw=4, borderPos=0); check("inside border colour near edge", px(b, 157, 50)[1] > 0.9 and px(b, 100, 50)[0] > 0.9)
bo = P(bw=4, borderPos=2); check("outside border beyond edge", px(bo, 162, 50)[1] > 0.9 and px(bo, 158, 50)[0] > 0.9)
bc = P(bw=4, borderPos=1); check("centre border straddles", px(bc, 158, 50)[1] > 0.9 and px(bc, 161, 50)[1] > 0.9)
# gradient
gp = P(fillMode=1, fillA=(0, 0, 0, 1), fillB=(1, 1, 1, 1), gradC=1, gradS=0)
check("linear gradient left dark right bright", px(gp, 45, 50)[0] < 0.1 and px(gp, 155, 50)[0] > 0.9 and near(px(gp, 100, 50)[0], 0.5, 0.02))
check("radial gradient centre = A", px(P(fillMode=2, fillA=(0,0,0,1), fillB=(1,1,1,1)), 100, 50)[0] < 0.02)
# shadow
sp = P(shadowCol=(0, 0, 0, 0.5), shadowOff=(0, -10), shadowBlur=6)
check("shadow visible below shape, none far away", px(sp, 100, 15)[3] > 0.1 and px(sp, 100, 98)[3] < 0.01)
check("shadow under fill (fill wins)", near(px(sp, 100, 50)[0], 1))
# opacity & premult
o = px(P(opacity=0.5), 100, 50); check("opacity premultiplied", near(o[0], 0.5) and near(o[3], 0.5))
ha = px(P(fillA=(1, 0, 0, 0.5)), 100, 50); check("straight alpha colour premultiplied", near(ha[0], 0.5) and near(ha[3], 0.5))
# rotation by 90: wide rect becomes tall
rp = P(cosA=0, sinA=1, half=(60, 20)); check("rotated rect is tall", px(rp, 100, 100 - 10)[3] == 1 and px(rp, 100 + 40, 50)[3] == 0)
# ring + sweep: 0 at top, clockwise
ring = P(shape=2, half=(40, 40), thick=10, center=(100, 50)); check("ring wall filled, hole empty", px(ring, 100, 50 + 35)[3] > 0.9 and px(ring, 100, 50)[3] == 0)
half = P(shape=2, half=(40, 40), thick=10, trim=0.5)
check("sweep 0.5 keeps right half only", px(half, 100 + 35, 50)[3] > 0.9 and px(half, 100 - 35, 50)[3] < 0.05)
check("sweep starts at top", px(half, 100 + 2, 50 + 35)[3] > 0.9)
q = P(shape=2, half=(40, 40), thick=10, trim=0.25); check("quarter = top-right only", px(q, 100 + 25, 50 + 25)[3] > 0.9 and px(q, 100 + 25, 50 - 25)[3] < 0.05)
# track (progress remainder)
tk = P(shape=2, half=(40, 40), thick=10, trim=0.5, trackCol=(0, 0, 1, 1))
check("track fills the trimmed-away half", px(tk, 100 - 35, 50)[2] > 0.9 and px(tk, 100 - 35, 50)[0] < 0.05)
check("fill stays on the swept half", px(tk, 100 + 35, 50)[0] > 0.9)
check("no track when alpha 0", px(P(shape=2, half=(40, 40), thick=10, trim=0.5), 100 - 35, 50)[3] < 0.05)
check("no track on untrimmed shape", px(P(trackCol=(0, 0, 1, 1)), 100, 50)[0] > 0.9)
# line + draw-on
ln = P(shape=3, half=(60, 0), thick=8)
check("line capsule body", px(ln, 100, 50)[3] > 0.9 and px(ln, 100, 60)[3] == 0)
lt = P(shape=3, half=(60, 0), thick=8, trim=0.5)
check("line trim draws left half", px(lt, 70, 50)[3] > 0.9 and px(lt, 130, 50)[3] < 0.05)
# end dot at the drawing front
dl = P(shape=3, half=(60, 0), thick=6, trim=0.5, dotR=9)
check("end dot sits at the drawing front", px(dl, 100, 50)[3] > 0.95 and px(dl, 100, 50 + 7)[3] > 0.5)
check("no dot beyond the front / no dot when radius 0", px(dl, 130, 57)[3] < 0.05 and px(P(shape=3, half=(60, 0), thick=6, trim=0.5), 100, 57)[3] < 0.05)
check("full-length line ends with the dot at the tip", px(P(shape=3, half=(60, 0), thick=6, dotR=9), 160, 57)[3] > 0.5)
# animation transforms already pre-applied: scale smaller => less coverage
small = P(half=(30, 15)); check("scaled-down shape", px(small, 100 + 45, 50)[3] == 0 and px(small, 100, 50)[3] == 1)

# ---------- Fuse CPU stage ----------
MOCK = r'''
CT_SourceTool = 3
TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE = 1, 2, 3
Width, Height, Depth = 1920, 1080, 8
function FuRegisterClass() end
function Number(v) return v end
function Pixel(t) return t end
function Image(a) local o={Width=a.IMG_Width, Height=a.IMG_Height}; function o:Fill() end; return o end
LAST = nil
function DVIPComputeNode(req, k, src, pname, pdef)
  assert(pdef:find("float shadowCol%[4%]") or pdef:find("shadowCol"), "params"); assert(src:find("__KERNEL__"), "kernel")
  local n = {block={}}
  function n:GetParamBlock() return self.block end
  function n:SetParamBlock(b) LAST = b end
  function n:AddSampler() end; function n:AddOutput() end
  function n:RunSession() return not FAIL end
  return n
end
function make_in(def, t) local o={default=def, t=t}; function o:GetValue(req) local ov=req.over and req.over[self.id]; if self.t and self.t.LINKID_DataType=="Point" then return ov or {X=self.t.INP_DefaultX, Y=self.t.INP_DefaultY} end return {Value=ov or self.default} end return o end
self = {Comp={RenderStart=0, RenderEnd=119}}
function self.Comp:GetPrefs() return 24 end
function self:AddInput(name, id, t) local o=make_in(t.INP_Default, t); o.id=id; return o end
function self:AddOutput(name, id, t) local o={id=id}; function o:Set(req,v) req.out=v end; return o end
'''
src = open(os.path.join(ROOT, "dist/fuses/SMK2_Shape.fuse")).read()
check("no runtime require", "require(" not in src and "dofile(" not in src)
lua.execute(MOCK); lua.execute(src); lua.execute("Create()")
run = lua.eval("""function(t, over, pre, fail) FAIL=fail; LAST=nil
  local req={Time=t, over=over}; function req:IsPreCalc() return pre end; Process(req); return LAST, req.out end""")
def frame(t, pre=False, fail=False, **o): return run(t, lua.table_from(o), pre, fail)
b, out = frame(60)
check("hold: centred, full size", near(b.center[1], 960, 0.5) and near(b.center[2], 540, 0.5) and near(b.half[1], 0.15 * 1920, 0.5) and near(b.opacity, 1, 1e-3))
check("hold: pill radius", near(b.radius, 0.15 * min(b.half[1], b.half[2]) * 2, 0.5))
b0, _ = frame(0, InEngine=0.0); check("frame 0 invisible, slid left", b0.opacity < 1e-6 and b0.center[1] < 960 - 100)
check("px@1920 units scale with resolution", near(b.bw, 0, 1e-9) and near(frame(60, BW=10.0)[0].bw, 10, 1e-3))
check("ring param remap", frame(60, Shape=2.0)[0].half[1] == frame(60, Shape=2.0)[0].half[2])
check("shadow offset y down is negative (y up)", frame(60, SY=10.0)[0].shadowOff[2] < 0)
check("scale about own centre (half shrinks)", frame(0, InEngine=0.0, InScale=0.5, InSlideDist=0.0)[0].half[1] < frame(60)[0].half[1] * 0.55)
check("last frame fades via Out", frame(119, OutEngine=0.0)[0].opacity < 0.05)
check("PreCalc skips GPU", frame(10, pre=True)[0] is None)
check("GPU failure => transparent, no crash", frame(10, fail=True)[1] is not None)
check("stagger delays", frame(10, InEngine=0.0, Index=5.0, Stagger=0.1)[0].opacity < frame(10, InEngine=0.0)[0].opacity)
b, _ = frame(60, Shape=3.0, UseEnd=1.0)
check("line endpoints: centre = midpoint, half = distance/2 (defaults 0.3,0.5 -> 0.7,0.5)", near(b.center[1], 960, 0.5) and near(b.center[2], 540, 0.5) and near(b.half[1], 0.2 * 1920, 0.5) and near(b.cosA, 1, 1e-6))
import math as _m
b, _ = frame(60, Shape=3.0, UseEnd=1.0, LT={"X": 0.3, "Y": 0.9})
check("vertical line: angle 90 deg, length = dy in px", near(b.sinA, 1, 1e-6) and near(b.half[1], 0.4 * 1080 / 2, 0.5) and near(b.center[1], 0.3 * 1920, 0.5) and near(b.center[2], 0.7 * 1080, 0.5))
b, _ = frame(0, Shape=3.0, TrimAnim=1.0, InEngine=0.0); check("draw-on: trim 0 at the start of In", near(b.trim, 0, 1e-6))
b, _ = frame(60, Shape=3.0, TrimAnim=1.0); check("draw-on: full trim when settled", near(b.trim, 1, 1e-3))
check("draw-on off keeps Trim", near(frame(0, Shape=3.0, InEngine=0.0)[0].trim, 1, 1e-6))
check("dot radius in px@1920 scales", near(frame(60, DotR=10.0)[0].dotR, 10, 1e-6))
print(f"shape: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
