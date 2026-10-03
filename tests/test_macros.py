"""Generated macros: structure, wiring, and published controls checked against the REAL Fuse input lists."""
import os, re, subprocess, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/make_macros.py")], stdout=subprocess.DEVNULL)
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)

MOCK = r'''
CT_Modifier, CT_Tool, CT_SourceTool = 1, 2, 3
function FuRegisterClass() end
function make_in(def) return {} end
self = {Comp={}}
IDS = {}
function self:AddInput(name, id, t) IDS[#IDS+1] = id; return {id=id} end
function self:AddOutput(name, id, t) return {id=id} end
function self:BeginControlNest() end; function self:EndControlNest() end
'''
def fuse_keys(name):
    lua = LuaRuntime(); lua.execute(MOCK)
    lua.execute(open(os.path.join(ROOT, f"dist/fuses/{name}.fuse")).read()); lua.execute("Create()")
    return set(lua.eval("IDS").values())
KEYS = {"Fuse.SMK2_Shape": fuse_keys("SMK2_Shape"), "Fuse.SMK2_Animator": fuse_keys("SMK2_Animator"), "Fuse.SMK2_Motion": fuse_keys("SMK2_Motion") | {"Output"}}
KEYS["Fuse.SMK2_Shape"] |= {"Output"}; KEYS["Fuse.SMK2_Animator"] |= {"Output", "Image"}
TEXTPLUS = {"StyledText", "Font", "Style", "Size", "Red1", "Green1", "Blue1", "Alpha1", "Center", "Angle", "Output"}
KEYS["TextPlus"] = TEXTPLUS; KEYS["Merge"] = {"Output", "Background", "Foreground"}
E1 = open(os.path.join(ROOT, "docs/phase4_evidence/S8_E1_all_inputs.md")).read()
KEYS["StyledTextFollower"] = set(re.findall(r"^\| \d+ \| `(\w+)` \|", E1, re.M)) | {"StyledText"}   # all 475 real follower inputs (S8 E1)
KEYS["Calculation"] = {"FirstOperand", "SecondOperand", "Operator", "Result"}
KEYS["Vector"] = {"Origin", "Distance", "Angle", "ImageAspect", "Position"}
KEYS["Background"] = {"TopLeftAlpha", "Output"}
EXPR = r'Expression = "((?:[^"\\]|\\.)*)"'
def user_controls(s, node):
    m = re.search(rf"^\t{{4}}{node} = [\w.]+ \{{\n\t{{5}}UserControls = ordered\(\) \{{(.*?)^\t{{5}}\}},", s, re.M | re.S)
    return set(re.findall(r"^\t{6}(\w+) = \{", m.group(1), re.M)) if m else set()

for path in sorted(os.listdir(os.path.join(ROOT, "dist/templates"))):
    s = open(os.path.join(ROOT, "dist/templates", path)).read()
    check(f"{path}: braces balanced", s.count("{") == s.count("}"))
    check(f"{path}: no CustomData.Path leak", "CustomData" not in s and "Path =" not in s)
    check(f"{path}: no hardcoded absolute paths", not re.search(r"[A-Za-z]:\\\\|/Users/|/home/", s))
    nodes = {k: v for k, v in re.findall(r"^\t{4}(\w+) = ([\w.]+) \{", s, re.M) if v not in ("InstanceInput", "InstanceOutput")}
    check(f"{path}: has nodes", len(nodes) >= 3)
    for n in list(nodes):
        uc = user_controls(s, n)
        if uc: KEYS[n + "#user"] = uc
    kk = lambda n: KEYS.get(nodes[n], set()) | KEYS.get(n + "#user", set())
    pubs = re.findall(r'(\w+) = InstanceInput \{\s+SourceOp = "(\w+)",\s+Source = "(\w+)"', s)
    keys = [k for k, _, _ in pubs]
    check(f"{path}: published keys unique", len(keys) == len(set(keys)))
    bad = [(op, src) for _, op, src in pubs if op not in nodes or src not in kk(op)]
    check(f"{path}: every published control exists on its node {bad[:3]}", not bad)
    links = re.findall(r'SourceOp = "(\w+)", Source = "(\w+)"', s)
    check(f"{path}: every link targets an existing node/output", all(op in nodes and src in kk(op) for op, src in links))
    pos = re.findall(r"OperatorInfo \{ Pos = \{ (-?\d+), (-?\d+) \}", s)
    is_text = "Text" in path
    check(f"{path}: nodes at distinct positions (readable graph)", len(pos) == len(set(pos)) == len(nodes))
    check(f"{path}: expression length within limits (<90 chars, text <2300)", all(len(e) < (2300 if is_text else 90) for e in re.findall(EXPR, s)))
    # DAG: forward-only (no cycles) through links+expressions
    deps = {n: set() for n in nodes}
    for n in nodes:
        block = re.search(rf"^\t{{4}}{n} = [\w.]+ \{{(.*?)^\t{{4}}\}},", s, re.M | re.S).group(1)
        deps[n] |= set(re.findall(r'SourceOp = "(\w+)"', block)) | {m for m in nodes if re.search(rf"\b{m}\.", " ".join(re.findall(EXPR, block)))}
    def cyc(n, seen=()):
        return n in seen or any(cyc(d, seen + (n,)) for d in deps[n])
    check(f"{path}: acyclic graph", not any(cyc(n) for n in nodes))
    blocks = re.findall(r"= InstanceInput \{(.*?)\n\t{4}\},", s, re.S)
    groups = {}
    for b in blocks:
        g = re.search(r"ControlGroup = (\d+)", b)
        if g: groups.setdefault(g.group(1), []).append("Name =" in b)
    check(f"{path}: colour pickers grouped (>=3 groups, 3-4 channels, one Name each)", len(groups) >= (1 if is_text else 3) and all(len(v) in (3, 4) and v.count(True) == 1 and v[0] for v in groups.values()))
    check(f"{path}: label rotates with card (AngleZ)", "UIB_Shape.Angle" in s or "Progress" in path or is_text)
    check(f"{path}: no .Output socket in expressions (v1 rule)", not re.search(r'Expression = "(?:[^"\\]|\\.)*\.Output', s))
    check(f"{path}: expression targets exist (tool.Input)", all(m in nodes and i in (kk(m) | {"AngleZ"}) for m, i in re.findall(r"\b(UI[BPT]_\w+)\.(\w+)", " ".join(re.findall(EXPR, s)))))
    check(f"{path}: published control count > {20 if is_text else 60}", len(pubs) > (20 if is_text else 60))
print(f"macros: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
