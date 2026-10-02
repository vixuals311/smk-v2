"""SMK2_MotionRig with mocked Fusion API."""
import os, subprocess, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)
MOCK = r'''
CT_Modifier = 1
function FuRegisterClass() end
function Number(v) return v end
function Point(x, y) return {x=x, y=y} end
function make_in(def) local o={default=def}; function o:GetValue(req) return {Value=(req.over and req.over[self.id]) or self.default} end return o end
self = {Comp={RenderStart=0, RenderEnd=119}}
function self.Comp:GetPrefs(k) if k:find("Width") then return 1920 elseif k:find("Height") then return 1080 end return 24 end
function self:AddInput(name, id, t) local o=make_in(t.INP_Default); o.id=id; return o end
function self:AddOutput(name, id, t) local o={id=id}; function o:Set(req,v) req.o = req.o or {}; req.o[id]=v end; return o end
'''
lua = LuaRuntime(unpack_returned_tuples=True)
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
src = open(os.path.join(ROOT, "dist/fuses/SMK2_MotionRig.fuse")).read()
check("no runtime require", "require(" not in src and "dofile(" not in src)
lua.execute(MOCK); lua.execute(src); lua.execute("Create()")
run = lua.eval("function(t, over) local req={Time=t, over=over}; Process(req); return req.o end")
def f(t, **o): return run(t, lua.table_from(o))
o = f(0, InEngine=0.0)
check("frame0 invisible", abs(o.Opacity) < 1e-9)
check("slide left: x<0.5, y~0.5", o.Center.x < 0.45 and abs(o.Center.y - 0.5) < 1e-6)
check("hold identity", all(abs(v) < 1e-3 for v in (f(60).OffsetX, f(60).OffsetY, f(60).Angle)) and abs(f(60).Opacity - 1) < 1e-3 and abs(f(60).Scale-1) < 1e-6)
o = f(0, InEngine=0.0, InSlideAngle=90.0, InSlideDist=0.1)
check("vertical slide aspect-corrected (0.1*1920/1080)", abs(o.OffsetY - 0.1 * 1920 / 1080) < 1e-6)
check("last frame fades via Out", f(119, OutEngine=0.0).Opacity < 0.05)
check("scale/angle at offset", abs(f(0, InEngine=0.0, InScale=0.5, InRot=90.0).Scale - 0.5) < 1e-6 and abs(f(0, InEngine=0.0, InRot=90.0).Angle - 90) < 1e-6)
check("stagger delays", f(10, InEngine=0.0, Index=5.0, Stagger=0.1).Opacity < f(10, InEngine=0.0).Opacity)
check("base center moves output", abs(f(60, BaseX=0.2).Center.x - 0.2) < 1e-3)
print(f"motion rig: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
