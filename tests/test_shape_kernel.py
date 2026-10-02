"""Compile the REAL SMK2_Shape GPU kernel source on the CPU (C shim for the DVIP macros) and compare every pixel
with the Lua oracle smk.shade(). Guards the hand-ported kernel against drift. Skipped if no C compiler."""
import os, random, re, shutil, subprocess, sys, tempfile
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cc = shutil.which("gcc") or shutil.which("cc")
if not cc: print("kernel parity: SKIPPED (no C compiler)"); sys.exit(0)
subprocess.check_call([sys.executable, os.path.join(ROOT, "build/build.py")], stdout=subprocess.DEVNULL)
fuse = open(os.path.join(ROOT, "dist/fuses/SMK2_Shape.fuse")).read()
fields = re.search(r"SMK2ShapeParams = \[\[(.*?)\]\]", fuse, re.S).group(1)
kernel = re.search(r"SMK2ShapeSource = \[\[(.*?)\]\]", fuse, re.S).group(1)

W, H = 96, 54
random.seed(7)
def scen():
    s = random.choice([0, 1, 2, 3])
    return dict(shape=s, fillMode=random.choice([0, 1, 2]), borderPos=random.choice([0, 1, 2]),
        center=(random.uniform(30, 66), random.uniform(18, 36)), half=(random.uniform(8, 30), random.uniform(5, 18)),
        radius=random.uniform(0, 12), thick=random.uniform(2, 10), bw=random.choice([0, 2, 4]),
        ang=random.uniform(0, 6.28), gang=random.uniform(0, 6.28), trim=random.choice([1, 0.7, 0.25]), trimStart=random.choice([0, 0.3]),
        shadowOff=(random.uniform(-5, 5), random.uniform(-5, 5)), shadowBlur=random.uniform(0, 8), opacity=random.choice([1, 0.6]),
        fillA=[random.random() for _ in range(3)] + [random.choice([1, 0.7])], fillB=[random.random() for _ in range(3)] + [1],
        borderCol=[random.random() for _ in range(3)] + [1], shadowCol=[random.random() for _ in range(3)] + [random.choice([0, 0.5])])
scens = [scen() for _ in range(8)]
import math
def cinit(s):
    F = lambda v: f"{float(v):.9g}f" if "." in f"{float(v):.9g}" or "e" in f"{float(v):.9g}" else f"{float(v):.9g}.0f"
    f = lambda a: "{" + ",".join(F(v) for v in a) + "}"
    return (f"{{ {{{W},{H}}}, {s['shape']}, {s['fillMode']}, {s['borderPos']}, {f(s['center'])}, {f(s['half'])}, "
            f"{F(s['radius'])}, {F(s['thick'])}, {F(s['bw'])}, {F(math.cos(s['ang']))}, {F(math.sin(s['ang']))}, "
            f"{F(math.cos(s['gang']))}, {F(math.sin(s['gang']))}, {F(s['trim'])}, {F(s['trimStart'])}, {f(s['shadowOff'])}, "
            f"{F(s['shadowBlur'])}, {F(s['opacity'])}, {f(s['fillA'])}, {f(s['fillB'])}, {f(s['borderCol'])}, {f(s['shadowCol'])} }}")
body = re.sub(r"(\w+)\s+(\w+)\[(\d)\];", r"\1 \2[\3];", fields)
c = f"""
#include <math.h>
#include <stdio.h>
typedef struct {{ float x,y,z,w; }} float4;
static float4 make_float4(float x,float y,float z,float w){{float4 r={{x,y,z,w}};return r;}}
#define __KERNEL__ static
#define __CONSTANTREF__ const
#define __TEXTURE2D_WRITE__ float4*
#define DEFINE_KERNEL_ITERATORS_XY(x,y) int x=gx, y=gy
#define _tex2DVec4Write(dst,x,y,c) (dst)[(y)*{W}+(x)] = (c)
typedef struct {{ {body.replace(chr(10), ' ')} }} SMK2ShapeParams;
static int gx, gy;
{kernel.replace('return;', 'return;')}
int main() {{
  static float4 img[{W*H}];
  SMK2ShapeParams S[] = {{ {",".join(cinit(s) for s in scens)} }};
  for (int i = 0; i < {len(scens)}; ++i) for (gy = 0; gy < {H}; ++gy) for (gx = 0; gx < {W}; ++gx) {{
    SMK2ShapeKernel(&S[i], img);
    float4 c = img[gy*{W}+gx]; printf("%d %d %d %.6f %.6f %.6f %.6f\\n", i, gx, gy, c.x, c.y, c.z, c.w); }}
  return 0; }}
"""
d = tempfile.mkdtemp(); open(d + "/k.c", "w").write(c)
r = subprocess.run([cc, "-O1", "-o", d + "/k", d + "/k.c", "-lm"], capture_output=True, text=True)
if r.returncode: print(r.stderr[:2000]); print("kernel parity: COMPILE FAILED"); sys.exit(1)
out = subprocess.run([d + "/k"], capture_output=True, text=True).stdout.split("\n")

lua = LuaRuntime(unpack_returned_tuples=True)
core = open(os.path.join(ROOT, "src/core/smk_core.lua")).read()
mod = re.search(r"-- SMK2_MOD_BEGIN\n(.*?)-- SMK2_MOD_END", open(os.path.join(ROOT, "src/core/smk_shape.lua")).read(), re.S).group(1)
smk = lua.execute("local smk = (function()\n" + core + "\nend)()\n" + mod + "\nreturn smk")
def tab(s):
    t = lua.table(); t.size = lua.table_from([W, H]); t.shape = s['shape']; t.fillMode = s['fillMode']; t.borderPos = s['borderPos']
    for k in ('center', 'half', 'shadowOff', 'fillA', 'fillB', 'borderCol', 'shadowCol'): t[k] = lua.table_from(list(s[k]))
    for k in ('radius', 'thick', 'bw', 'trim', 'trimStart', 'shadowBlur', 'opacity'): t[k] = s[k]
    t.cosA, t.sinA, t.gradC, t.gradS = math.cos(s['ang']), math.sin(s['ang']), math.cos(s['gang']), math.sin(s['gang'])
    return t
T = [tab(s) for s in scens]
worst = 0.0; n = 0
for line in out:
    if not line: continue
    i, x, y, *c = line.split(); i, x, y = int(i), int(x), int(y); c = list(map(float, c))
    o = list(smk.shade(T[i], x, y)); n += 1
    worst = max(worst, max(abs(a - b) for a, b in zip(c, o)))
ok = n == len(scens) * W * H and worst < 2e-3
print(f"kernel parity: {n} pixels, max |kernel - oracle| = {worst:.2e} -> {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
