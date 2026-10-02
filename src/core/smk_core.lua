-- smk_core v2: seconds-based, clip-relative timing + easing/physics library.
-- Pure Lua 5.1-compatible, no globals besides the returned table, no require().
-- Inlined into every runtime artifact by build/build.py (between the markers).
-- SMK2_CORE_BEGIN
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
-- SMK2_CORE_END
return smk
