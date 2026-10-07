# SMK Motion Engines — portable reference

Everything needed to reuse the SMK v2 motion maths in another plugin or chat, without redoing the work. Source of truth: `src/core/smk_core.lua`
(Lua 5.1 / LuaJIT-safe, no `require`, no bitwise operators), unit-tested (49 tests) and cross-checked against the closed-form expressions used inside
Fusion macros (62 more). Paste this whole file into the other chat.

---

## 1. Timing model (all values in SECONDS, relative to the clip)

* `t` = seconds from the clip start = `(frame − RenderStart) / rate`. `T` = clip length in seconds. Never use raw frames: presets then look the same at 24/30/60 fps
  and follow the clip when it is trimmed on the Edit page.
* Optional stagger: `d = Index × Stagger` (seconds).
* **In** runs from `InDelay + d` for `InDur`. **Out** ends at `T − OutOffset` and lasts `OutDur` (so it is anchored to the clip end). **Hold** is everything between.
* Each phase has its own **engine** `E` and its own normalised progress `p = clamp(τ / dur, 0, 1)` where `τ` = seconds since that phase started.
* Value: `lerp(from, rest, E_in(p_in))` during In, `lerp(rest, to, E_out(p_out))` during Out. Only the ACTIVE phase's engine is evaluated.
* **Springs are real-time**: they use `τ` in seconds (not `p`) and are allowed to keep settling after the phase "ends" (no end-of-duration jump).
  If Out starts before an In spring has settled, Out wins (the value steps from the in-flight value).
* "Amount" form used by the Animator / Text: `a = 0` settled … `1` fully offset. In: `a = 1 − E_in`. Out: `a = E_out`. Property = `rest + (offset − rest) · a`
  (e.g. opacity `1 − (1−Fade)·a`, scale `1 + (Scale−1)·a`, position `Distance·a` along the angle). Overshooting engines make `a` leave 0..1 (value passes through rest) — clamp
  opacity if you use it.
* Fusion note: the last frame of a clip is at `(RenderEnd − RenderStart) / rate` (= `T − 1/rate` if `T` counts the inclusive frames). Use whichever convention you pick for BOTH Out
  placement and tests.

## 2. Engines

`E(p)` maps 0..1 → eased 0..1 (spring: `E(τ)`). All satisfy `E(0)=0`, `E(1)=1` (spring settles to 1).

| Engine | Formula | Parameters (defaults) |
|---|---|---|
| **Ease** (CSS cubic-bezier) | Solve `x(s)=p` for the curve with control points `(0,0),(x1,y1),(x2,y2),(1,1)` (Newton, 8 iterations, then 40-step bisection fallback), return `y(s)`. | `x1,y1,x2,y2 = .25,.1,.25,1` (CSS "ease"). In-expressions (no solver): cubic-out `1 − (1−p)³` |
| **Spring** (damped, unit step, x(0)=0, x'(0)=0, target 1) | `ω0=√(k/m)`, `ζ=c/(2√(k·m))`. **ζ<1:** `1 − e^(−ζω0τ)·(cos(ωdτ) + (ζω0/ωd)·sin(ωdτ))`, `ωd=ω0√(1−ζ²)`. **ζ≈1:** `1 − e^(−ω0τ)(1+ω0τ)`. **ζ>1:** `1 − (r2·e^(r1τ) − r1·e^(r2τ))/(r2−r1)`, `r1,2=−ω0(ζ ∓ √(ζ²−1))`. | stiffness k=180, damping c=18, mass m=1 → ζ≈0.67. Unclamped (may overshoot) |
| **Bounce** (Penner ease-out) | `n1=7.5625, d1=2.75`; `p<1/d1: n1p²`; `p<2/d1: p−=1.5/d1, n1p²+.75`; `p<2.5/d1: p−=2.25/d1, n1p²+.9375`; else `p−=2.625/d1, n1p²+.984375` | none |
| **Elastic** (ease-out) | `0 / 1` at the ends; else `amp·2^(−10p)·sin((p−s)·2π/period)+1`, `s = period/(2π)·asin(1/amp)` | amp=1 (≥1), period=0.3 → s=0.075 |
| **Overshoot** (ease-out-back) | `q=p−1; 1 + (s+1)q³ + s·q²` | s=1.70158 (≈10 % overshoot) |
| **Inertia** (exponential approach, normalised) | `(1 − e^(−kp)) / (1 − e^(−k))` | k=4 |

Sample values (computed from the real code; In duration 0.5 s, `p` = τ/0.5):

| Engine | p=0 | 0.1 | 0.25 | 0.5 | 0.75 | 0.9 | 1.0 |
|---|---|---|---|---|---|---|---|
| Ease (cubic-bezier .25,.1,.25,1) | 0.0000 | 0.0948 | 0.4085 | 0.8024 | 0.9605 | 0.9943 | 1.0000 |
| Bounce | 0.0000 | 0.0756 | 0.4727 | 0.7656 | 0.9727 | 0.9881 | 1.0000 |
| Elastic (amp 1, period .3) | 0.0000 | 1.2500 | 0.9116 | 1.0156 | 1.0055 | 0.9980 | 1.0000 |
| Overshoot (s 1.70158) | 0.0000 | 0.4088 | 0.8174 | 1.0877 | 1.0641 | 1.0143 | 1.0000 |
| Inertia (k 4) | 0.0000 | 0.3358 | 0.6439 | 0.8808 | 0.9679 | 0.9908 | 1.0000 |

Spring step response (k=180, real time τ in seconds): 

| damping c | τ=0 | 0.05 | 0.1 | 0.2 | 0.3 | 0.5 | 0.75 | 1.0 | 2.0 |
|---|---|---|---|---|---|---|---|---|---|
| 18 (under-damped ζ≈0.67) | 0.0000 | 0.1644 | 0.4702 | 0.9307 | 1.0569 | 1.0068 | 0.9986 | 1.0002 | 1.0000 |
| 26.83 (critical) | 0.0000 | 0.1457 | 0.3879 | 0.7483 | 0.9102 | 0.9906 | 0.9995 | 1.0000 | 1.0000 |
| 60 (over-damped) | 0.0000 | 0.0995 | 0.2287 | 0.4379 | 0.5905 | 0.7827 | 0.9015 | 0.9554 | 0.9981 |

Useful numbers: theory for peak overshoot `exp(−πζ/√(1−ζ²))` (c=8: peak−1 = 0.3748, matches numeric); spring settle time to 0.1 % for k=180,c=18,m=1 ≈ 0.78 s.

Design notes: v1's spring was a closed form hard-clamped to 1 at the end of the duration (visible jump at low damping and "oscillations" tied to duration). v2 ties the spring to
real time and never clamps. Bounce/Elastic/Overshoot/Inertia/Ease are duration-bound (use `p`).

## 3. Stagger orders

`staggerIndex(i, n, mode, seed)` returns the 0-based delay rank (delay = rank × Stagger): 1 forward `i`; 2 reverse `n−1−i`; 3 centre-out `|i − (n−1)/2|`; 4 edges-in `(n−1)/2 − |i − (n−1)/2|`;
5 random = rank of a seeded integer hash among the n items (a true permutation, deterministic). Hash (Lua 5.1 safe, arithmetic only, exact in doubles):
`x = x mod 2^32; repeat 3×: x = (x·1664525 + 1013904223) mod 2^32; x = (x + floor(x/65536)·40503) mod 2^32`. Never use `sin()`-style hashes (precision/GPU differences).

## 4. One-expression form (for Fusion expression fields)

Fusion expressions are one Lua chunk (an immediately-invoked function works), **max ≈ 2,300 characters**, and `comp:GetPrefs("Comp.FrameFormat.Rate")`, `comp.RenderStart`, `comp.RenderEnd`,
`time` are available (`comp:GetAttrs()` is not). The amount `a` (0 settled … 1 offset) with In + Out, six engines, ~1,200 characters:

```lua
(function()
 local r=comp:GetPrefs("Comp.FrameFormat.Rate") local t=(time-comp.RenderStart)/r
 local T=(comp.RenderEnd-comp.RenderStart)/r local ti=t-InDelay local a=1
 if ti>=0 then
  local p=math.min(1,ti/math.max(InDur,0.001)) local g=Engine local e=p
  if g<0.5 then e=1-(1-p)^3
  elseif g<1.5 then local k=math.max(Stiff,1) local w=math.sqrt(k) local z=math.min(0.999,math.max(0.05,Damp/(2*w)))
   local wd=w*math.sqrt(1-z*z) e=1-math.exp(-z*w*ti)*(math.cos(wd*ti)+z*w/wd*math.sin(wd*ti))
  elseif g<2.5 then local q=p
   if q<0.3636 then e=7.5625*q*q elseif q<0.7273 then q=q-0.5454 e=7.5625*q*q+0.75
   elseif q<0.9091 then q=q-0.8182 e=7.5625*q*q+0.9375 else q=q-0.9545 e=7.5625*q*q+0.984375 end
  elseif g<3.5 then if p>0 and p<1 then e=2^(-10*p)*math.sin((p-0.075)*20.944)+1 end
  elseif g<4.5 then local q=p-1 e=1+(Over+1)*q*q*q+Over*q*q
  else e=(1-math.exp(-4*p))/(1-math.exp(-4)) end
  a=1-e
 end
 if HasOut>0.5 then
  local po=math.min(1,math.max(0,(t-(T-OutOffset-OutDur))/math.max(OutDur,0.001)))
  a=math.min(1,a+po*po*(3-2*po))        -- Out: smoothstep
 end
 return a
end)()
```
(`InDelay, InDur, Engine, Stiff, Damp, Over, HasOut, OutOffset, OutDur` are control values; in the macros they are `UIT_Ctrl.<name>`.) The spring there is under-damped only (ζ clamped to 0.05–0.999).
Verified against `smk_core` to < 2e-3 for every engine.

## 5. Fusion lessons that cost rounds (read before building the next plugin)

1. **GPU Fuses:** return early on `req:IsPreCalc()` (`DVIPComputeNode` is nil there). Kernel params struct = a bare field list (no `typedef`), arrays assigned as Lua tables, output `Image({IMG_Width,IMG_Height,IMG_Depth,IMG_DeferAlloc=true})`.
2. **Inside a Fuse**: `self.Comp.RenderStart / .RenderEnd` are plain fields (`GetAttrs()` is invalid); `self.Comp:GetPrefs("Comp.FrameFormat.Rate")` works. **File-level locals filled in `Create()` are NOT visible in `Process`** (the file is re-executed): use globals set in `Create()`.
3. **Cost:** every Fuse node or Fuse modifier ≈ 3 ms/frame/instance (and ≈ 3 ms **per letter** for a modifier bound to a Text+ follower). Prefer ONE Fuse per element; a native Calculation modifier is ~100× cheaper. Tight output buffers / DoD tricks do NOT help (`IMG_DataWindow` is the only one that works, no speed-up).
4. **Text+ per-letter animation:** `StyledTextFollower` input bound to a built-in **Calculation** whose expression reads `time` (it sees each letter's delayed time). An expression typed directly on the follower input is ignored; Fuse modifiers work but are slow. Position = `Vector` modifier on `CharacterOffset`. Share one long amount expression and feed small linked Calculations (Multiply = Operator 2; "Second − First" = 5; default = Add) — Fusion re-parses long expressions every evaluation. Follower `Delay` is in frames: `Stagger * comp:GetPrefs("Comp.FrameFormat.Rate")`.
5. **Expression rules:** never read another tool's `.Output`/`.Result` in an expression (it is an object, not a number; link it with SourceOp/Source instead); read input values (`Tool.Input`). Keep dependencies forward-only (a holder node with UserControls and no inputs; never expressions that read downstream nodes). Text input `.Value` is a string (`#UIT_Ctrl.Text.Value`); count UTF-8 characters with `select(2, s:gsub("[^\128-\191]", ""))`.
6. **Premultiplied alpha & AA:** SDF coverage `clamp(0.5 − d, 0, 1)` in pixels; premultiply colours; opacity multiplies all four channels; sizes in fractions of frame width and px-@1920 units scaled by `width/1920` so looks are resolution independent.
7. **Pasting macros:** deselect (`FlowView.Select()`) before each paste or Fusion auto-adds a Merge; a timeline set to 60 fps does NOT change a Fusion comp's own rate (set `Comp.FrameFormat.Rate`); repeat renders reuse cached frames (change the Background by 0.001 before timing).
8. **Colour controls** in macros: publish R,G,B(,A) with the same `ControlGroup`, `Name` only on the first. `Font` + `Style` publishing is unreliable (the visible Style combo does not drive the real Style input).
9. **Rotation convention:** positive angle = counter-clockwise; slide/offset angle = direction of the START offset (−90 starts below and rises).

## 6. Appendix — full Lua source (`smk_core.lua`, the part inlined into every artifact)

```lua
local smk = {}
smk.VERSION = "2.0.0-dev"

function smk.clamp(v, lo, hi) if v < lo then return lo elseif v > hi then return hi end return v end
function smk.lerp(a, b, t) return a + (b - a) * t end
function smk.sat(x) return smk.clamp(x, 0, 1) end

-- ---------------------------------------------------------------- timing ---
-- t: seconds from clip start. T: clip length (s). All offsets in seconds.
-- idx*stagger delays the In start (d); Out is anchored to the clip end.
-- Returns tin (seconds since In started, may be <0 -> 0), tout (seconds since
-- Out started, <0 means Out has not begun) and the out start time.
function smk.timing(t, T, inDelay, idx, stagger, outOffset, outDur)
  local d = (idx or 0) * (stagger or 0)
  local inStart = (inDelay or 0) + d
  local outStart = T - (outOffset or 0) - (outDur or 0)
  return t - inStart, t - outStart, outStart
end

-- Convert a clip's time in frames to seconds. rate = comp frame rate.
function smk.framesToSeconds(frame, renderStart, rate)
  return (frame - renderStart) / rate
end

-- Clip length in seconds from RenderStart/RenderEnd (inclusive frame range).
function smk.clipSeconds(renderStart, renderEnd, rate)
  return (renderEnd - renderStart + 1) / rate
end

-- --------------------------------------------------------------- easing ---
-- Every engine: f(tau, dur, params) -> value, f(0)=0, f(>=dur)->1 (spring: settles).
-- tau = seconds since phase start. dur = phase duration (s).

-- CSS-style cubic-bezier(x1,y1,x2,y2) solved with Newton + bisection fallback.
function smk.cubicBezier(x1, y1, x2, y2, x)
  if x <= 0 then return 0 elseif x >= 1 then return 1 end
  local function bx(s) local u = 1 - s; return 3*u*u*s*x1 + 3*u*s*s*x2 + s*s*s end
  local function by(s) local u = 1 - s; return 3*u*u*s*y1 + 3*u*s*s*y2 + s*s*s end
  local function dbx(s) local u = 1 - s; return 3*u*u*x1 + 6*u*s*(x2-x1) + 3*s*s*(1-x2) end
  local s = x
  for _ = 1, 8 do
    local err = bx(s) - x
    if math.abs(err) < 1e-7 then return by(s) end
    local d = dbx(s)
    if math.abs(d) < 1e-6 then break end
    s = s - err / d
  end
  local lo, hi = 0, 1
  s = x
  for _ = 1, 40 do
    local v = bx(s)
    if math.abs(v - x) < 1e-7 then break end
    if v < x then lo = s else hi = s end
    s = (lo + hi) * 0.5
  end
  return by(s)
end

-- Real-time damped spring unit step response. NOT clamped, NOT duration-bound.
-- stiffness k, damping c, mass m. x(0)=0, x'(0)=0, target 1.
function smk.spring(tau, k, c, m)
  if tau <= 0 then return 0 end
  k = math.max(k or 180, 1e-3); c = math.max(c or 18, 0); m = math.max(m or 1, 1e-3)
  local w0 = math.sqrt(k / m)
  local zeta = c / (2 * math.sqrt(k * m))
  if zeta < 1 - 1e-6 then
    local wd = w0 * math.sqrt(1 - zeta*zeta)
    local e = math.exp(-zeta * w0 * tau)
    return 1 - e * (math.cos(wd*tau) + (zeta*w0/wd) * math.sin(wd*tau))
  elseif zeta <= 1 + 1e-6 then
    return 1 - math.exp(-w0*tau) * (1 + w0*tau)
  else
    local s = math.sqrt(zeta*zeta - 1)
    local r1, r2 = -w0*(zeta - s), -w0*(zeta + s)
    return 1 - (r2*math.exp(r1*tau) - r1*math.exp(r2*tau)) / (r2 - r1)
  end
end

-- Time (s) after which |1-x| stays below eps, for UI/diagnostics (numeric scan).
function smk.springSettleTime(k, c, m, eps)
  eps = eps or 0.001
  local last = 0
  for i = 1, 6000 do
    local tau = i * 0.005
    if math.abs(1 - smk.spring(tau, k, c, m)) > eps then last = tau end
  end
  return last + 0.005
end

function smk.bounce(p) -- ease-out bounce (Penner), p in 0..1
  p = smk.sat(p)
  local n1, d1 = 7.5625, 2.75
  if p < 1/d1 then return n1*p*p
  elseif p < 2/d1 then p = p - 1.5/d1; return n1*p*p + 0.75
  elseif p < 2.5/d1 then p = p - 2.25/d1; return n1*p*p + 0.9375
  else p = p - 2.625/d1; return n1*p*p + 0.984375 end
end

function smk.elastic(p, amp, period) -- ease-out elastic
  p = smk.sat(p)
  if p == 0 or p == 1 then return p end
  amp = math.max(amp or 1, 1); period = period or 0.3
  local s = period / (2*math.pi) * math.asin(1/amp)
  return amp * 2^(-10*p) * math.sin((p - s) * 2*math.pi / period) + 1
end

function smk.overshoot(p, s) -- ease-out-back
  p = smk.sat(p); s = s or 1.70158
  local q = p - 1
  return 1 + (s + 1) * q*q*q + s * q*q
end

-- Inertia: exponential decay approach, normalised so f(1)=1.
function smk.inertia(p, k)
  p = smk.sat(p); k = math.max(k or 4, 1e-3)
  return (1 - math.exp(-k*p)) / (1 - math.exp(-k))
end

smk.ENGINES = { "Ease", "Spring", "Bounce", "Elastic", "Overshoot", "Inertia" }

-- Evaluate engine -> eased progress. cfg: {engine=1..6, x1,y1,x2,y2, stiffness,
-- damping, mass, amp, period, s, k}. Springs ignore dur (real time).
function smk.evalEngine(engine, tau, dur, cfg)
  if engine == 2 then return smk.spring(tau, cfg.stiffness, cfg.damping, cfg.mass) end
  local p = (dur and dur > 0) and smk.sat(tau / dur) or (tau > 0 and 1 or 0)
  if engine == 1 then return smk.cubicBezier(cfg.x1 or .25, cfg.y1 or .1, cfg.x2 or .25, cfg.y2 or 1, p)
  elseif engine == 3 then return smk.bounce(p)
  elseif engine == 4 then return smk.elastic(p, cfg.amp, cfg.period)
  elseif engine == 5 then return smk.overshoot(p, cfg.s)
  elseif engine == 6 then return smk.inertia(p, cfg.k) end
  return p
end

-- One-evaluation animated value: only the ACTIVE phase's engine runs.
-- cfgIn/cfgOut each carry .engine. Returns value, phaseName.
function smk.value(t, T, from, rest, to, tm, cfgIn, cfgOut)
  local tin, tout = smk.timing(t, T, tm.inDelay, tm.index, tm.stagger, tm.outOffset, tm.outDur)
  if tm.hasOut and tout >= 0 then
    return smk.lerp(rest, to, smk.evalEngine(cfgOut.engine, tout, tm.outDur, cfgOut)), "out"
  end
  if tin < 0 then return from, "pre" end
  local e = smk.evalEngine(cfgIn.engine, tin, tm.inDur, cfgIn)
  return smk.lerp(from, rest, e), (tin >= (tm.inDur or 0) and "hold" or "in")
end

-- Animator amount: 0 = settled at rest, 1 = fully offset (In start / Out end). May leave 0..1 for
-- springs/overshoot (value passes through rest). Returns amount, phase ("pre"|"in"|"hold"|"out").
function smk.animAmount(t, T, tm, cfgIn, cfgOut)
  local tin, tout = smk.timing(t, T, tm.inDelay, tm.index, tm.stagger, tm.outOffset, tm.outDur)
  if tm.hasOut and tout >= 0 then
    return smk.evalEngine(cfgOut.engine, tout, tm.outDur, cfgOut), "out"
  end
  if tin < 0 then return 1, "pre" end
  local e = smk.evalEngine(cfgIn.engine, tin, tm.inDur, cfgIn)
  return 1 - e, (tin >= (tm.inDur or 0) and "hold" or "in")
end

-- Inverse-mapping coefficients for the Animator kernel (pixel space, y up, angle CCW degrees).
-- m: {w,h,pivotX,pivotY (0..1), slideDist (fraction of width), slideAngle, scaleFrom, rotFrom, fadeFrom}
function smk.animXform(a, m)
  local rad = (m.slideAngle or 0) * math.pi / 180
  local d = (m.slideDist or 0) * a * m.w
  local sc = 1 + ((m.scaleFrom or 1) - 1) * a
  if sc < 1e-4 then sc = 1e-4 end
  local rot = (m.rotFrom or 0) * a * math.pi / 180
  local op = smk.clamp(1 + ((m.fadeFrom or 1) - 1) * a, 0, 1)
  return { px = m.pivotX * m.w, py = m.pivotY * m.h, tx = math.cos(rad) * d, ty = math.sin(rad) * d,
           invScale = 1 / sc, c = math.cos(rot), s = math.sin(rot), opacity = op }
end

-- Rig outputs for driving an EXISTING Merge/Transform (no extra node): opacity, scale, angle, centre offset.
-- Fusion Point inputs are normalised to width (x) and height (y), so y is multiplied by w/h to keep slides isotropic.
function smk.rigOut(a, m)
  local rad = (m.slideAngle or 0) * math.pi / 180
  local d = (m.slideDist or 0) * a
  local aspect = (m.h and m.h > 0) and (m.w / m.h) or (16 / 9)
  local sc = 1 + ((m.scaleFrom or 1) - 1) * a
  return { opacity = smk.clamp(1 + ((m.fadeFrom or 1) - 1) * a, 0, 1), scale = math.max(sc, 1e-4),
           angle = (m.rotFrom or 0) * a, dx = math.cos(rad) * d, dy = math.sin(rad) * d * aspect }
end

-- ---------------------------------------------------------------- stagger ---
-- Returns delay-order index (0-based) for unit i of n. mode: 1 forward,
-- 2 reverse, 3 center-out, 4 edges-in, 5 random(seed).
function smk.hash32(x) -- integer hash, arithmetic only (Lua 5.1/LuaJIT safe), no sin()
  local M = 4294967296
  x = (x % M)
  for _ = 1, 3 do
    x = (x * 1664525 + 1013904223) % M
    x = (x + math.floor(x / 65536) * 40503) % M
  end
  return x
end

function smk.staggerIndex(i, n, mode, seed)
  if n <= 1 then return 0 end
  if mode == 2 then return n - 1 - i
  elseif mode == 3 then return math.abs(i - (n - 1) / 2)
  elseif mode == 4 then return (n - 1) / 2 - math.abs(i - (n - 1) / 2)
  elseif mode == 5 then
    -- seeded permutation rank: sort by hash, rank = position
    local hi = smk.hash32((seed or 0) * 7919 + i * 104729 + 1)
    local rank = 0
    for j = 0, n - 1 do
      local hj = smk.hash32((seed or 0) * 7919 + j * 104729 + 1)
      if hj < hi or (hj == hi and j < i) then rank = rank + 1 end
    end
    return rank
  end
  return i
end
```

Test vectors you can reuse to verify a port: engine table in §2; `cubicBezier(.25,.1,.25,1, .5) ≈ 0.8024`; `bounce(.5)=0.765625`; `overshoot` peaks ≈ 1.1 near p≈0.75; critical spring `c=2√(k·m)` has no overshoot;
`smk.timing(t=2, T=5, inDelay=.5, idx=2, stagger=.1, outOffset=.25, outDur=.5)` → `tin = 1.3`, out start `4.25`.
