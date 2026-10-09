"""smk_connector: magnetic ports, path builders (curve / straight / elbow / bezier handles / spline through points) and the reference pixel function."""
import math, os, re, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lua = LuaRuntime(unpack_returned_tuples=True)
core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
mod = re.search(r"-- SMK2_MOD_BEGIN\n(.*?)-- SMK2_MOD_END", open(os.path.join(ROOT, "src/core/smk_connector.lua")).read(), re.S).group(1)
smk = lua.execute("local smk = (function()\n" + core + "\nend)()\n" + mod + "\nreturn smk")
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
def near(a, b, e=1e-3): return abs(a - b) <= e
T = lua.table_from
box0 = lambda: T(dict(hw=0, hh=0, mag=0))
def spec(**k):
    d = dict(mode=2, pa=(40, 100), pb=(260, 100), h1=(100, 160), h2=(200, 40), mid=[], bend=0.45, tension=1, radius=0, gap=0, aBox=box0(), bBox=box0())
    d.update(k)
    return T({kk: (T(list(v)) if isinstance(v, tuple) else (T([T(list(m)) for m in v]) if kk == "mid" else v)) for kk, v in d.items()})
def pts(path): return [(path.pts[i][1], path.pts[i][2]) for i in range(1, path.n + 1)]

# ---- magnetic ports
mp = lambda c, hw, hh, mag, to, gap=0: smk.magnetPoint(T(list(c)), hw, hh, mag, T(list(to)), gap)
p, n = mp((100, 100), 40, 20, 1, (300, 100)); check("auto: exits right edge toward the target", near(p[1], 140) and near(p[2], 100) and n[1] == 1 and n[2] == 0)
p, n = mp((100, 100), 40, 20, 1, (100, 300)); check("auto: exits the top edge", near(p[1], 100) and near(p[2], 120) and n[2] == 1)
p, n = mp((100, 100), 40, 20, 1, (300, 300)); check("auto: diagonal exits where the ray meets the box (top edge)", near(p[1], 120) and near(p[2], 120) and n[2] == 1)
p, n = mp((100, 100), 40, 20, 2, (0, 0)); check("side ports: top / right / bottom / left", near(p[2], 120) and near(mp((100, 100), 40, 20, 3, (0, 0))[0][1], 140) and near(mp((100, 100), 40, 20, 4, (0, 0))[0][2], 80) and near(mp((100, 100), 40, 20, 5, (0, 0))[0][1], 60))
p, n = mp((100, 100), 40, 20, 3, (0, 0), 8); check("gap pushes the end outward along the normal", near(p[1], 148))
p, n = mp((100, 100), 40, 20, 0, (0, 0)); check("off: centre unchanged, no normal", near(p[1], 100) and n is None)

# ---- paths
s = smk.connPath(spec(mode=2)); check("straight: 2 points, length = distance", s.n == 2 and near(s.total, 220))
c = smk.connPath(spec(mode=1)); P = pts(c)
check("curve: starts at A, ends at B", near(P[0][0], 40) and near(P[-1][0], 260) and near(P[0][1], 100) and near(P[-1][1], 100))
check("curve: arclength monotonic and sums to total", all(c.cum[i] <= c.cum[i + 1] for i in range(1, c.n)) and near(c.cum[c.n], c.total))
check("curve between level points has no bulge when aligned", max(abs(y - 100) for _, y in P) < 1e-6)
c = smk.connPath(spec(mode=1, pa=(40, 60), pb=(260, 160), aBox=T(dict(hw=20, hh=10, mag=3)), bBox=T(dict(hw=20, hh=10, mag=5))))
P = pts(c); check("curve with right->left ports leaves A and arrives at B horizontally", near(P[0][0], 60) and abs(P[1][1] - P[0][1]) < 3 and P[1][0] > P[0][0] and near(P[-1][0], 240) and abs(P[-2][1] - P[-1][1]) < 3)
check("S-curve passes through the mid-point of its ends", min(math.hypot(x - 150, y - 110) for x, y in P) < 2.5)
# bezier handles
b0 = smk.connPath(spec(mode=4, h1=(40, 100), h2=(260, 100))); b1 = smk.connPath(spec(mode=4, h1=(100, 180), h2=(200, 20)))
check("bezier: endpoints exact", near(pts(b1)[0][0], 40) and near(pts(b1)[-1][0], 260))
check("bezier: handles shape the curve (above toward H1, below toward H2)", max(y for _, y in pts(b1)) > 115 and min(y for _, y in pts(b1)) < 85 and max(abs(y - 100) for _, y in pts(b0)) < 1e-6)
bm = smk.connPath(spec(mode=4, aBox=T(dict(hw=20, hh=10, mag=3)))); check("bezier with a magnet: start snapped to the box edge", near(pts(bm)[0][0], 60, 1e-6))
# spline through points
mid = [(100, 150), (160, 60), (210, 140)]
sp = smk.connPath(spec(mode=5, mid=mid)); Q = pts(sp)
check("spline passes through every editable point (<= 0.6 px)", all(min(math.hypot(x - mx, y - my) for x, y in Q) < 0.6 for mx, my in mid))
check("spline starts/ends at A/B and has <= 96 points", near(Q[0][0], 40) and near(Q[-1][0], 260) and sp.n <= 192)
tight = smk.connPath(spec(mode=5, mid=mid, tension=0.0)); check("tension 0 gives a polyline through the points; different from tension 1", min(math.hypot(x - 100, y - 150) for x, y in pts(tight)) < 0.1 and sp.total != tight.total)
# elbow
e = smk.connPath(spec(mode=3, pa=(40, 60), pb=(260, 160), radius=0)); E = pts(e)
check("elbow (radius 0): every segment is axis-aligned", all(abs(E[i][0] - E[i + 1][0]) < 1e-6 or abs(E[i][1] - E[i + 1][1]) < 1e-6 for i in range(len(E) - 1)))
er = smk.connPath(spec(mode=3, pa=(40, 60), pb=(260, 160), radius=20)); check("elbow with radius: corners cut (shorter) and smooth (more points)", er.total < e.total + 1e-6 and er.n > e.n)
c = smk.connPath(spec(mode=2)); pa_ = smk.connPointAt(c, 110); check("point at arclength", near(pa_[1], 150) and near(pa_[2], 100))
# ---- reference pixel function
def shader(path, **k):
    flat = []
    for i in range(1, path.n + 1): flat += [path.pts[i][1], path.pts[i][2]]
    cum = [path.cum[i] for i in range(1, path.n + 1)]
    mk0 = dict(kind=0, cx=0, cy=0, r=0, tri=[0] * 6)
    d = dict(n=path.n, pts=flat, cum=cum, total=path.total, thick=6, trim=1, dash=0, dgap=0, colA=[1, 0, 0, 1], colB=[0, 0, 1, 1], gradOn=0,
             mkA=mk0, mkB=mk0, pul=[[0, 0, 0, 0]] * 3, pulCol=[1, 1, 1, 1], opacity=1)
    d.update(k)
    t = lua.table()
    for key, v in d.items():
        if key in ("mkA", "mkB"): t[key] = T({a: (T(b) if isinstance(b, list) else b) for a, b in v.items()})
        elif key == "pul": t[key] = T([T(q) for q in v])
        elif isinstance(v, list): t[key] = T(v)
        else: t[key] = v
    return t
px = lambda t, x, y: tuple(smk.connShade(t, x, y))
ln = smk.connPath(spec(mode=2)); S = shader(ln)
check("line body is solid colour A", px(S, 150, 99)[3] > 0.99 and px(S, 150, 99)[0] > 0.99)
check("outside the stroke is transparent", px(S, 150, 110)[3] == 0 and px(S, 10, 100)[3] == 0)
check("gradient from A to B along arclength", px(shader(ln, gradOn=1), 60, 99)[0] > 0.8 and px(shader(ln, gradOn=1), 240, 99)[2] > 0.8)
check("draw-on: trim 0.5 shows the first half only", px(shader(ln, trim=0.5), 100, 99)[3] > 0.99 and px(shader(ln, trim=0.5), 200, 99)[3] < 0.05)
check("trim 0 draws nothing", px(shader(ln, trim=0.0), 100, 99)[3] < 0.05)
dsh = shader(ln, dash=20, dgap=10)
check("dash pattern: on 10 px into a dash, off in the gap, on again", px(dsh, 40 + 10, 99)[3] > 0.99 and px(dsh, 40 + 25, 99)[3] < 0.05 and px(dsh, 40 + 40, 99)[3] > 0.99)
dotB = dict(kind=1, cx=260, cy=100, r=9, tri=[0] * 6)
check("dot at end B shows only when fully drawn", px(shader(ln, mkB=dotB), 260, 108)[3] > 0.5 and px(shader(ln, trim=0.6, mkB=dotB), 260, 108)[3] < 0.05)
check("dot at A is visible from the start", px(shader(ln, trim=0.3, mkA=dict(kind=1, cx=40, cy=100, r=9, tri=[0] * 6)), 40, 108)[3] > 0.5)
tri = [270, 100, 250, 108, 250, 92]
check("arrow marker (triangle) at B", px(shader(ln, mkB=dict(kind=2, cx=0, cy=0, r=0, tri=tri)), 255, 100)[3] > 0.99 and px(shader(ln, mkB=dict(kind=2, cx=0, cy=0, r=0, tri=tri)), 255, 120)[3] == 0)
check("pulse dot over the line", px(shader(ln, pul=[[150, 100, 7, 0.9], [0, 0, 0, 0], [0, 0, 0, 0]], pulCol=[1, 1, 0, 1]), 150, 105)[3] > 0.5)
check("opacity premultiplied", near(px(shader(ln, opacity=0.5), 150, 99)[3], 0.5, 1e-6))
print(f"connector core: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
