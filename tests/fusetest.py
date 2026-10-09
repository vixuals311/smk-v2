"""Shared test scaffolding for per-pixel Fuses: Lua runtime with smk_core + one module, a Fuse API mock, and image helpers."""
import math, os, re, subprocess, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Counter:
    def __init__(self): self.passed = self.failed = 0
    def check(self, n, c):
        if c: self.passed += 1
        else: self.failed += 1; print("FAIL:", n)
    def done(self, label):
        print(f"{label}: {self.passed} passed, {self.failed} failed"); sys.exit(1 if self.failed else 0)

def build():
    subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)

def oracle(module):
    core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
    mod = re.search(r"-- SMK2_MOD_BEGIN\n(.*?)-- SMK2_MOD_END", open(os.path.join(ROOT, f"src/core/{module}.lua")).read(), re.S).group(1)
    lua = LuaRuntime(unpack_returned_tuples=True)
    smk = lua.execute("local smk = (function()\n" + core + "\nend)()\n" + mod + "\nreturn smk")
    return lua, smk, lua.table_from

def src_fn(lua, img, W, H):
    T = lua.table_from
    return lua.eval("function(img, W, H) return function(sx, sy) if sx < 0 or sy < 0 or sx > W or sy > H then return 0, 0, 0, 0 end local ix = math.min(math.max(math.floor(sx), 0), W - 1) local iy = math.min(math.max(math.floor(sy), 0), H - 1) local p = img[iy + 1][ix + 1] return p[1], p[2], p[3], p[4] end end")(
        T([T([T(list(p)) for p in row]) for row in img]), W, H)

def rect_image(W, H, x0, x1, y0, y1, color=(1.0, 1.0, 1.0), a=1.0):
    return [[(color[0] * a, color[1] * a, color[2] * a, a) if (x0 <= x < x1 and y0 <= y < y1) else (0.0, 0.0, 0.0, 0.0) for x in range(W)] for y in range(H)]

def table(lua, d, **extra):
    t = lua.table()
    for k, v in {**d, **extra}.items(): t[k] = lua.table_from(v) if isinstance(v, list) else v
    return t

MOCK = r'''
CT_Tool = 2
TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE = 1, 2, 3
function FuRegisterClass() end
IMG = {Width=1920, Height=1080}
IMG2 = {Width=1920, Height=1080}
function ImgRectI(l,b,r,t) return {left=l,bottom=b,right=r,top=t} end
function Image(a) local o={Width=a.IMG_Like and a.IMG_Like.Width, Height=a.IMG_Like and a.IMG_Like.Height, DataWindow=a.IMG_DataWindow}; return o end
LAST, ADDED = nil, {}
function DVIPComputeNode(req, k, src, pname, pdef)
  assert(src:find("__KERNEL__") and pdef:find("float opacity"))
  local n = {}
  function n:GetParamBlock() return {} end
  function n:SetParamBlock(b) LAST = b end
  function n:AddSampler() end
  function n:AddInput(name, img) ADDED[#ADDED + 1] = name end
  function n:AddOutput() end
  function n:RunSession() return not FAIL end
  return n
end
function self_input(t, id)
  local o = {id=id, t=t}
  function o:GetValue(req)
    if self.id == "Image" then if NOIMG then return nil end return IMG end
    if self.id == "Reveal" then if NOREV then return nil end return IMG2 end
    return {Value = (req.over and req.over[self.id]) or self.t.INP_Default}
  end
  return o
end
self = {Comp={RenderStart=0, RenderEnd=119}}
function self.Comp:GetPrefs() return 24 end
function self:AddInput(name, id, t) return self_input(t, id) end
function self:AddOutput(name, id, t) local o={id=id}; function o:Set(req,v) req.out=v end; return o end
'''

def load_fuse(lua, name):
    lua.execute(MOCK)
    src = open(os.path.join(ROOT, f"dist/fuses/{name}.fuse")).read()
    lua.execute(src); lua.execute("Create()")
    run = lua.eval("""function(t, over, pre, fail, noimg, norev) FAIL=fail; NOIMG=noimg; NOREV=norev; LAST=nil; ADDED={}
      local req={Time=t, over=over}; function req:IsPreCalc() return pre end; Process(req); return LAST, req.out, ADDED end""")
    def frame(t, pre=False, fail=False, noimg=False, norev=False, **o): return run(t, lua.table_from(o), pre, fail, noimg, norev)
    return src, frame
