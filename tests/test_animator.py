"""SMK2_Animator: CPU stage + GPU dispatch contract, with a mocked Fusion/DVIP API."""
import os, subprocess, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)
MOCK = r'''
CT_Modifier, CT_Tool, CT_SourceTool = 1, 2, 3
TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE = 1, 2, 3
function FuRegisterClass(n, t, a) end
function Number(v) return v end
function Image(a) local o = {Width=a.IMG_Like and a.IMG_Like.Width, Height=a.IMG_Like and a.IMG_Like.Height}; return o end
LAST = nil
function DVIPComputeNode(req, k, src, pname, pdef)
  assert(pdef:find("float opacity"), "param struct"); assert(src:find("__KERNEL__"), "kernel")
  local n = {block={}}
  function n:GetParamBlock() return self.block end
  function n:SetParamBlock(b) LAST = b end
  function n:AddSampler() end; function n:AddInput() end; function n:AddOutput() end
  function n:RunSession() return not FAIL end
  return n
end
function make_in(def) local o={default=def}; function o:GetValue(req) if self.id=="Image" then return IMG end return {Value=(req.over and req.over[self.id]) or self.default} end return o end
self = {Comp={RenderStart=0, RenderEnd=119}}
function self.Comp:GetPrefs() return 24 end
function self:AddInput(name, id, t) local o=make_in(t.INP_Default); o.id=id; return o end
function self:AddOutput(name, id, t) local o={id=id}; function o:Set(req,v) req.out=v end; return o end
function self:BeginControlNest() end; function self:EndControlNest() end
IMG = {Width=1920, Height=1080}
'''
lua = LuaRuntime(unpack_returned_tuples=True)
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
src = open(os.path.join(ROOT, "dist/fuses/SMK2_Animator.fuse")).read()
check("no runtime require", "require(" not in src and "dofile(" not in src)
lua.execute(MOCK); lua.execute(src); lua.execute("Create()")
run = lua.eval("""function(t, over, pre, fail)
  FAIL = fail; LAST = nil
  local req = {Time=t, over=over}; function req:IsPreCalc() return pre end
  Process(req); return LAST, req.out end""")
def frame(t, pre=False, fail=False, **o):
    return run(t, lua.table_from(o), pre, fail)
b, out = frame(0, InEngine=0.0, InDelay=0.0)
check("frame0 fully offset: opacity 0", b is not None and abs(b.opacity) < 1e-6)
check("slide 180deg moves left", b.trans[1] < -100 and abs(b.trans[2]) < 1e-3)
check("size passed", b.size[1] == 1920 and b.size[2] == 1080)
b, _ = frame(60); check("hold is identity", abs(b.opacity - 1) < 1e-3 and abs(b.trans[1]) < 1e-2 and abs(b.invScale - 1) < 1e-6)
b, _ = frame(119, OutEngine=0.0); check("last frame offset by Out", b.opacity < 0.05)
b, out = frame(10, pre=True); check("PreCalc skips GPU", b is None and out is not None)
b, out = frame(0, fail=True); check("GPU failure passes input through", lua.eval("function(o) return rawequal(o, IMG) end")(out))
b, _ = frame(0, InEngine=0.0, PivotX=0.0, PivotY=0.0); check("pivot in pixels", b.pivot[1] == 0 and b.pivot[2] == 0)
b9, _ = frame(10, InEngine=0.0, Index=0.0, Stagger=0.0); bs, _ = frame(10, InEngine=0.0, Index=5.0, Stagger=0.1)
check("stagger delays", bs.opacity < b9.opacity)
print(f"animator: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
