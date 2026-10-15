"""SMK2_LongShadow: oracle behaviour, Fuse CPU stage (mock), multi-pass kernel pipeline vs oracle (gcc)."""
import math, os, random, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fusetest as ft, kparity
C = ft.Counter(); check = C.check
ft.build()
lua, smk, T = ft.oracle("smk_longshadow")
W, H = 96, 64
def P(pad=(40, 40, 40, 40), L=40, ang=0.0, **k):
    l, r, b, t = pad; ow, oh = W + l + r, H + b + t
    d = dict(size=[W, H], off=[-l, -b], osize=[ow, oh], passes=smk.lsPasses(L), shift=1, dx=math.cos(ang), dy=math.sin(ang), slope=1 / L, curve=1, opacity=1, col=[0, 0, 0, 1])
    d.update(k); return ft.table(lua, d), (l, b)
img = ft.rect_image(W, H, 30, 40, 28, 36, color=(1, 0.5, 0.2)); src = ft.src_fn(lua, img, W, H)
def render(ang=0.0, L=40, **k):
    p, (l, b) = P(L=L, ang=ang, **k); F = smk.lsBuild(p, src)
    return (lambda x, y: tuple(smk.lsShade(p, F, x + l, y + b, src)))     # x, y in SOURCE pixel coordinates
r = render()
check("passes = ceil(log2(L+1))", smk.lsPasses(1) == 1 and smk.lsPasses(40) == 6 and smk.lsPasses(1000) == 10 and smk.lsPasses(1e9) == 12)
check("object pixel unchanged", r(35, 32) == (1, 0.5, 0.2, 1))
check("shadow to the right (direction 0), fading linearly with distance", r(41, 32)[3] > 0.9 and abs(r(40 + 20, 32)[3] - 0.5) < 0.06 and r(40 + 39, 32)[3] < 0.06 and r(40 + 45, 32)[3] == 0)
check("no shadow on the other side or above/below", r(25, 32)[3] == 0 and r(35, 50)[3] == 0 and r(35, 10)[3] == 0)
check("shadow is black here (colour * alpha), behind the object", r(50, 32)[0] == 0 and r(50, 32)[3] > 0.5)
up = render(math.pi / 2); check("direction 90 = shadow goes up (y up)", up(35, 36 + 10)[3] > 0.5 and up(35, 28 - 10)[3] == 0)
dg = render(-math.pi / 4); check("direction -45 = down-right, diagonal reach", dg(40 + 10, 28 - 10)[3] > 0.4 and dg(40 + 10, 28 + 10)[3] == 0)
check("length 80 reaches further than 40", render(0.0, 80)(40 + 60, 32)[3] > r(40 + 60, 32)[3])
rc = render(col=[1, 0, 0, 0.5])(50, 32)
check("shadow colour and alpha apply (red, half strength)", rc[0] > 0.1 and rc[1] == 0 and rc[3] < r(50, 32)[3])
check("fade curve < 1 makes the tail brighter", render(curve=0.5)(40 + 30, 32)[3] > r(40 + 30, 32)[3])
check("opacity multiplies", abs(render(opacity=0.5)(35, 32)[3] - 0.5) < 1e-6)
sq = ft.rect_image(W, H, 80, 94, 28, 36); sr = ft.src_fn(lua, sq, W, H)
p, (l, b) = P(L=40, ang=0.0); F = smk.lsBuild(p, sr)
check("padding catches the shadow that leaves the frame", smk.lsShade(p, F, W + 10 + l, 32 + b, sr)[3] > 0.4)

# ---------------- Fuse CPU stage
lua2 = ft.LuaRuntime(unpack_returned_tuples=True)
fsrc, frame = ft.load_fuse(lua2, "SMK2_LongShadow")
check("no runtime require", "require(" not in fsrc and "dofile(" not in fsrc)
b, out, added = frame(0)
check("defaults: down-right, 400 px -> 9 passes, slope 1/400, no padding without a DataWindow", b.passes == 9 and abs(b.slope - 1 / 400) < 1e-9 and b.dx > 0.7 and b.dy < -0.7 and out.DataWindow is None)
b2, _, _ = frame(0, Length=400.0); check("slope scales with length", abs(b2.slope - 1 / 400) < 1e-9)
check("pass count follows length", frame(0, Length=1000.0)[0].passes == 10 and frame(0, Length=20.0)[0].passes == 5)
check("input textures of the composite", list(added.values())[-2:] == ["src", "F"] and list(added.values()).count("prev") == b.passes)
lua2.execute("IMG.DataWindow = {left=700,bottom=400,right=1000,top=600}")
b, out, _ = frame(0, Direction=0.0, Length=100.0); dw = out.DataWindow
check("padding only on the shadow side (right +102, others +2)", dw.right == 1000 + 102 and dw.left == 700 - 2 and dw.top == 600 + 2 and dw.bottom == 400 - 2)
b, out, _ = frame(0, Direction=-90.0, Length=100.0); dw = out.DataWindow
check("direction -90 pads the bottom", dw.bottom == 400 - 102 and dw.top == 600 + 2 and b.off[2] == 400 - 102)
lua2.execute("IMG.DataWindow = nil")
check("PreCalc skips the GPU", frame(0, pre=True)[0] is None)
check("GPU failure passes the input through", frame(0, fail=True)[1] is not None)
check("no input: nil output", frame(0, noimg=True)[1] is None)

# ---------------- multi-pass kernel pipeline parity
cc = shutil.which("gcc") or shutil.which("cc")
if not cc: print("longshadow kernel parity: SKIPPED (no C compiler)")
else:
    fuse = open(os.path.join(ft.ROOT, "dist/fuses/SMK2_LongShadow.fuse")).read()
    ks = {n: re.search(rf"{n} = \[\[(.*?)\]\]", fuse, re.S).group(1) for n in ("SMK2LSInitSource", "SMK2LSStepSource", "SMK2LSCompSource")}
    fields = re.search(r"SMK2LSParams = \[\[(.*?)\]\]", fuse, re.S).group(1).replace("\n", " ")
    random.seed(71)
    pic = kparity.make_image(W, H, random, blobs=5); sfn = ft.src_fn(lua, pic, W, H)
    def scen():
        L = random.uniform(6, 70); a = random.uniform(0, 6.283)
        pad = [math.ceil(max(0, -math.cos(a)) * L) + 2, math.ceil(max(0, math.cos(a)) * L) + 2, math.ceil(max(0, -math.sin(a)) * L) + 2, math.ceil(max(0, math.sin(a)) * L) + 2]
        return dict(pad=pad, L=L, a=a, curve=random.uniform(0.6, 1.6), opacity=random.choice([1, 0.7]), col=[random.random() for _ in range(3)] + [random.choice([1, 0.6])])
    scens = [scen() for _ in range(4)]
    F_, A_ = kparity.F, kparity.A
    def init(s, shift):
        l, r_, b_, t_ = s["pad"]
        return "{ {%d,%d}, {%d,%d}, {%d,%d}, %d, %s, %s, %s, %s, %s, %s, %s }" % (W, H, -l, -b_, W + l + r_, H + b_ + t_, smk.lsPasses(s["L"]), F_(shift), F_(math.cos(s["a"])), F_(math.sin(s["a"])), F_(1 / s["L"]), F_(s["curve"]), F_(s["opacity"]), A_(s["col"]))
    flat = ",".join(F_(v) for row in pic for p_ in row for v in p_)
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
typedef struct {{ {fields} }} SMK2LSParams;
static int gx, gy;
static const float PIC[] = {{ {flat} }};
{ks['SMK2LSInitSource']}
{ks['SMK2LSStepSource']}
{ks['SMK2LSCompSource']}
static SMK2LSParams S0[] = {{ {",".join(init(s, 0) for s in scens)} }};
int main() {{
  Tex src; src.w = {W}; src.h = {H}; src.d = malloc(sizeof(float4) * {W*H}); for (int i = 0; i < {W*H}; ++i) ((float4*)src.d)[i] = make_float4(PIC[4*i], PIC[4*i+1], PIC[4*i+2], PIC[4*i+3]);
  for (int sc = 0; sc < {len(scens)}; ++sc) {{
    SMK2LSParams p = S0[sc]; int w = p.osize[0], h = p.osize[1];
    OutTex a, b, o; a.w = b.w = o.w = w; a.h = b.h = o.h = h;
    a.d = calloc(w*h, sizeof(float4)); b.d = calloc(w*h, sizeof(float4)); o.d = calloc(w*h, sizeof(float4));
    for (gy = 0; gy < h; ++gy) for (gx = 0; gx < w; ++gx) SMK2LSInitKernel(&p, &src, &a);
    for (int k = 1; k <= p.passes; ++k) {{
      p.shift = (float)(1 << (k - 1)); Tex t; t.w = w; t.h = h; t.d = a.d;
      for (gy = 0; gy < h; ++gy) for (gx = 0; gx < w; ++gx) SMK2LSStepKernel(&p, &t, &b);
      float4* tmp = a.d; a.d = b.d; b.d = tmp;
    }}
    Tex ft; ft.w = w; ft.h = h; ft.d = a.d;
    for (gy = 0; gy < h; ++gy) for (gx = 0; gx < w; ++gx) {{
      SMK2LSCompKernel(&p, &src, &ft, &o);
      float4 c = o.d[gy*w+gx]; printf("%d %d %d %.6f %.6f %.6f %.6f\\n", sc, gx, gy, c.x, c.y, c.z, c.w); }}
  }}
  return 0; }}
"""
    d = tempfile.mkdtemp(); open(d + "/k.c", "w").write(c)
    rr = subprocess.run([cc, "-O1", "-o", d + "/k", d + "/k.c", "-lm"], capture_output=True, text=True)
    if rr.returncode: print(rr.stderr[:3000]); print("longshadow kernel parity: COMPILE FAILED"); sys.exit(1)
    outp = subprocess.run([d + "/k"], capture_output=True, text=True).stdout.split("\n")
    renders = []
    for s in scens:
        l, r_, b_, t_ = s["pad"]
        p = ft.table(lua, dict(size=[W, H], off=[-l, -b_], osize=[W + l + r_, H + b_ + t_], passes=smk.lsPasses(s["L"]), shift=1, dx=math.cos(s["a"]), dy=math.sin(s["a"]), slope=1 / s["L"], curve=s["curve"], opacity=s["opacity"], col=s["col"]))
        Fm = smk.lsBuild(p, sfn); renders.append(lambda x, y, p=p, Fm=Fm: tuple(smk.lsShade(p, Fm, x, y, sfn)))
    n = bad = 0; worst = 0.0
    for line in outp:
        if not line: continue
        i, x, y, *cv = line.split(); i, x, y = int(i), int(x), int(y); cv = list(map(float, cv))
        o = renders[i](x, y); n += 1
        df = max(abs(a - b) for a, b in zip(cv, o)); worst = max(worst, df)
        if df > 3e-3: bad += 1
    expect = sum((W + s["pad"][0] + s["pad"][1]) * (H + s["pad"][2] + s["pad"][3]) for s in scens)
    ok = n == expect and bad / max(n, 1) < 0.003
    check(f"longshadow pipeline parity: {n} px, {bad} differ, max {worst:.2e}", ok)
    print(f"longshadow pipeline parity: {n} pixels, {bad} differ by > 3e-3, max diff {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
C.done("longshadow")
