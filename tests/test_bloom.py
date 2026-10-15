"""SMK2_Bloom: oracle behaviour, Fuse CPU stage (mock), multi-pass kernel pipeline vs oracle (real kernels compiled with gcc)."""
import math, os, random, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fusetest as ft, kparity
C = ft.Counter(); check = C.check
ft.build()
lua, smk, T = ft.oracle("smk_bloom")
W, H = 96, 64
def levels(ow, oh): return [math.ceil(ow / 2 ** k) for k in range(1, 7)], [math.ceil(oh / 2 ** k) for k in range(1, 7)]
def P(pad=0, R=20, **k):
    ow, oh = W + 2 * pad, H + 2 * pad; lw, lh = levels(ow, oh)
    wts = [1 / (1 + (2 ** i / R) ** 4) for i in range(1, 7)]; s = sum(wts); wts = [w / s for w in wts]
    d = dict(size=[W, H], off=[-pad, -pad], osize=[ow, oh], lw=lw, lh=lh, lvl=0, glowSrc=0, glowBehind=0, glowOnly=0, glowThr=0.5, glowI=1.5, glowGamma=1, opacity=1, wts=wts, glowCol=[0.2, 0.4, 1, 1])
    d.update(k); return ft.table(lua, d)
img = ft.rect_image(W, H, 38, 58, 26, 38); src = ft.src_fn(lua, img, W, H)
def render(p, s=src): L = smk.bloomBuild(p, s); return lambda x, y: tuple(smk.bloomShade(p, L, x, y, s))
r = render(P(pad=30))
check("object pixel is kept (additive adds glow on top, alpha stays 1)", r(30 + 48, 30 + 32)[3] == 1.0 and r(30 + 48, 30 + 32)[2] >= 1.0)
check("halo outside the object, none far away", r(30 + 30, 30 + 32)[3] > 0.02 and r(0, 0)[3] < 0.02)
check("halo falls off with distance", r(30 + 36, 30 + 32)[3] > r(30 + 28, 30 + 32)[3] > r(30 + 18, 30 + 32)[3] > r(30 + 6, 30 + 32)[3])
check("halo is symmetric left/right of a centred object", abs(r(30 + 48 - 30, 30 + 32)[3] - r(30 + 48 + 30, 30 + 32)[3]) < 0.02)
check("bigger radius = wider glow", render(P(pad=30, R=40))(30 + 12, 30 + 32)[3] > render(P(pad=30, R=8))(30 + 12, 30 + 32)[3])
check("intensity scales", render(P(pad=30, glowI=3))(30 + 30, 30 + 32)[3] > r(30 + 30, 30 + 32)[3])
check("glow only: object removed", render(P(pad=30, glowOnly=1))(30 + 48, 30 + 32)[0] < 0.5 and render(P(pad=30, glowOnly=1))(30 + 30, 30 + 32)[3] > 0.02)
check("behind leaves the object untouched", render(P(pad=30, glowBehind=1))(30 + 48, 30 + 32) == (1, 1, 1, 1))
check("glow tint (blue-ish halo)", r(30 + 30, 30 + 32)[2] > r(30 + 30, 30 + 32)[0])
check("opacity multiplies", abs(render(P(pad=30, opacity=0.5))(30 + 48, 30 + 32)[3] - 0.5) < 1e-6)
check("spread < 1 gives brighter tails", render(P(pad=30, glowGamma=0.5))(30 + 10, 30 + 32)[3] > render(P(pad=30, glowGamma=1.5))(30 + 10, 30 + 32)[3])
dark = ft.src_fn(lua, ft.rect_image(W, H, 38, 58, 26, 38, color=(0.1, 0.1, 0.1)), W, H)
check("brightness source: dark object does not glow, bright does", render(P(pad=30, glowSrc=1), dark)(30 + 30, 30 + 32)[3] < 1e-6 and render(P(pad=30, glowSrc=1))(30 + 30, 30 + 32)[3] > 0.02)
# energy: total glow mass is conserved by the pyramid (sum of field ~ constant w.r.t. radius)
def mass(R):
    p = P(pad=40, R=R, glowI=1); rr = render(p); return sum(rr(x, y)[3] for x in range(0, W + 80) for y in range(0, H + 80))
check("glow mass roughly independent of radius (within 25%)", abs(mass(8) - mass(40)) / mass(8) < 0.25)

# ---------------- Fuse CPU stage
lua2 = ft.LuaRuntime(unpack_returned_tuples=True)
fsrc, frame = ft.load_fuse(lua2, "SMK2_Bloom")
check("no runtime require", "require(" not in fsrc and "dofile(" not in fsrc)
b, out, added = frame(0)
check("defaults: window not padded without a DataWindow; 6 levels halving", out.DataWindow is None and b.osize[1] == 1920 and b.lw[1] == 960 and b.lw[6] == 30 and b.lh[1] == 540)
check("level weights sum to 1", abs(sum(b.wts[i] for i in range(1, 7)) - 1) < 1e-9)
check("big radius adds levels: R=300 at 1080p builds 1 extra halving, weights still sum to 1", frame(0, GlowR=300.0)[0].sh == 2 and b.sh == 0 and abs(sum(frame(0, GlowR=300.0)[0].wts[i] for i in range(1, 7)) - 1) < 1e-9)
check("a large radius shifts weight to coarse levels", frame(0, GlowR=300.0)[0].wts[6] > frame(0, GlowR=10.0)[0].wts[6])
check("passes: extract(src) + 5 downs + comp(src, L1..L6) = last AddInput list", list(added.values())[-7:] == ["src", "L1", "L2", "L3", "L4", "L5", "L6"])
check("8 render passes", len([a for a in added.values() if a in ("src", "prev")]) == 2 + 5)
lua2.execute("IMG.DataWindow = {left=700,bottom=400,right=1000,top=600}")
b, out, _ = frame(0, GlowR=100.0); pad = math.ceil(100 * 1.3) + 2
check("DoD padding: window grown by 1.3 x radius + 2, kernel gets origin/size", out.DataWindow.left == 700 - pad and out.DataWindow.top == 600 + pad and b.off[1] == 700 - pad and b.osize[1] == 300 + 2 * pad)
lua2.execute("IMG.DataWindow = nil")
check("PreCalc skips the GPU", frame(0, pre=True)[0] is None)
check("GPU failure passes the input through", frame(0, fail=True)[1] is not None)
check("no input: nil output", frame(0, noimg=True)[1] is None)

# ---------------- multi-pass kernel pipeline parity
cc = shutil.which("gcc") or shutil.which("cc")
if not cc: print("bloom kernel parity: SKIPPED (no C compiler)")
else:
    fuse = open(os.path.join(ft.ROOT, "dist/fuses/SMK2_Bloom.fuse")).read()
    ks = {n: re.search(rf"{n} = \[\[(.*?)\]\]", fuse, re.S).group(1) for n in ("SMK2BloomExtractSource", "SMK2BloomDownSource", "SMK2BloomCompSource")}
    fields = re.search(r"SMK2BloomParams = \[\[(.*?)\]\]", fuse, re.S).group(1).replace("\n", " ")
    random.seed(61)
    pic = kparity.make_image(W, H, random, blobs=5); sfn = ft.src_fn(lua, pic, W, H)
    def scen():
        pad = random.choice([0, 12, 30]); R = random.uniform(6, 60); ow, oh = W + 2 * pad, H + 2 * pad; lw, lh = levels(ow, oh)
        wts = [1 / (1 + (2 ** i / R) ** 4) for i in range(1, 7)]; s = sum(wts)
        return dict(pad=pad, ow=ow, oh=oh, lw=lw, lh=lh, glowSrc=random.choice([0, 1]), glowBehind=random.choice([0, 1]), glowOnly=random.choice([0, 0, 1]), glowThr=random.uniform(0.2, 0.7),
                    glowI=random.uniform(0.8, 3), glowGamma=random.uniform(0.6, 1.6), opacity=random.choice([1, 0.7]), wts=[w / s for w in wts], glowCol=[random.random() for _ in range(3)] + [random.choice([1, 0.8])])
    scens = [scen() for _ in range(4)]
    F, A = kparity.F, kparity.A
    I_ = lambda a: "{" + ",".join(str(v) for v in a) + "}"
    def init(s, lvl):
        return ("{ {%d,%d}, {%d,%d}, {%d,%d}, %s, %s, %d, %d, %d, %d, %d, %s, %s, %s, %s, %s, %s }" % (W, H, -s["pad"], -s["pad"], s["ow"], s["oh"], I_(s["lw"]), I_(s["lh"]), lvl, 0, s["glowSrc"], s["glowBehind"], s["glowOnly"],
                F(s["glowThr"]), F(s["glowI"]), F(s["glowGamma"]), F(s["opacity"]), A(s["wts"]), A(s["glowCol"])))
    flat = ",".join(F(v) for row in pic for p in row for v in p)
    c = f"""
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct {{ float x,y,z,w; }} float4;
typedef struct {{ const float4* d; int w, h; }} Tex;
typedef struct {{ float4* d; int w, h; }} OutTex;
static float4 make_float4(float x,float y,float z,float w){{float4 r={{x,y,z,w}};return r;}}
#define __KERNEL__ static
#define __CONSTANTREF__ const
#define __TEXTURE2D__ const Tex*
#define __TEXTURE2D_WRITE__ OutTex*
#define DEFINE_KERNEL_ITERATORS_XY(x,y) int x=gx, y=gy
#define _tex2DVec4Write(dst,x,y,c) (dst)->d[(y)*(dst)->w+(x)] = (c)
static float4 _tex2DVecN(const Tex* t, float u, float v, int n) {{
  int ix = (int)floorf(u * t->w), iy = (int)floorf(v * t->h);
  if (ix < 0) ix = 0; if (ix > t->w-1) ix = t->w-1; if (iy < 0) iy = 0; if (iy > t->h-1) iy = t->h-1;
  return t->d[iy * t->w + ix]; }}
typedef struct {{ {fields} }} SMK2BloomParams;
static int gx, gy;
static const float PIC[] = {{ {flat} }};
{ks['SMK2BloomExtractSource']}
{ks['SMK2BloomDownSource']}
{ks['SMK2BloomCompSource']}
static SMK2BloomParams S[][7] = {{ {",".join("{" + ",".join(init(s, l) for l in range(7)) + "}" for s in scens)} }};
int main() {{
  Tex src; src.w = {W}; src.h = {H}; src.d = malloc(sizeof(float4) * {W*H}); for (int i = 0; i < {W*H}; ++i) ((float4*)src.d)[i] = make_float4(PIC[4*i], PIC[4*i+1], PIC[4*i+2], PIC[4*i+3]);
  for (int sc = 0; sc < {len(scens)}; ++sc) {{
    SMK2BloomParams* p0 = &S[sc][0];
    OutTex lv[6]; Tex lt[6];
    for (int k = 0; k < 6; ++k) {{ lv[k].w = p0->lw[k]; lv[k].h = p0->lh[k]; lv[k].d = calloc(lv[k].w * lv[k].h, sizeof(float4)); }}
    for (gy = 0; gy < lv[0].h; ++gy) for (gx = 0; gx < lv[0].w; ++gx) SMK2BloomExtractKernel(p0, &src, &lv[0]);
    for (int k = 0; k < 6; ++k) {{ lt[k].w = lv[k].w; lt[k].h = lv[k].h; lt[k].d = lv[k].d; }}
    for (int k = 1; k < 6; ++k) for (gy = 0; gy < lv[k].h; ++gy) for (gx = 0; gx < lv[k].w; ++gx) SMK2BloomDownKernel(&S[sc][k], &lt[k-1], &lv[k]);
    OutTex o; o.w = p0->osize[0]; o.h = p0->osize[1]; o.d = calloc(o.w * o.h, sizeof(float4));
    for (gy = 0; gy < o.h; ++gy) for (gx = 0; gx < o.w; ++gx) {{
      SMK2BloomCompKernel(p0, &src, &lt[0], &lt[1], &lt[2], &lt[3], &lt[4], &lt[5], &o);
      float4 c = o.d[gy*o.w+gx]; printf("%d %d %d %.6f %.6f %.6f %.6f\\n", sc, gx, gy, c.x, c.y, c.z, c.w); }}
  }}
  return 0; }}
"""
    d = tempfile.mkdtemp(); open(d + "/k.c", "w").write(c)
    rr = subprocess.run([cc, "-O1", "-o", d + "/k", d + "/k.c", "-lm"], capture_output=True, text=True)
    if rr.returncode: print(rr.stderr[:3000]); print("bloom kernel parity: COMPILE FAILED"); sys.exit(1)
    outp = subprocess.run([d + "/k"], capture_output=True, text=True).stdout.split("\n")
    renders = []
    for s in scens:
        p = ft.table(lua, dict(s, size=[W, H], off=[-s["pad"], -s["pad"]], osize=[s["ow"], s["oh"]], lvl=0))
        renders.append(render(p, sfn))
    n = bad = 0; worst = 0.0
    for line in outp:
        if not line: continue
        i, x, y, *cv = line.split(); i, x, y = int(i), int(x), int(y); cv = list(map(float, cv))
        o = renders[i](x, y); n += 1
        df = max(abs(a - b) for a, b in zip(cv, o)); worst = max(worst, df)
        if df > 3e-3: bad += 1
    expect = sum(s["ow"] * s["oh"] for s in scens)
    ok = n == expect and bad / max(n, 1) < 0.003
    check(f"bloom pipeline parity: {n} px, {bad} differ, max {worst:.2e}", ok)
    print(f"bloom pipeline parity: {n} pixels, {bad} differ by > 3e-3, max diff {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
C.done("bloom")
