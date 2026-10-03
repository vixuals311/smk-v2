"""SMK Text expressions: run the generated Lua expressions in a sandbox and compare with the tested smk_core engines."""
import math, os, re, subprocess, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
def near(a, b, e=1e-4): return abs(a - b) <= e

lua = LuaRuntime(unpack_returned_tuples=True)
core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
smk = lua.execute("return (function()\n" + core + "\nend)()")

def exprs(name):
    s = open(os.path.join(ROOT, f"dist/templates/{name}.setting")).read()
    out = {}
    for node, body in re.findall(r"^\t{4}(UIT_\w+) = \w+ \{(.*?)^\t{4}\},", s, re.M | re.S):
        m = re.search(r'Expression = "((?:[^"\\]|\\.)*)"', body)
        if m: out[node] = m.group(1).replace('\\"', '"').replace("\\\\", "\\")
    return s, out

s, E = exprs("SMK2_TextLetter")
check("expressions found for all calc nodes", {"UIT_Dist", "UIT_Opacity", "UIT_Scale", "UIT_AngleZ", "UIT_Blur"} <= set(E))
check("every expression within Fusion's ~2300-char limit", all(len(v) < 2300 for v in E.values()))
check("no Fuse/.Output references", all(".Output" not in v for v in E.values()))

def evaluate(expr, t_frames, rate=24, rs=0, re_=119, **ctl):
    d = dict(InDelay=0.0, InDur=0.5, Stagger=0.04, Engine=1.0, Stiff=180.0, Damp=18.0, Over=1.70158, Fade=0.0, SlideDist=0.03,
             SlideAngle=-90.0, Scale=0.5, Rot=20.0, Blur=4.0, HasOut=0.0, OutOffset=0.0, OutDur=0.5, Count=12.0)
    d.update(ctl)
    g = lua.globals()
    g.UIT_Ctrl = lua.table_from(d)
    g.time = t_frames
    g.comp = lua.eval("function(rate, rs, re_) return { RenderStart = rs, RenderEnd = re_, GetPrefs = function(self, k) return rate end } end")(rate, rs, re_)
    return lua.execute("return " + expr)

amt = lambda t, **c: evaluate(E["UIT_Dist"], t, **c) / 0.03          # Dist = SlideDist * a
check("pre-delay: fully offset", near(amt(-5), 1))
check("before In (t<0)", near(amt(-1), 1))
check("hold: settled", near(amt(60), 0, 1e-3))
check("Opacity = Fade at start, 1 when settled", near(evaluate(E["UIT_Opacity"], -3), 0) and near(evaluate(E["UIT_Opacity"], 60), 1, 1e-3))
check("Scale: 0.5 at start", near(evaluate(E["UIT_Scale"], -3), 0.5))
check("Rotation: 20 at start, 0 settled", near(evaluate(E["UIT_AngleZ"], -3), 20) and near(evaluate(E["UIT_AngleZ"], 60), 0, 1e-2))
check("Blur: 4 at start", near(evaluate(E["UIT_Blur"], -3), 4))

# engines vs the tested core (spring is real-time; others use p = tau/dur)
cfg = lambda **k: lua.table_from(k)
for eng, name in ((1, "spring"), (2, "bounce"), (3, "elastic"), (4, "overshoot"), (5, "inertia")):
    worst = 0.0
    for f in range(0, 30):
        tau = f / 24
        a_expr = amt(f, Engine=float(eng))
        a_core = 1 - smk.evalEngine(eng + 1, tau, 0.5, cfg(stiffness=180, damping=18, mass=1, amp=1, period=0.3, s=1.70158, k=4))
        worst = max(worst, abs(a_expr - a_core))
    check(f"engine {name} matches smk_core (max diff {worst:.1e})", worst < 2e-3)
check("ease engine: 0 → 1 monotonic, ends at rest", near(amt(12, Engine=0.0), 0, 1e-6) and amt(3, Engine=0.0) > amt(6, Engine=0.0) > amt(9, Engine=0.0))

# stagger via shifted time: follower evaluates at t - i*delay
d = 0.04 * 24
vals = [amt(6 - i * d) for i in range(5)]
check("later letters are further from rest at the same frame", all(vals[i] <= vals[i + 1] + 1e-9 for i in range(4)))
# Out: letters leave in order and all are gone by the last frame (shifted by index)
n, st = 12, 0.04
for i in (0, 5, 11):
    last = amt(119 - i * st * 24, HasOut=1.0, Engine=0.0, Count=float(n))
    check(f"Out: letter {i} fully offset at the last frame", near(last, 1, 1e-3))
mid = amt(100, HasOut=1.0, Engine=0.0, Count=12.0)
check("Out: letter 0 is mid-exit at frame 100 (leaves first)", 0 < mid < 1)
check("fps independent (24 vs 60 at equal seconds)", near(amt(6, Engine=1.0), evaluate(E["UIT_Dist"], 15, rate=60, re_=299) / 0.03, 1e-6))
check("clip-relative: RenderStart offset ignored", near(amt(6, Engine=1.0), evaluate(E["UIT_Dist"], 6 + 100, rs=100, re_=219) / 0.03, 1e-9))
check("follower Delay expression is seconds→frames", "GetPrefs" in re.search(r'UIT_Follower = StyledTextFollower \{.*?Delay = Input \{ Expression = "(.*?)", \}', s, re.S).group(1))
print(f"text expressions: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
