-- smk_shape: reference implementation of the SMK2 Shape pixel function (pixel space, y up, angle CCW degrees).
-- The GPU kernel in SMK2_Shape.lua is a hand port of smk.shade(); tests render with this oracle.
-- All geometry arrives pre-scaled in pixels (see SMK2_ShapePrep). Colours are straight RGBA.
-- SMK2_MOD_BEGIN
local atan2 = math.atan2 or function(y, x) return math.atan(y, x) end
local function cov(d) return smk.clamp(0.5 - d, 0, 1) end
local function hyp(a, b) return math.sqrt(a * a + b * b) end

-- shape: 0 rect/rounded/pill, 1 ellipse, 2 ring (half[1]=outer radius, thick=ring width), 3 line/capsule (half[1]=half length)
-- returns signed distance d (px, <0 inside) and sweep mask m (0..1)
function smk.shapeSdf(P, qx, qy)
  local s, hx, hy = P.shape, P.half[1], P.half[2]
  local d, m = 0, 1
  if s == 0 then
    local r = math.min(P.radius, hx, hy)
    local bx, by = math.abs(qx) - (hx - r), math.abs(qy) - (hy - r)
    d = hyp(math.max(bx, 0), math.max(by, 0)) + math.min(math.max(bx, by), 0) - r
  elseif s == 1 then
    local ax, ay = math.max(hx, 1e-4), math.max(hy, 1e-4)
    d = (hyp(qx / ax, qy / ay) - 1) * math.min(ax, ay)
  elseif s == 2 then
    local rad = hyp(qx, qy)
    d = math.abs(rad - (hx - P.thick * 0.5)) - P.thick * 0.5
    local sweep = P.trim
    if sweep < 0.9999 then
      local t = atan2(qx, qy) / (2 * math.pi); if t < 0 then t = t + 1 end
      local u = (t - P.trimStart) % 1
      m = smk.clamp((sweep - u) * 2 * math.pi * math.max(rad, 1) + 0.5, 0, 1)
    end
  else
    local cx = smk.clamp(qx, -hx, hx)
    d = hyp(qx - cx, qy) - P.thick * 0.5
    if P.trim < 0.9999 then
      local u = qx + hx
      m = smk.clamp(P.trim * 2 * hx - u + 0.5, 0, 1)
      if P.trimStart > 0.0001 then m = m * smk.clamp(u - P.trimStart * 2 * hx + 0.5, 0, 1) end
    end
    if (P.dotR or 0) > 0 then                 -- end dot at the drawing front (callout targets)
      local xe = (P.trim < 0.9999) and (-hx + P.trim * 2 * hx) or hx
      local dd = hyp(qx - xe, qy) - P.dotR
      m = math.max(m, cov(dd)); d = math.min(d, dd)
    end
  end
  return d, m
end

local function over(top, bot) -- premultiplied RGBA
  local k = 1 - top[4]
  return { top[1] + bot[1] * k, top[2] + bot[2] * k, top[3] + bot[3] * k, top[4] + bot[4] * k }
end
local function premul(c, k) return { c[1] * c[4] * k, c[2] * c[4] * k, c[3] * c[4] * k, c[4] * k } end

function smk.shade(P, x, y) -- returns premultiplied r,g,b,a
  local dx, dy = x + 0.5 - P.center[1], y + 0.5 - P.center[2]
  local lx = P.cosA * dx + P.sinA * dy
  local ly = -P.sinA * dx + P.cosA * dy
  local d, m = smk.shapeSdf(P, lx, ly)
  -- fill
  local ca, cb, g = P.fillA, P.fillB, 0
  if P.fillMode == 1 then
    local gx = P.gradC * lx + P.gradS * ly
    local ext = math.abs(P.gradC) * P.half[1] + math.abs(P.gradS) * P.half[2] + 1e-4
    g = smk.clamp(gx / (2 * ext) + 0.5, 0, 1)
  elseif P.fillMode == 2 then
    g = smk.clamp(hyp(lx, ly) / (math.max(P.half[1], P.half[2]) + 1e-4), 0, 1)
  end
  local fc = { ca[1] + (cb[1] - ca[1]) * g, ca[2] + (cb[2] - ca[2]) * g, ca[3] + (cb[3] - ca[3]) * g, ca[4] + (cb[4] - ca[4]) * g }
  local fill = premul(fc, cov(d) * m)
  -- border band
  local bmin, bmax = -P.bw, 0
  if P.borderPos == 1 then bmin, bmax = -P.bw * 0.5, P.bw * 0.5 elseif P.borderPos == 2 then bmin, bmax = 0, P.bw end
  local bcov = P.bw > 0 and math.max(cov(d - bmax) - cov(d - bmin), 0) * m or 0
  local border = premul(P.borderCol, bcov)
  -- shadow (blurred SDF falloff)
  local shadow = { 0, 0, 0, 0 }
  if P.shadowCol[4] > 0 then
    local sd, sm = smk.shapeSdf(P, lx - P.shadowOff[1], ly - P.shadowOff[2])
    local blur = math.max(P.shadowBlur, 0.5)
    local t = smk.clamp((sd + blur) / (2 * blur), 0, 1)
    shadow = premul(P.shadowCol, (1 - t * t * (3 - 2 * t)) * sm)
  end
  -- track: the part of the shape removed by Trim, drawn in its own colour (progress bars / rings)
  local track = { 0, 0, 0, 0 }
  if P.trackCol[4] > 0 and m < 1 then track = premul(P.trackCol, cov(d) * (1 - m)) end
  local out = over(border, over(fill, over(track, shadow)))
  return out[1] * P.opacity, out[2] * P.opacity, out[3] * P.opacity, out[4] * P.opacity
end
-- SMK2_MOD_END
