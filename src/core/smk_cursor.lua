-- smk_cursor: cursor path / click state (CPU) and the reference pixel function (oracle for the GPU kernel).
-- Pixel space, y up. All times in seconds, clip-relative. Needs smk_core (smk.clamp, smk.cubicBezier, smk.spring).
-- SMK2_MOD_BEGIN
-- Classic pointer, hot spot (tip) at the origin, unit height, y up.
smk.POINTER = { {0, 0}, {0, -0.84}, {0.19, -0.66}, {0.33, -1.0}, {0.45, -0.95}, {0.31, -0.62}, {0.58, -0.62} }

-- wp[i] = { x, y (0..1 of frame; y up), move (s to arrive from previous), hold (s after arriving), click (bool) }
-- o = { n, startDelay, arc, ease (1 smooth, 2 snappy, 3 spring), clickDelay, pressDur, pressAmt, rippleDur,
--       fadeIn, fadeOut, T (time of last frame), aspect (w/h) }
function smk.cursorTimeline(wp, o)
  local arrive, depart = {}, {}
  arrive[1] = o.startDelay; depart[1] = arrive[1] + (wp[1].hold or 0)
  for i = 2, o.n do
    arrive[i] = depart[i - 1] + math.max(wp[i].move or 0, 0); depart[i] = arrive[i] + (wp[i].hold or 0)
  end
  return arrive, depart
end

local function ease(kind, p, tau)
  if kind == 3 then return smk.spring(tau, 220, 22, 1) end                       -- spring (real time)
  if kind == 2 then return smk.cubicBezier(0.2, 0.9, 0.3, 1, p) end              -- snappy: fast start, soft landing
  return smk.cubicBezier(0.65, 0, 0.35, 1, p)                                    -- smooth: symmetric in-out
end

function smk.cursorState(t, wp, o)
  local arrive, depart = smk.cursorTimeline(wp, o)
  local x, y = wp[1].x, wp[1].y
  for i = 2, o.n do
    if t >= depart[i - 1] then
      local dur = math.max(wp[i].move or 0, 1e-4)
      local tau = t - depart[i - 1]
      local p = smk.clamp(tau / dur, 0, 1)
      local e = ease(o.ease, p, tau)
      local x0, y0, x1, y1 = wp[i - 1].x, wp[i - 1].y, wp[i].x, wp[i].y
      -- gentle arc: parabolic bulge perpendicular to the move (aspect-corrected so the arc is isotropic on screen)
      local dx, dy = (x1 - x0) * o.aspect, (y1 - y0)
      local len = math.sqrt(dx * dx + dy * dy)
      local bulge = (o.arc or 0) * len * 4 * p * (1 - p)
      local nx, ny = (len > 1e-9) and (-dy / len) or 0, (len > 1e-9) and (dx / len) or 0
      x = x0 + (x1 - x0) * e + (nx * bulge) / o.aspect
      y = y0 + (y1 - y0) * e + ny * bulge
    end
  end
  -- clicks: press dip + ripples
  local press, ripples = 1, {}
  for i = 1, o.n do
    if wp[i].click then
      local tc = arrive[i] + o.clickDelay
      local pd = smk.clamp((t - tc) / o.pressDur, 0, 1)
      if t >= tc and t <= tc + o.pressDur then press = math.min(press, 1 - o.pressAmt * math.sin(math.pi * pd)) end
      local rp = (t - tc) / o.rippleDur
      if rp >= 0 and rp <= 1 then
        ripples[#ripples + 1] = { x = wp[i].x, y = wp[i].y, r = 1 - (1 - rp) ^ 3, a = (1 - rp) ^ 1.5 }
      end
    end
  end
  table.sort(ripples, function(a, b) return a.r > b.r end)
  local op = smk.clamp((t - math.max(o.startDelay - o.fadeIn, 0)) / math.max(o.fadeIn, 1e-4), 0, 1)
  op = op * smk.clamp((o.T - t) / math.max(o.fadeOut, 1e-4), 0, 1)
  return { x = x, y = y, press = press, ripples = ripples, opacity = op }
end

-- ---- reference pixel function -----------------------------------------------------------------
local function cov(d) return smk.clamp(0.5 - d, 0, 1) end
local function polySdf(px, py, V, S)
  local n = #V
  local d = (px - V[1][1] * S) ^ 2 + (py - V[1][2] * S) ^ 2
  local s = 1.0
  local j = n
  for i = 1, n do
    local ex, ey = (V[j][1] - V[i][1]) * S, (V[j][2] - V[i][2]) * S
    local wx, wy = px - V[i][1] * S, py - V[i][2] * S
    local t = smk.clamp((wx * ex + wy * ey) / (ex * ex + ey * ey), 0, 1)
    local bx, by = wx - ex * t, wy - ey * t
    d = math.min(d, bx * bx + by * by)
    local c1, c2, c3 = (py >= V[i][2] * S), (py < V[j][2] * S), (ex * wy > ey * wx)
    if (c1 and c2 and c3) or ((not c1) and (not c2) and (not c3)) then s = -s end
    j = i
  end
  return s * math.sqrt(d)
end
smk.polySdf = polySdf

local function over(top, bot) local k = 1 - top[4]; return { top[1] + bot[1] * k, top[2] + bot[2] * k, top[3] + bot[3] * k, top[4] + bot[4] * k } end
local function premul(c, k) return { c[1] * c[4] * k, c[2] * c[4] * k, c[3] * c[4] * k, c[4] * k } end

-- P: tip{x,y} px, S (pointer height px), press, fillCol, borderCol, bw (px), shadowCol, shadowOff{x,y}, shadowBlur,
--    rip[1..3] = {cx, cy, r, a} (px, a=0 disables), ripCol, ripThick (px), opacity
function smk.cursorShade(P, x, y)
  local V = smk.POINTER
  local lx, ly = (x + 0.5 - P.tip[1]) / P.press, (y + 0.5 - P.tip[2]) / P.press         -- press scales about the tip
  local d = polySdf(lx, ly, V, P.S) * P.press
  local fill = premul(P.fillCol, cov(d))
  local border = premul(P.borderCol, P.bw > 0 and math.max(cov(d - 0) - cov(d + P.bw), 0) or 0)       -- inside border band
  local shadow = { 0, 0, 0, 0 }
  if P.shadowCol[4] > 0 then
    local sd = polySdf(lx - P.shadowOff[1] / P.press, ly - P.shadowOff[2] / P.press, V, P.S) * P.press
    local blur = math.max(P.shadowBlur, 0.5)
    local t = smk.clamp((sd + blur) / (2 * blur), 0, 1)
    shadow = premul(P.shadowCol, 1 - t * t * (3 - 2 * t))
  end
  local rip = { 0, 0, 0, 0 }
  for i = 1, 3 do
    local r = P.rip[i]
    if r[4] > 0 then
      local rd = math.abs(math.sqrt((x + 0.5 - r[1]) ^ 2 + (y + 0.5 - r[2]) ^ 2) - r[3]) - P.ripThick * 0.5
      rip = over(premul(P.ripCol, cov(rd) * r[4]), rip)
    end
  end
  local out = over(border, over(fill, over(shadow, rip)))
  return out[1] * P.opacity, out[2] * P.opacity, out[3] * P.opacity, out[4] * P.opacity
end
-- SMK2_MOD_END
