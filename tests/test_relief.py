"""SMK2_Relief: oracle behaviour, Fuse CPU stage (mock), kernel-vs-oracle parity."""
import math, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fusetest as ft, kparity
C = ft.Counter(); check = C.check
ft.build()
lua, smk, T = ft.oracle("smk_relief")
W, H = 96, 64
def P(**k):
    d = dict(size=[W, H], samples=48, srcKind=0, reliefOnly=0, sigma=4, depth=2, lx=-0.5, ly=0.5, hiAmt=2, shAmt=2, blend=1, opacity=1,
             hiCol=[1, 1, 1, 1], shCol=[0, 0, 0, 1])
    d.update(k); return ft.table(lua, d)
img = ft.rect_image(W, H, 30, 66, 20, 44, color=(0.5, 0.5, 0.5)); src = ft.src_fn(lua, img, W, H)
px = lambda p, x, y, s=src: tuple(smk.reliefShade(p, x, y, s))
# light from the upper left (dir 135deg: lx<0, ly>0, y up): edges facing the light brighten, opposite edges darken
check("flat interior is unchanged", all(abs(a - b) < 1e-2 for a, b in zip(px(P(), 48, 32), (0.5, 0.5, 0.5, 1))))
check("far outside stays empty", px(P(), 3, 3)[3] == 0)
left, right, top, bottom = px(P(), 31, 32), px(P(), 64, 32), px(P(), 48, 43), px(P(), 48, 21)
check("edge facing the light is brighter than the interior", left[0] > 0.5 + 0.02 and top[0] > 0.5 + 0.02)
check("edge facing away is darker than the interior", right[0] < 0.5 - 0.02 and bottom[0] < 0.5 - 0.02)
check("alpha is untouched by the bevel", all(abs(px(P(), x, 32)[3] - src(x + .5, 32.5)[3]) < 1e-6 for x in (31, 48, 64)))
check("depth 0 = no effect", all(abs(a - b) < 1e-4 for a, b in zip(px(P(depth=0), 31, 32), (0.5, 0.5, 0.5, 1))))
check("blend 0 = no effect", all(abs(a - b) < 1e-6 for a, b in zip(px(P(blend=0), 31, 32), (0.5, 0.5, 0.5, 1))))
check("more depth = stronger edge response", px(P(depth=4), 31, 32)[0] > px(P(depth=1), 31, 32)[0])
check("opening the light direction flips highlight/shadow", px(P(lx=0.5, ly=-0.5), 31, 32)[0] < 0.5 < px(P(lx=0.5, ly=-0.5), 64, 32)[0])
check("coloured highlight tints the edge", px(P(hiCol=[1, 0, 0, 1], hiAmt=4), 31, 32)[0] > px(P(hiCol=[1, 0, 0, 1], hiAmt=4), 31, 32)[1] + 0.05)
rm = P(reliefOnly=1)
check("relief map: flat = mid-grey, lit edge lighter, shaded edge darker, grey (r=g=b)", abs(px(rm, 48, 32)[0] - 0.5) < 1e-2 and px(rm, 31, 32)[0] > 0.52 and px(rm, 64, 32)[0] < 0.48 and px(rm, 31, 32)[0] == px(rm, 31, 32)[2])
check("opacity multiplies", abs(px(P(opacity=0.5), 48, 32)[3] - 0.5) < 1e-6)
# brightness height: a dark rect on a bright one reads as a dent
bimg = ft.rect_image(W, H, 0, W, 0, H, color=(1, 1, 1)); br = [[(1, 1, 1, 1)] * W for _ in range(H)]
for y in range(20, 44):
    for x in range(30, 66): br[y][x] = (0.1, 0.1, 0.1, 1)
bs = ft.src_fn(lua, br, W, H)
check("brightness height: alpha-flat image still gets edges", px(P(srcKind=1), 31, 32, bs)[0] != px(P(srcKind=0), 31, 32, bs)[0] and abs(px(P(srcKind=0), 31, 32, bs)[0] - 0.1) < 1e-2)

# ---------------- Fuse CPU stage
lua2 = ft.LuaRuntime(unpack_returned_tuples=True)
fsrc, frame = ft.load_fuse(lua2, "SMK2_Relief")
check("no runtime require", "require(" not in fsrc and "dofile(" not in fsrc)
b, out, added = frame(0)
check("defaults: bevel, alpha, size 8 px, light up-left", b.reliefOnly == 0 and b.srcKind == 0 and abs(b.sigma - 8) < 1e-6 and b.lx < 0 < b.ly)
check("light lateral part = cos(elevation)", abs(math.hypot(b.lx, b.ly) - math.cos(math.radians(45))) < 1e-6)
check("sizes are px@1920", abs(frame(0, Size=8.0)[0].sigma - 8) < 1e-6)
check("direction 0 = light from the right (+x), CCW", frame(0, Direction=0.0)[0].lx > 0.5 and abs(frame(0, Direction=0.0)[0].ly) < 1e-6 and frame(0, Direction=90.0)[0].ly > 0.5)
check("quality maps to taps, large sizes get more", [frame(0, Quality=float(i), Size=2.0)[0].samples for i in range(3)] == [24, 48, 96] and frame(0, Size=40.0)[0].samples >= 120)
check("mode and height-from inputs", frame(0, Mode=1.0)[0].reliefOnly == 1 and frame(0, HeightFrom=1.0)[0].srcKind == 1)
check("one input texture", list(added.values()) == ["src"])
check("PreCalc skips the GPU", frame(0, pre=True)[0] is None)
check("GPU failure passes the input through", frame(0, fail=True)[1] is not None)
check("no input: nil output", frame(0, noimg=True)[1] is None)

# ---------------- kernel parity
random.seed(31)
fuse = open(os.path.join(ft.ROOT, "dist/fuses/SMK2_Relief.fuse")).read()
bimg2 = kparity.make_image(W, H, random, blobs=6)
def scen():
    dr, el = random.uniform(0, 6.28), random.uniform(0.3, 1.4)
    return dict(samples=random.choice([24, 48, 96]), srcKind=random.choice([0, 1]), reliefOnly=random.choice([0, 0, 1]), sigma=random.uniform(1, 7), depth=random.uniform(0.5, 6),
                lx=math.cos(el) * math.cos(dr), ly=math.cos(el) * math.sin(dr), hiAmt=random.uniform(0.5, 4), shAmt=random.uniform(0.5, 4),
                blend=random.choice([1, 0.6]), opacity=random.choice([1, 0.8]), hiCol=[random.random() for _ in range(3)] + [1], shCol=[random.random() for _ in range(3)] + [random.choice([1, 0.7])])
scens = [scen() for _ in range(5)]
order = ["samples", "srcKind", "reliefOnly"]; forder = ["sigma", "depth", "lx", "ly", "hiAmt", "shAmt", "blend", "opacity"]
init = lambda s: "{ {%d,%d}, " % (W, H) + ", ".join(str(s[k]) for k in order) + ", " + ", ".join(kparity.F(s[k]) for k in forder) + ", " + kparity.A(s["hiCol"]) + ", " + kparity.A(s["shCol"]) + " }"
sfn = ft.src_fn(lua, bimg2, W, H)
res = kparity.run(fuse, "SMK2ReliefSource", "SMK2ReliefParams", "SMK2ReliefKernel", scens, init, W, H, {"IMG0": bimg2}, ["IMG0"],
                  lambda i, x, y: tuple(smk.reliefShade(ft.table(lua, scens[i], size=[W, H]), x, y, sfn)))
if res is None: print("relief kernel parity: SKIPPED (no C compiler)")
else:
    ok, n, bad, worst = res
    check(f"relief kernel parity: {n} px, {bad} differ, max {worst:.2e}", ok)
    print(f"relief kernel parity: {n} pixels, {bad} differ by > 3e-3, max diff {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
C.done("relief")
