"""Unit tests for smk_core v2. Runs the real Lua source through lupa."""
import math, os, sys
from lupa import LuaRuntime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lua = LuaRuntime(unpack_returned_tuples=True)
smk = lua.execute(open(os.path.join(ROOT, "src/core/smk_core.lua")).read())

passed = failed = 0
def check(name, cond):
    global passed, failed
    if cond: passed += 1
    else: failed += 1; print("FAIL:", name)
def near(a, b, e=1e-4): return abs(a - b) <= e
def cfg(**k): return lua.table_from(k)

# timing
tin, tout, os_ = smk.timing(2.0, 5.0, 0.5, 2, 0.1, 0.25, 0.5)
check("tin includes delay+stagger", near(tin, 2.0 - 0.7))
check("out start anchors to clip end", near(os_, 5.0 - 0.25 - 0.5))
check("frames->seconds fps-independent", near(smk.framesToSeconds(30, 0, 30), smk.framesToSeconds(60, 0, 60)))
check("clip seconds", near(smk.clipSeconds(0, 59, 30), 2.0))

# bezier
check("bezier endpoints", smk.cubicBezier(.25,.1,.25,1,0)==0 and smk.cubicBezier(.25,.1,.25,1,1)==1)
check("bezier linear", near(smk.cubicBezier(0,0,1,1,0.37), 0.37, 1e-5))
check("css ease mid", near(smk.cubicBezier(.25,.1,.25,1,.5), 0.8024, 2e-3))
prev = -1; mono = True
for i in range(101):
    v = smk.cubicBezier(.42,0,.58,1,i/100); mono &= v >= prev - 1e-9; prev = v
check("bezier monotonic", mono)

# spring: real-time, unclamped, no end jump
check("spring x(0)=0", smk.spring(0, 180, 18, 1) == 0)
check("spring zero initial velocity", abs(smk.spring(1e-4, 180, 18, 1)) < 1e-5)
for (k, c, m, name) in [(180, 8, 1, "under"), (180, 2*math.sqrt(180), 1, "critical"), (180, 60, 1, "over")]:
    check(f"spring {name} settles", near(smk.spring(6.0, k, c, m), 1.0, 1e-4))
    check(f"spring {name} finite", all(math.isfinite(smk.spring(i/10, k, c, m)) for i in range(100)))
peak = max(smk.spring(i/1000, 180, 8, 1) for i in range(1, 3000))
zeta = 8/(2*math.sqrt(180)); check("overshoot matches theory", near(peak-1, math.exp(-math.pi*zeta/math.sqrt(1-zeta**2)), 2e-3))
# no jump: v1 clamped to 1 at end of duration; v2 must be continuous at any sample step
ds = [abs(smk.spring((i+1)/240, 120, 6, 1) - smk.spring(i/240, 120, 6, 1)) for i in range(1440)]
check("spring continuous at 240Hz", max(ds) < 0.05)
check("spring settle time sane", 0.2 < smk.springSettleTime(180, 18, 1, 0.001) < 3)

# other engines
for name, f in [("bounce", smk.bounce), ("elastic", lambda p: smk.elastic(p,1,.3)),
                ("overshoot", lambda p: smk.overshoot(p,1.70158)), ("inertia", lambda p: smk.inertia(p,4))]:
    check(f"{name} endpoints", near(f(0), 0, 1e-9) and near(f(1), 1, 1e-9))
check("overshoot exceeds 1", max(smk.overshoot(i/100, 1.70158) for i in range(100)) > 1.05)
check("inertia monotonic", all(smk.inertia(i/100,4) <= smk.inertia((i+1)/100,4) for i in range(100)))

# value(): independent in/out engines, only active phase evaluated
tm = cfg(inDelay=0, index=0, stagger=0, outOffset=0, outDur=0.5, inDur=0.5, hasOut=True)
ci = cfg(engine=2, stiffness=180, damping=18, mass=1)
co = cfg(engine=1, x1=.4, y1=0, x2=.2, y2=1)
v, ph = smk.value(0.0, 4.0, 0, 1, 0, tm, ci, co); check("pre/in start", near(v, 0) and ph in ("in", "pre"))
v, ph = smk.value(2.0, 4.0, 0, 1, 0, tm, ci, co); check("hold rest", near(v, 1, 1e-4) and ph == "hold")
v, ph = smk.value(3.75, 4.0, 0, 1, 0, tm, ci, co); check("out mid", 0 < v < 1 and ph == "out")
v, ph = smk.value(4.0, 4.0, 0, 1, 0, tm, ci, co); check("out end = to", near(v, 0, 1e-3))
tm2 = cfg(inDelay=0, index=3, stagger=0.1, outOffset=0, outDur=0.5, inDur=0.5, hasOut=False)
v, ph = smk.value(0.25, 4.0, 0, 1, 0, tm2, ci, co); check("stagger delays start", ph == "pre" and v == 0)
# clip length change moves Out (live follow)
a = smk.value(3.0, 3.2, 0, 1, 0, tm, ci, co)[0]; b = smk.value(3.0, 6.0, 0, 1, 0, tm, ci, co)[0]
check("out follows clip length", a < b)

# stagger
n = 6
check("forward", [smk.staggerIndex(i, n, 1, 0) for i in range(n)] == list(range(n)))
check("reverse", [smk.staggerIndex(i, n, 2, 0) for i in range(n)] == list(reversed(range(n))))
co_ = [smk.staggerIndex(i, n, 3, 0) for i in range(n)]; check("center-out symmetric", co_ == co_[::-1] and min(co_) == 0.5)
ei = [smk.staggerIndex(i, n, 4, 0) for i in range(n)]; check("edges-in ends zero", ei[0] == 0 and ei[-1] == 0)
r = sorted(smk.staggerIndex(i, 9, 5, 42) for i in range(9)); check("random is permutation", r == list(range(9)))
check("random deterministic", [smk.staggerIndex(i,9,5,7) for i in range(9)] == [smk.staggerIndex(i,9,5,7) for i in range(9)])
check("random seed changes order", [smk.staggerIndex(i,9,5,1) for i in range(9)] != [smk.staggerIndex(i,9,5,2) for i in range(9)])
check("hash in 32-bit range", all(0 <= smk.hash32(i) < 2**32 for i in range(1000)))

print(f"smk_core: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
