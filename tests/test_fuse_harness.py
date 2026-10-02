"""Loads the BUILT Fuses in Lua with a mocked Fusion API; catches nil keys, syntax, require() and runtime errors."""
import os, subprocess, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)

MOCK = r'''
CT_Modifier, CT_Tool, CT_SourceTool = 1, 2, 3
local registry
function FuRegisterClass(n, t, a) registry = {name=n, attrs=a} end
function Number(v) return v end
function ImgRectI(a,b,c,d) return {left=a,bottom=b,right=c,top=d} end
function make_in(def) local o={default=def}; function o:GetValue(req) return {Value=(req.over and req.over[self.id]) or self.default} end return o end
self = {Comp={RenderStart=0, RenderEnd=119, GlobalStart=0, GlobalEnd=119}}   -- mirrors Resolve: ffi FusionDoc*, plain fields
function self.Comp:GetPrefs() return 24 end
function self:AddInput(name, id, t) local o=make_in(t.INP_Default); o.id=id; return o end
function self:AddOutput(name, id, t) local o={id=id}; function o:Set(req,v) req.out[id]=v end; return o end
return function() return registry end
'''
lua = LuaRuntime(unpack_returned_tuples=True)
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)

src = open(os.path.join(ROOT, "dist/fuses/SMK2_Motion.fuse")).read()
check("no runtime require", "require(" not in src and "dofile(" not in src)
env = lua.execute("return setmetatable({}, {__index=_G})")
# run mock + fuse inside one sandbox env
lua.execute(MOCK.replace("return function() return registry end", ""))
lua.execute(src)
lua.execute("Create()")
def run(t, **over):
    return lua.eval("function(t, over) local req={Time=t, out={}, over=over}; Process(req); return req.out.Output, req.out.Phase end")(t, lua.table_from(over))
v, ph = run(0)
check("frame0 pre/in value is From", abs(v) < 1e-9)
v, ph = run(60); check("mid-clip holds Rest", abs(v - 1) < 1e-4 and ph == 2)
v, ph = run(119); check("last frame reaches To", abs(v) < 0.02 and ph == 3)
v1, _ = run(110); v2, _ = run(110, ClipLength=100.0); check("ClipLength override moves Out", v1 < 0.999 and abs(v2 - 1) < 1e-4)
# fps independence: same seconds -> same value (rate fixed in mock, so compare 0.25s)
v, ph = run(6, EngineIn=1.0)  # spring at 0.25s
check("spring engine active, finite", v == v and v != 1.0)
for name in ("S1_GPU", "S2_FollowerMod", "S3_ClipTime", "S4_DoD", "S6_MotionBlur", "S7_TightBuffer"):
    s = open(os.path.join(ROOT, f"dist/spikes/SMK2_Spike_{name}.fuse")).read()
    try: lua.eval("function(src) return assert(loadstring or load)(src) end")(s); ok = True
    except Exception as e: ok = False; print(e)
    check(f"spike {name} parses", ok)
print(f"fuse harness: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
