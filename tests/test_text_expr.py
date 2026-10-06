"""SMK Text: evaluate the generated amount expression AND the whole linked Calculation chain in a Lua sandbox;
compare engines with the tested smk_core library."""
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
EXPR = r'Expression = "((?:[^"\\]|\\.)*)"'
unesc = lambda e: e.replace('\\"', '"').replace("\\\\", "\\")

def load(name):
    s = open(os.path.join(ROOT, f"dist/templates/{name}.setting")).read()
    nodes = {}
    for node, body in re.findall(r"^\t{4}(UIT_\w+) = Calculation \{(.*?)^\t{4}\},", s, re.M | re.S):
        d = {"first_link": None, "first_expr": None, "op": 0, "second_expr": None, "second_val": 0.0}
        m = re.search(r'FirstOperand = Input \{ SourceOp = "(\w+)"', body); d["first_link"] = m.group(1) if m else None
        m = re.search(r'FirstOperand = Input \{ Expression = "((?:[^"\\]|\\.)*)"', body); d["first_expr"] = unesc(m.group(1)) if m else None
        m = re.search(r"Operator = Input \{ Value = (\d+)", body); d["op"] = int(m.group(1)) if m else 0
        m = re.search(r'SecondOperand = Input \{ Expression = "((?:[^"\\]|\\.)*)"', body); d["second_expr"] = unesc(m.group(1)) if m else None
        m = re.search(r"SecondOperand = Input \{ Value = ([-\d.]+)", body); d["second_val"] = float(m.group(1)) if m else 0.0
        nodes[node] = d
    return s, nodes

TEXT = "SMK TEXT DEMO"
def setup(t_frames, rate=24, rs=0, re_=119, text=TEXT, **ctl):
    d = dict(InDelay=0.0, InDur=0.5, Stagger=0.04, Engine=1.0, Stiff=180.0, Damp=18.0, Over=1.70158, Fade=0.0, SlideDist=0.03,
             SlideAngle=-90.0, Scale=0.5, Rot=20.0, Blur=4.0, HasOut=0.0, OutOffset=0.0, OutDur=0.5)
    d.update(ctl)
    g = lua.globals()
    t = lua.table_from(d); t.Text = lua.table_from({"Value": text}); g.UIT_Ctrl = t
    g.time = t_frames
    g.comp = lua.eval("function(rate, rs, re_) return { RenderStart = rs, RenderEnd = re_, GetPrefs = function(self, k) return rate end } end")(rate, rs, re_)

def value(nodes, name, memo=None):
    """Evaluate a Calculation node (chain of links, operators, expressions) at the current globals."""
    n = nodes[name]
    first = value(nodes, n["first_link"]) if n["first_link"] else float(lua.execute("return " + n["first_expr"]))
    second = float(lua.execute("return " + n["second_expr"])) if n["second_expr"] else n["second_val"]
    return {2: first * second, 5: second - first}.get(n["op"], first + second)

s, N = load("SMK2_TextLetter")
check("chain nodes present", {"UIT_Amt", "UIT_Dist", "UIT_PreOp", "UIT_Opacity", "UIT_PreScale", "UIT_Scale", "UIT_AngleZ", "UIT_Blur"} <= set(N))
amount_expr = N["UIT_Amt"]["first_expr"]
check("only ONE long expression (amount); the rest are tiny", len(amount_expr) > 900 and all(len(e) < 40 for k, v in N.items() if k != "UIT_Amt" for e in [v["second_expr"] or ""]))
check("amount expression within Fusion's ~2300-char limit", len(amount_expr) < 2300)
check("auto count: no manual Count control, text length used", "#UIT_Ctrl.Text.Value" in amount_expr and "Count" not in s.split("Tools = ordered()")[0].replace("Count", "", 0) or "UIT_Ctrl_Count" not in s)
check("follower Text is an expression on the holder text", re.search(r'Text = Input \{ Expression = "UIT_Ctrl.Text"', s) is not None)

def a_at(t, **c):
    setup(t, **c); return float(lua.execute("return " + amount_expr))
check("pre-delay / before In: fully offset", near(a_at(-5), 1) and near(a_at(-1), 1))
check("hold: settled", near(a_at(60), 0, 1e-3))
# whole chain at start and settled
setup(-3); v = {k: value(N, k) for k in ("UIT_Dist", "UIT_Opacity", "UIT_Scale", "UIT_AngleZ", "UIT_Blur")}
check("chain at start: dist=SlideDist, opacity=Fade(0), scale=0.5, rot=20, blur=4", near(v["UIT_Dist"], 0.03) and near(v["UIT_Opacity"], 0) and near(v["UIT_Scale"], 0.5) and near(v["UIT_AngleZ"], 20) and near(v["UIT_Blur"], 4))
setup(60); v = {k: value(N, k) for k in ("UIT_Dist", "UIT_Opacity", "UIT_Scale", "UIT_AngleZ", "UIT_Blur")}
check("chain settled: dist 0, opacity 1, scale 1, rot 0, blur 0", near(v["UIT_Dist"], 0, 1e-3) and near(v["UIT_Opacity"], 1, 1e-3) and near(v["UIT_Scale"], 1, 1e-3) and near(v["UIT_AngleZ"], 0, 1e-2) and near(v["UIT_Blur"], 0, 5e-2))
setup(-3, Fade=0.5); check("Fade 0.5 starts at 0.5 opacity", near(value(N, "UIT_Opacity"), 0.5))

cfg = lambda **k: lua.table_from(k)
for eng, name in ((1, "spring"), (2, "bounce"), (3, "elastic"), (4, "overshoot"), (5, "inertia")):
    worst = max(abs(a_at(f, Engine=float(eng)) - (1 - smk.evalEngine(eng + 1, f / 24, 0.5, cfg(stiffness=180, damping=18, mass=1, amp=1, period=0.3, s=1.70158, k=4)))) for f in range(30))
    check(f"engine {name} matches smk_core (max diff {worst:.1e})", worst < 2e-3)
check("ease engine monotonic, ends at rest", near(a_at(12, Engine=0.0), 0, 1e-6) and a_at(3, Engine=0.0) > a_at(6, Engine=0.0) > a_at(9, Engine=0.0))
d = 0.04 * 24
vals = [a_at(6 - i * d) for i in range(5)]
check("later letters are further from rest at the same frame", all(vals[i] <= vals[i + 1] + 1e-9 for i in range(4)))

# Out with the count taken from the text: every letter fully gone on the last frame (follower shifts time by i*delay)
for text in ("SMK TEXT DEMO", "ONE TWO THREE", "HELLO", "A", "éüÈ ÀBC", "A😀B"):
    n = len(text)
    worst = min(a_at(119 - i * d, HasOut=1.0, Engine=0.0, text=text) for i in range(n))
    check(f"Out ('{text}'): every letter fully offset on the last frame (min a = {worst:.3f})", worst > 1 - 1e-3)
check("Out: letter 0 is mid-exit at frame 100 (leaves first)", 0 < a_at(100, HasOut=1.0, Engine=0.0) < 1)
check("fps independent (24 vs 60 at equal seconds)", near(a_at(6, Engine=1.0), (setup(15, rate=60, re_=299) or float(lua.execute("return " + amount_expr)))))
check("clip-relative: RenderStart offset ignored", near(a_at(6, Engine=1.0), (setup(106, rs=100, re_=219) or float(lua.execute("return " + amount_expr))), 1e-9))
check("follower Delay expression is seconds->frames", "GetPrefs" in re.search(r'Delay = Input \{ Expression = "(.*?)", \}', s).group(1))

# ---- Word / Line macros: stagger per unit, Out finishes at the last frame based on the LAST UNIT's own start index ----
def unit_checks(macro, texts, unit):
    s2, N2 = load(macro)
    amt = N2["UIT_Amt"]["first_expr"]
    delay = re.search(r'Delay = Input \{ Expression = "((?:[^"\\]|\\.)*)"', s2); delay = unesc(delay.group(1))
    check(f"{macro}: expressions contain no raw newline characters", "\n" not in amt and "\n" not in delay)
    for text in texts:
        setup(0, text=text, HasOut=1.0, Engine=0.0, Stagger=0.1)
        d_lua = float(lua.execute("return " + delay)) / 24                      # follower delay per character, seconds
        n = len(text.split()) if unit == "word" else max(1, len([q for q in text.split("\n") if q]))
        L = len(text) - 1                                                        # last CHARACTER: opacity is per character
        d_exp = 0.1 * n / max(1, len(text))
        check(f"{macro} '{text[:12]!r}': per-character delay = Stagger*units/chars ({d_lua:.4f}s)", near(d_lua, d_exp, 1e-6))
        sh = L * d_exp * 24
        setup(119 - sh, text=text, HasOut=1.0, Engine=0.0, Stagger=0.1); end = float(lua.execute("return " + amt))
        setup(116 - sh, text=text, HasOut=1.0, Engine=0.0, Stagger=0.1); early = float(lua.execute("return " + amt))
        check(f"{macro} '{text[:12]!r}': LAST CHARACTER fully out on the last frame (a={end:.3f}) and not before frame ~117 (a@-3f={early:.3f})", end > 0.999 and early < 0.999)
        # the last unit's own motion may finish early by (unit length - 1) * d at most
        first = len(text) - len((text.split()[-1] if unit == "word" else text.split("\n")[-1]))
        lag_frames = (L - first) * d_exp * 24
        check(f"{macro} '{text[:12]!r}': last unit's slide finishes at most 7 frames early ({lag_frames:.1f})", lag_frames <= 7)
unit_checks("SMK2_TextWord", ["ONE TWO THREE", "HELLO", "A", "ONE TWO", "éüÈ ÀBC", "A😀B"], "word")
unit_checks("SMK2_TextLine", ["LINE ONE\nLINE TWO\nLINE THREE", "HELLO", "A", "AB\nCD", "éü\nÈ À😀"], "line")
print(f"text expressions: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
