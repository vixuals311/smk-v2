"""Product macros (Stat card number expression, Card stack geometry, Click demo wiring, style presets): the generated expressions are EXECUTED here."""
import os, re, subprocess, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/make_macros.py")], stdout=subprocess.DEVNULL)
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
def setting(name): return open(os.path.join(ROOT, "dist/templates", name + ".setting")).read()
def expr_of(s, node, inp):
    blk = re.search(rf"^\t{{4}}{node} = [\w.]+ \{{(.*?)^\t{{4}}\}},", s, re.M | re.S).group(1)
    m = re.search("\t" + inp + r' = Input \{ Expression = "((?:[^"\\]|\\.)*)"', blk)
    return m.group(1).replace('\\"', '"').replace("\\\\", "\\") if m else None
lua = LuaRuntime(unpack_returned_tuples=True)

# ---- Stat card number
s = setting("SMK2_StatCard")
e = expr_of(s, "UIS_Num", "StyledText")
check("stat number expression found, within the length budget", e is not None and len(e) < 2300)
def number(frame, **ctrl):
    c = dict(Value=12480.0, Decimals=0.0, Commas=1.0, Prefix="", Suffix="", InDelay=0.3, InDur=1.4, Engine=0.0, Stiff=120.0, Damp=18.0, Over=1.7, HasOut=0.0, OutOffset=0.0, OutDur=0.5, Weight=4.0)
    c.update(ctrl)
    lua.execute("UIS_Ctrl = {}")
    for k, v in c.items(): lua.globals().UIS_Ctrl[k] = v
    lua.execute("comp = { RenderStart = 0, RenderEnd = 239 }; function comp:GetPrefs() return 24 end")
    lua.globals().time = frame
    return lua.eval("(function() return " + e + " end)()")
check("starts at 0 before the delay", number(0) == "0" and number(int(0.2 * 24)) == "0")
mid = number(int(1.0 * 24)); check("counts up in between (value between 0 and the target, with a comma)", 0 < int(mid.replace(",", "")) < 12480)
check("ends exactly on the target with thousands separator", number(int(3 * 24)) == "12,480")
check("monotone while counting (Ease)", all(int(number(f).replace(",", "")) <= int(number(f + 1).replace(",", "")) for f in range(7, 40)))
check("no separator when off", number(100, Commas=0.0) == "12480")
check("prefix and suffix", number(100, Prefix="$", Suffix="K") == "$12,480K")
check("decimals", number(100, Value=3.14159, Decimals=2.0) == "3.14" and number(100, Value=2.5, Decimals=1.0) == "2.5")
check("small numbers and zero", number(100, Value=999.0) == "999" and number(100, Value=0.0) == "0" and number(100, Value=1000.0) == "1,000")
check("million", number(100, Value=1234567.0) == "1,234,567")
check("spring engine overshoots then settles on the target", max(int(number(f, Engine=1.0).replace(",", "")) for f in range(7, 90)) > 12480 and number(200, Engine=1.0) == "12,480")
check("delay shifts the start", number(int(1.2 * 24), InDelay=1.0) == "0" or int(number(int(1.2 * 24), InDelay=1.0).replace(",", "")) < int(number(int(1.2 * 24), InDelay=0.3).replace(",", "")))

# ---- Card stack geometry
s = setting("SMK2_CardStack")
cy4 = expr_of(s, "UIL_S4", "CY")
def card_y(expr, cy1=0.72, h=0.07, gap=0.015):
    lua.execute("UIL_S1 = { CY = %f, H = %f }; UIL_Ctrl = { Gap = %f }; comp = {}; function comp:GetPrefs(k) if k:find('Width') then return 1920 else return 1080 end end" % (cy1, h, gap))
    return lua.eval("(function() return " + expr + " end)()")
exp = 0.72 - 3 * (0.07 + 0.015) * 1920 / 1080
check("card 4 sits 3 pitches below card 1 (pitch = height + gap in frame-width units, converted to height units)", abs(card_y(cy4) - exp) < 1e-9)
check("cards 2..4 follow card 1 for size/colour (linked, not copied)", all(f'{k} = Input {{ SourceOp = "UIL_S1", Source = "{k}", }}' in s for k in ("W", "H", "FillAR", "SCA", "BW")))
check("each animator has its own Index 0..3 and mirrors the first animator's timing", all(f"Index = Input {{ Value = {i}, }}" in s for i in range(4)) and "InDelay = Input { Expression = \"UIL_A1.InDelay\"" in s)
check("four independent text controls published", len(re.findall(r"Label\d_Text = InstanceInput", s)) == 4)
check("only the first card's stagger is published", s.count("Stagger Between Cards") == 1)

# ---- Click demo
s = setting("SMK2_ClickDemo")
check("cursor's second waypoint follows the button centre", expr_of(s, "UID_Cursor", "P2") == "Point(UID_Card.CX, UID_Card.CY)")
check("cursor start is published (draggable)", "Cursor Start (drag in viewer)" in s and "Cursor_P1" in s)
check("button below the cursor in the merge order", re.search(r'UID_Over = Merge \{.*?Background = Input \{ SourceOp = "UID_Animator".*?Foreground = Input \{ SourceOp = "UID_Cursor"', s, re.S) is not None)

# ---- Presets
names = sorted(f[:-8] for f in os.listdir(os.path.join(ROOT, "dist/templates")))
for base in ("SMK2_UIBlock", "SMK2_CardStack", "SMK2_StatCard", "SMK2_ClickDemo"):
    for st in ("Glass", "Neon", "Soft"): check(f"preset {base}_{st} exists", f"{base}_{st}" in names)
base_s, neon = setting("SMK2_StatCard"), setting("SMK2_StatCard_Neon")
check("preset renames the macro and changes only defaults", "SMK2_StatCard_Neon = GroupOperator" in neon and neon.count("InstanceInput") == base_s.count("InstanceInput") and neon != base_s)
check("neon border is cyan", re.search(r"BCG = Input \{ Value = 0\.9", neon) is not None)
glass = setting("SMK2_UIBlock_Glass"); check("glass fill is translucent", re.search(r"FillAA = Input \{ Value = 0\.12", glass) is not None)
check("preset names unique and valid macro names", len(names) == len(set(names)) and all(re.fullmatch(r"SMK2_\w+", n) for n in names))
print(f"products: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
