"""SMK2_Reflection: oracle behaviour, Fuse CPU stage (mock), kernel-vs-oracle parity."""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fusetest as ft, kparity
C = ft.Counter(); check = C.check
ft.build()
lua, smk, T = ft.oracle("smk_reflection")
W, H = 96, 96
def P(**k):
    d = dict(size=[W, H], keepOrig=1, samples=32, baseY=60, gap=0, fadeLen=40, fadePow=1, reflOpacity=1, blur0=0, blurGrow=0, rippleAmp=0, rippleFreq=0.1, phase=0, opacity=1, tint=[1, 1, 1, 1])
    d.update(k); return ft.table(lua, d)
# object sits ON the baseline (y 60..80, y-up): its mirror is at y 40..60
img = ft.rect_image(W, H, 30, 66, 60, 80, color=(1, 0.5, 0.2)); src = ft.src_fn(lua, img, W, H)
px = lambda p, x, y, s=src: tuple(smk.reflectShade(p, x, y, s))
check("original is kept untouched", px(P(), 48, 70) == (1, 0.5, 0.2, 1))
check("reflection appears just below the baseline", px(P(), 48, 59)[3] > 0.9 and px(P(), 48, 59)[0] > 0.9)
check("reflection fades with distance and ends at the length", px(P(), 48, 59)[3] > px(P(), 48, 49)[3] > px(P(), 48, 42)[3] > 0 and px(P(), 48, 15)[3] == 0)
check("reflection is horizontally aligned (mirror, not shifted)", px(P(), 29, 55)[3] == 0 and px(P(), 31, 55)[3] > 0.5)
check("reflection only (keep original off)", px(P(keepOrig=0), 48, 70)[3] == 0 and px(P(keepOrig=0), 48, 59)[3] > 0.9)
check("gap lowers the start of the reflection", px(P(gap=6), 48, 58)[3] == 0 and px(P(gap=6), 48, 53)[3] > 0.5)
check("reflection opacity scales it", abs(px(P(reflOpacity=0.5), 48, 59)[3] - px(P(), 48, 59)[3] * 0.5) < 1e-6)
check("tint colours the reflection but not the original", px(P(tint=[0, 0, 1, 1]), 48, 59)[0] < 1e-6 and px(P(tint=[0, 0, 1, 1]), 48, 70)[0] == 1)
check("fade curve > 1 darkens the middle faster", px(P(fadePow=2), 48, 48)[3] < px(P(fadePow=1), 48, 48)[3])
# blur grows with distance: soft edge below the object's side edge is wider far away than near
near_edge = [px(P(blurGrow=0.15), x, 58)[3] for x in range(24, 36)]
far_edge = [px(P(blurGrow=0.15), x, 44)[3] for x in range(24, 36)]
width = lambda v: sum(1 for a in v if 0.05 < a < 0.95)
check("blur grows with distance (far edge softer than near edge)", width(far_edge) > width(near_edge))
check("blur keeps energy (interior stays ~ solid in the middle of a wide object)", px(P(blurGrow=0.15), 48, 56)[3] > 0.9)
rip = P(rippleAmp=3, rippleFreq=0.3)
check("ripple wobbles the edge sideways, no ripple at the baseline", px(rip, 31, 58) == px(P(), 31, 58) or abs(px(rip, 31, 58)[3] - px(P(), 31, 58)[3]) < 0.2)
check("ripple changes with the phase", any(abs(px(P(rippleAmp=3, rippleFreq=0.3, phase=0), x, 45)[3] - px(P(rippleAmp=3, rippleFreq=0.3, phase=2), x, 45)[3]) > 0.05 for x in range(26, 36)))
check("opacity multiplies all", abs(px(P(opacity=0.5), 48, 70)[3] - 0.5) < 1e-6)
# premultiplied over: semi-transparent original lets the reflection show through where they overlap (gap negative)
check("negative gap overlaps the object (reflection shows below, original on top)", px(P(gap=-4), 48, 62)[3] >= px(P(), 48, 62)[3])

# ---------------- Fuse CPU stage
lua2 = ft.LuaRuntime(unpack_returned_tuples=True)
fsrc, frame = ft.load_fuse(lua2, "SMK2_Reflection")
check("no runtime require", "require(" not in fsrc and "dofile(" not in fsrc)
b, out, added = frame(0)
check("defaults: keep original, baseline 0.4 of height, length 400 px", b.keepOrig == 1 and abs(b.baseY - 0.4 * 1080) < 1e-6 and abs(b.fadeLen - 400) < 1e-6 and b.samples == 32)
check("blur growth is a ratio (resolution independent)", abs(frame(0, BlurGrow=4.0)[0].blurGrow - 0.04) < 1e-9)
check("ripple phase advances in seconds, clip-relative", abs(frame(0, RippleSpeed=1.0)[0].phase) < 1e-9 and abs(frame(24, RippleSpeed=1.0)[0].phase - 2 * math.pi) < 1e-6 and abs(frame(12, RippleSpeed=1.0)[0].phase - math.pi) < 1e-6)
check("quality maps to taps", [frame(0, Quality=float(i))[0].samples for i in range(3)] == [16, 32, 64])
check("one input texture", list(added.values()) == ["src"])
check("PreCalc skips the GPU", frame(0, pre=True)[0] is None)
check("GPU failure passes the input through", frame(0, fail=True)[1] is not None)
check("no input: nil output", frame(0, noimg=True)[1] is None)

# ---------------- kernel parity
random.seed(41)
fuse = open(os.path.join(ft.ROOT, "dist/fuses/SMK2_Reflection.fuse")).read()
bimg = kparity.make_image(W, H, random, blobs=6)
def scen():
    return dict(keepOrig=random.choice([0, 1, 1]), samples=random.choice([16, 32, 64]), baseY=random.uniform(30, 70), gap=random.uniform(-4, 8), fadeLen=random.uniform(20, 60), fadePow=random.uniform(0.6, 2.5),
                reflOpacity=random.uniform(0.3, 1), blur0=random.choice([0, 0, 2]), blurGrow=random.uniform(0, 0.2), rippleAmp=random.choice([0, 2.5]), rippleFreq=random.uniform(0.1, 0.5),
                phase=random.uniform(0, 6.28), opacity=random.choice([1, 0.7]), tint=[random.random() for _ in range(3)] + [random.choice([1, 0.8])])
scens = [scen() for _ in range(5)]
order = ["keepOrig", "samples"]; forder = ["baseY", "gap", "fadeLen", "fadePow", "reflOpacity", "blur0", "blurGrow", "rippleAmp", "rippleFreq", "phase", "opacity"]
init = lambda s: "{ {%d,%d}, " % (W, H) + ", ".join(str(s[k]) for k in order) + ", " + ", ".join(kparity.F(s[k]) for k in forder) + ", " + kparity.A(s["tint"]) + " }"
sfn = ft.src_fn(lua, bimg, W, H)
res = kparity.run(fuse, "SMK2ReflectSource", "SMK2ReflectParams", "SMK2ReflectKernel", scens, init, W, H, {"IMG0": bimg}, ["IMG0"],
                  lambda i, x, y: tuple(smk.reflectShade(ft.table(lua, scens[i], size=[W, H]), x, y, sfn)))
if res is None: print("reflection kernel parity: SKIPPED (no C compiler)")
else:
    ok, n, bad, worst = res
    check(f"reflection kernel parity: {n} px, {bad} differ, max {worst:.2e}", ok)
    print(f"reflection kernel parity: {n} pixels, {bad} differ by > 3e-3, max diff {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
C.done("reflection")
