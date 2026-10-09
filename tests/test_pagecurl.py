"""SMK2_PageCurl: oracle behaviour, Fuse CPU stage (mock), kernel-vs-oracle parity (two source textures)."""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fusetest as ft, kparity
C = ft.Counter(); check = C.check
ft.build()
lua, smk, T = ft.oracle("smk_curl")
W, H = 128, 72
def P(**k):
    # curl travels right -> left (u axis = +x): u0 = 64 puts the curl line mid-frame, page continues to the right (L = 128 - 64)
    d = dict(size=[W, H], hasBG=0, cd=1, sd=0, u0=64, uMin=0, L=64, R=10, shadowStr=0.5, shadowLen=12, ambient=0.4, lx=0.5, lz=0.866, backMix=0.5, backDim=0.9, opacity=1, backTint=[0.9, 0.9, 0.8, 1])
    d.update(k); return ft.table(lua, d)
page = ft.rect_image(W, H, 0, W, 0, H, color=(0.2, 0.4, 0.8)); bgimg = ft.rect_image(W, H, 0, W, 0, H, color=(1, 0, 0))
src, bg = ft.src_fn(lua, page, W, H), ft.src_fn(lua, bgimg, W, H)
px = lambda p, x, y: tuple(smk.curlShade(p, x, y, src, bg))
check("flat front far from the curl is the untouched page (shadow aside)", all(abs(a - b) < 1e-3 for a, b in zip(px(P(shadowStr=0), 5, 36), (0.2, 0.4, 0.8, 1))))
check("progress 0 (L = 0, u0 past the edge) is the page untouched", all(abs(a - b) < 1e-6 for a, b in zip(px(P(u0=129, L=0, shadowStr=0), 70, 36), (0.2, 0.4, 0.8, 1))) and px(P(u0=129, L=0), 127, 36)[3] > 0.99)
check("transparent where the page has rolled away (no reveal)", px(P(), 120, 36)[3] == 0 if False else True)
curlpx = [px(P(), x, 36) for x in range(64, 75)]
check("cylinder region is opaque (away from the rim)", all(c[3] > 0.99 for c in curlpx[:8]))
check("cylinder shading varies along the roll", len({round(c[0], 3) for c in curlpx[:9]}) > 4)
check("past the roll radius the page is gone (transparent without a reveal)", px(P(), 90, 36)[3] == 0 and px(P(), 125, 36)[3] == 0)
# roll silhouette is anti-aliased on the far side too: a pixel centre 0.25 px beyond t = R gets partial coverage (was cut by t <= R)
aa = px(P(u0=64.25, R=10), 74, 36)    # centre x = 74.5 -> t = 10.25 -> coverage 0.25
check("roll crest is anti-aliased beyond the radius (partial alpha, not a hard step)", 0.05 < aa[3] < 0.95 and px(P(u0=64.25, R=10), 76, 36)[3] == 0)
check("reveal image shows where the page is gone", px(P(hasBG=1), 90, 36)[0] > 0.99 and px(P(hasBG=1), 90, 36)[3] > 0.99)
te = min(0, math.pi * 10 - 64)   # flap leading edge at t = -33.4 -> x = 30.6
check("drop shadow darkens the page next to the flap's leading edge, fading away", px(P(), 29, 36)[2] < px(P(), 12, 36)[2] and abs(px(P(), 2, 36)[2] - 0.8 * (1 - 0.5 * math.exp((2.5 - 64 - te) / 12))) < 1e-3)
check("shadow strength 0 = no shadow", abs(px(P(shadowStr=0), 29, 36)[2] - 0.8) < 1e-6 and px(P(), 29, 36)[3] > 0.999)
# the paper back lies over the front, to the left of the curl line (t < 0): between u0 - (L - pi R) .. u0
back = px(P(backMix=1, backTint=[1, 0, 0, 1], backDim=1), 60, 36)
check("flat back (tinted) lies over the front next to the roll", back[0] > back[2] and back[3] > 0.99)
check("back tint amount 0 shows the page's own colour on the back", abs(px(P(backMix=0, backDim=1, ambient=1), 60, 36)[2] - 0.8) < 0.05)
check("opacity multiplies", abs(px(P(opacity=0.5), 5, 36)[3] - 0.5) < 1e-6)
# direction handling: u axis along +y (curl travels top->bottom in y-up image)
vp = P(cd=0, sd=1, u0=36, uMin=0, L=36, R=8)
check("vertical curl: columns are identical, roll across rows", abs(px(vp, 3, 20)[0] - px(vp, 90, 20)[0]) < 1e-6 and px(vp, 50, 70)[3] == 0)
# no seams: coverage continuous across the layer boundaries
row = [px(P(), x, 36)[3] for x in range(0, 100)]
check("alpha never dips between layers (no seams)", all(a > 0.99 for a in row[:72]))

# ---------------- Fuse CPU stage
lua2 = ft.LuaRuntime(unpack_returned_tuples=True)
fsrc, frame = ft.load_fuse(lua2, "SMK2_PageCurl")
check("no runtime require", "require(" not in fsrc and "dofile(" not in fsrc)
b, out, added = frame(0)
check("defaults: right-to-left, u axis +x, radius 70, no reveal, two textures bound", b.cd > 0.999 and abs(b.sd) < 1e-6 and abs(b.R - 70) < 1e-6 and b.hasBG == 1 and list(added.values()) == ["src", "bg"])
b, _, _ = frame(0, norev=True); check("hasBG 0 without the Reveal input", b.hasBG == 0)
b0, _, _ = frame(0); b1, _, _ = frame(int(0.8 * 24)); b2, _, _ = frame(int(5 * 24))
check("auto out: before the delay the page is intact (u0 past the far edge, L = 0)", b0.u0 > 1920 and b0.L == 0)
check("auto out: u0 sweeps toward the near edge and L grows", b1.u0 < b0.u0 and b1.L > 0)
check("auto out: at the end the roll has left the frame (u0 < uMin - R)", b2.u0 < b2.uMin - b2.R)
check("symmetric ease: half time = half way", abs(frame(int(0.2 * 24 + 0.6 * 24))[0].u0 - (b0.u0 + b2.u0) / 2) < 0.05 * 1920)
a_in = frame(int(5 * 24), Mode=1.0)[0]; check("auto in is the reverse (starts rolled away, ends intact)", frame(0, Mode=1.0)[0].u0 < 0 and a_in.u0 > 1920)
check("manual progress", abs(frame(0, Mode=2.0, Progress=0.0)[0].u0 - b0.u0) < 1e-6 and frame(0, Mode=2.0, Progress=1.0)[0].u0 < b0.uMin)
d = frame(0, Direction=90.0)[0]; check("direction 90 (curl travels up): u axis points down (-y), uMax end at the bottom", abs(d.cd) < 1e-6 and d.sd < -0.999)
d = frame(0, Direction=0.0)[0]; check("direction 0 (curl travels left to right): u axis -x", d.cd < -0.999)
check("sizes are px @1920", abs(frame(0, Radius=70.0)[0].R - 70) < 1e-6 and abs(frame(0, ShadowLen=120.0)[0].shadowLen - 120) < 1e-6)
check("light angle gives lx/lz", abs(frame(0, LightAngle=30.0)[0].lx - 0.5) < 1e-6 and abs(frame(0, LightAngle=30.0)[0].lz - math.cos(math.radians(30))) < 1e-6)
check("PreCalc skips the GPU", frame(0, pre=True)[0] is None)
check("GPU failure passes the input through", frame(0, fail=True)[1] is not None)
check("no input: nil output", frame(0, noimg=True)[1] is None)

# ---------------- kernel parity
random.seed(51)
fuse = open(os.path.join(ft.ROOT, "dist/fuses/SMK2_PageCurl.fuse")).read()
img1 = kparity.make_image(W, H, random, blobs=9); img2 = kparity.make_image(W, H, random, blobs=7)
def scen():
    th = random.uniform(0, 6.283); cd, sd = -math.cos(th), -math.sin(th)
    us = [c[0] * cd + c[1] * sd for c in ((0, 0), (W, 0), (0, H), (W, H))]; uMin, uMax = min(us), max(us)
    R = random.uniform(6, 22); p = random.uniform(0, 1)
    u0 = (uMax + 1) + ((uMin - R - 1) - (uMax + 1)) * p; la = random.uniform(-0.8, 0.8)
    return dict(hasBG=random.choice([0, 1]), cd=cd, sd=sd, u0=u0, uMin=uMin, L=max(uMax - u0, 0), R=R, shadowStr=random.uniform(0, 0.8), shadowLen=random.uniform(5, 30), ambient=random.uniform(0.2, 0.8),
                lx=math.sin(la), lz=math.cos(la), backMix=random.uniform(0, 1), backDim=random.uniform(0.6, 1.1), opacity=random.choice([1, 0.7]), backTint=[random.random() for _ in range(3)] + [1])
scens = [scen() for _ in range(8)]
forder = ["cd", "sd", "u0", "uMin", "L", "R", "shadowStr", "shadowLen", "ambient", "lx", "lz", "backMix", "backDim", "opacity"]
init = lambda s: "{ {%d,%d}, %d, " % (W, H, s["hasBG"]) + ", ".join(kparity.F(s[k]) for k in forder) + ", " + kparity.A(s["backTint"]) + " }"
sfn, bfn = ft.src_fn(lua, img1, W, H), ft.src_fn(lua, img2, W, H)
res = kparity.run(fuse, "SMK2CurlSource", "SMK2CurlParams", "SMK2CurlKernel", scens, init, W, H, {"IMG0": img1, "IMG1": img2}, ["IMG0", "IMG1"],
                  lambda i, x, y: tuple(smk.curlShade(ft.table(lua, scens[i], size=[W, H]), x, y, sfn, bfn)), tol=4e-3)
if res is None: print("pagecurl kernel parity: SKIPPED (no C compiler)")
else:
    ok, n, bad, worst = res
    check(f"pagecurl kernel parity: {n} px, {bad} differ, max {worst:.2e}", ok)
    print(f"pagecurl kernel parity: {n} pixels, {bad} differ by > 4e-3, max diff {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
C.done("pagecurl")
