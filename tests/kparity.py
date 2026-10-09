"""Shared helper: compile a Fuse's real GPU kernel on the CPU (C shim for the DVIP macros) and compare every pixel with a Lua oracle.
Works for kernels that read up to N source textures (nearest-texel shim) and write one output."""
import math, os, re, shutil, subprocess, tempfile

def F(v): s = f"{float(v):.9g}"; return (s if ("." in s or "e" in s or "n" in s) else s + ".0") + "f"
def A(a): return "{" + ",".join(F(v) for v in a) + "}"

def make_image(W, H, rng, blobs=5):
    img = [[(0.0, 0.0, 0.0, 0.0)] * W for _ in range(H)]
    for _ in range(blobs):
        cx, cy, rx, ry = rng.uniform(20, W - 20), rng.uniform(12, H - 12), rng.uniform(6, 24), rng.uniform(5, 16)
        cr, cg, cb, ca = rng.random(), rng.random(), rng.random(), rng.choice([1.0, 0.8, 0.5])
        for y in range(H):
            for x in range(W):
                d = math.hypot((x + .5 - cx) / rx, (y + .5 - cy) / ry)
                if d < 1:
                    a = ca * min(1.0, (1 - d) * 4); o = img[y][x]; k = 1 - a
                    img[y][x] = (cr * a + o[0] * k, cg * a + o[1] * k, cb * a + o[2] * k, a + o[3] * k)
    return img

def run(fuse_text, source_var, params_var, kernel_name, scens, init_fn, W, H, images, tex_names, oracle, tol=3e-3, max_bad_frac=0.003):
    """images: {name: rows of (r,g,b,a)}; tex_names: kernel texture argument names in order (e.g. ["IMG0", "IMG1"]); oracle(scen_index, x, y) -> (r,g,b,a).
    Returns (ok, n, bad, worst) or None if no compiler."""
    cc = shutil.which("gcc") or shutil.which("cc")
    if not cc: return None
    kernel = re.search(rf"{source_var} = \[\[(.*?)\]\]", fuse_text, re.S).group(1)
    fields = re.search(rf"{params_var} = \[\[(.*?)\]\]", fuse_text, re.S).group(1).replace("\n", " ")
    decl = "".join(f"static const float {n}[] = {{ {','.join(F(v) for row in images[n] for p in row for v in p)} }};\n" for n in tex_names)
    c = f"""
#include <math.h>
#include <stdio.h>
typedef struct {{ float x,y,z,w; }} float4;
static float4 make_float4(float x,float y,float z,float w){{float4 r={{x,y,z,w}};return r;}}
#define __KERNEL__ static
#define __CONSTANTREF__ const
#define __TEXTURE2D__ const float*
#define __TEXTURE2D_WRITE__ float4*
#define DEFINE_KERNEL_ITERATORS_XY(x,y) int x=gx, y=gy
#define _tex2DVec4Write(dst,x,y,c) (dst)[(y)*{W}+(x)] = (c)
static float4 _tex2DVecN(const float* s, float u, float v, int n) {{
  int ix = (int)floorf(u * {W}.0f), iy = (int)floorf(v * {H}.0f);
  if (ix < 0) ix = 0; if (ix > {W-1}) ix = {W-1}; if (iy < 0) iy = 0; if (iy > {H-1}) iy = {H-1};
  const float* q = s + 4 * (iy * {W} + ix); return make_float4(q[0], q[1], q[2], q[3]); }}
typedef struct {{ {fields} }} {params_var.replace('Params', '')}Params_t;
static int gx, gy;
{decl}
{kernel}
int main() {{
  static float4 out[{W*H}];
  static {params_var.replace('Params', '')}Params_t S[] = {{ {",".join(init_fn(s) for s in scens)} }};
  for (int i = 0; i < {len(scens)}; ++i) for (gy = 0; gy < {H}; ++gy) for (gx = 0; gx < {W}; ++gx) {{
    {kernel_name}(&S[i], {", ".join(tex_names)}, out);
    float4 c = out[gy*{W}+gx]; printf("%d %d %d %.6f %.6f %.6f %.6f\\n", i, gx, gy, c.x, c.y, c.z, c.w); }}
  return 0; }}
"""
    # kernel signature uses the struct type name from the Fuse (e.g. SMK2ReliefParams): alias it
    pname = params_var
    c = c.replace(f"{params_var.replace('Params', '')}Params_t", pname)
    d = tempfile.mkdtemp(); open(d + "/k.c", "w").write(c)
    r = subprocess.run([cc, "-O1", "-o", d + "/k", d + "/k.c", "-lm"], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[:3000])
    out = subprocess.run([d + "/k"], capture_output=True, text=True).stdout.split("\n")
    n = bad = 0; worst = 0.0
    for line in out:
        if not line: continue
        i, x, y, *cv = line.split(); i, x, y = int(i), int(x), int(y); cv = list(map(float, cv))
        o = oracle(i, x, y); n += 1
        df = max(abs(a - b) for a, b in zip(cv, o)); worst = max(worst, df)
        if df > tol: bad += 1
    ok = n == len(scens) * W * H and bad / max(n, 1) <= max_bad_frac
    return ok, n, bad, worst
