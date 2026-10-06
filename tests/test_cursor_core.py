"""smk_cursor: path / click timeline and reference pixel function."""
import math, os, re, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lua = LuaRuntime(unpack_returned_tuples=True)
core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
mod = re.search(r"-- SMK2_MOD_BEGIN\n(.*?)-- SMK2_MOD_END", open(os.path.join(ROOT, "src/core/smk_cursor.lua")).read(), re.S).group(1)
smk = lua.execute("local smk = (function()\n" + core + "\nend)()\n" + mod + "\nreturn smk")
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
def near(a, b, e=1e-3): return abs(a - b) <= e
T = lua.table_from
wp = T([T(dict(x=0.2, y=0.3, move=0, hold=0.5, click=False)), T(dict(x=0.8, y=0.7, move=1.0, hold=0.5, click=True)), T(dict(x=0.5, y=0.2, move=0.8, hold=0.2, click=True))])
o = T(dict(n=3, startDelay=0.5, arc=0.0, ease=1, clickDelay=0.1, pressDur=0.2, pressAmt=0.15, rippleDur=0.6, fadeIn=0.2, fadeOut=0.3, T=6.0, aspect=16 / 9))
st = lambda t, **k: (o.__setitem__("arc", k.get("arc", 0.0)) or o.__setitem__("ease", k.get("ease", 1)) or smk.cursorState(t, wp, o))

arrive, depart = smk.cursorTimeline(wp, o)
check("timeline: first arrival = startDelay", near(arrive[1], 0.5) and near(depart[1], 1.0))
check("timeline: move and hold accumulate", near(arrive[2], 2.0) and near(depart[2], 2.5) and near(arrive[3], 3.3) and near(depart[3], 3.5))
s = st(0.0); check("before start: at first waypoint, invisible", near(s.x, 0.2) and near(s.y, 0.3) and s.opacity < 1e-6)
s = st(0.9); check("hold at waypoint 1", near(s.x, 0.2) and near(s.y, 0.3))
s = st(2.0); check("arrives exactly at waypoint 2", near(s.x, 0.8, 1e-4) and near(s.y, 0.7, 1e-4))
s = st(1.5); check("mid-move strictly between", 0.2 < s.x < 0.8 and 0.3 < s.y < 0.7)
check("smooth ease is symmetric: half time = half way", near(st(1.5).x, 0.5, 0.01))
check("moves monotonically", all(st(1.0 + i * 0.05).x <= st(1.0 + (i + 1) * 0.05).x + 1e-9 for i in range(19)))
s = st(5.0); check("rests at the last waypoint", near(s.x, 0.5) and near(s.y, 0.2))
# arc: bulge perpendicular, zero at both ends, isotropic (aspect-corrected)
m = st(1.5, arc=0.2); l = st(1.5, arc=0.0)
check("arc leaves endpoints alone", near(st(1.0, arc=0.2).x, 0.2) and near(st(2.0, arc=0.2).x, 0.8, 1e-4))
dx, dy = (m.x - l.x) * 16 / 9, (m.y - l.y); mv = (0.6 * 16 / 9, 0.4)
check("arc displacement is perpendicular to the move", abs(dx * mv[0] + dy * mv[1]) < 1e-6 and math.hypot(dx, dy) > 0.01)
# spring ease may overshoot, then settles
sp = [st(1.0 + i * 0.02, ease=3).x for i in range(60)]
check("spring ease overshoots then settles", max(sp) > 0.8 and near(st(2.45, ease=3).x, 0.8, 0.01))
# clicks
s = st(2.0 + 0.1 + 0.1); check("press dip at mid-press", s.press < 0.9)
check("no press before click", st(2.05).press == 1 and st(2.5).press == 1)
r = st(2.1 + 0.3).ripples; check("ripple active, expanding and fading", len(r) == 1 and 0 < r[1].r < 1 and 0 < r[1].a < 1 and near(r[1].x, 0.8))
check("ripple gone after duration", len(st(2.1 + 0.7).ripples) == 0)
check("overlapping ripples are separate", len(st(3.3 + 0.1 + 0.3).ripples) >= 1)
# fades
check("fade in", 0 < st(0.4).opacity < 1 and near(st(1.0).opacity, 1) and near(st(3.0).opacity, 1))
check("fade out at the last frame", st(6.0).opacity < 1e-6 and 0 < st(5.9).opacity < 1)

# ---- reference pixel function
def P(**k):
    d = dict(tip=(100, 100), S=60, press=1, fillCol=(1, 1, 1, 1), borderCol=(0, 0, 0, 1), bw=2, shadowCol=(0, 0, 0, 0), shadowOff=(2, -3),
             shadowBlur=3, rip=((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)), ripCol=(0.2, 0.5, 1, 1), ripThick=4, opacity=1)
    d.update(k); t = lua.table()
    for key, v in d.items():
        t[key] = lua.table_from([lua.table_from(list(x)) if isinstance(x, tuple) else x for x in v]) if isinstance(v, tuple) and isinstance(v[0], tuple) else (lua.table_from(list(v)) if isinstance(v, tuple) else v)
    return t
px = lambda p, x, y: tuple(smk.cursorShade(p, x, y))
check("pointer body is filled (inside the shaft)", px(P(), 100 + 8, 100 - 25)[3] > 0.99)
check("outside the pointer is transparent", px(P(), 100 - 20, 100 + 20)[3] == 0 and px(P(), 100 + 80, 100 - 30)[3] == 0)
check("border band is dark, interior white", px(P(), 100, 100 - 20)[3] > 0.9 and px(P(), 100 + 7, 100 - 28)[0] > 0.9)
check("tip is at the hot spot", px(P(), 100, 99)[3] > 0.5)
check("press scales about the tip", px(P(press=0.5), 100 + 6, 100 - 24)[3] < 0.5 and px(P(), 100 + 6, 100 - 24)[3] > 0.5)
rp = P(rip=((100, 100, 40, 0.8), (0, 0, 0, 0), (0, 0, 0, 0)))
check("ripple ring visible at its radius, empty inside/outside", px(rp, 100 + 40, 100)[3] > 0.7 and px(rp, 100 + 20, 100 + 20)[3] < 0.05 and px(rp, 100 + 70, 100)[3] == 0)
check("opacity premultiplied", abs(px(P(opacity=0.5), 100 + 8, 100 - 25)[3] - 0.5) < 1e-6)
sh = P(shadowCol=(0, 0, 0, 0.5), shadowOff=(0, -10), shadowBlur=4); check("shadow appears below the tip, none far away", px(sh, 100 + 6, 100 - 56)[3] > 0.0 and px(sh, 100 + 150, 100)[3] == 0)
print(f"cursor core: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
