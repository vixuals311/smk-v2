-- smk_connector: connector path builder (CPU) + reference pixel function (oracle for the GPU kernel).
-- Pixel space, y up. Needs smk_core. Paths are polylines of <= 96 points with cumulative arclength (px).
-- SMK2_MOD_BEGIN
smk.CONN_MAXP = 96
local function hyp(a, b) return math.sqrt(a * a + b * b) end
local function cov(d) return smk.clamp(0.5 - d, 0, 1) end

-- magnetic port: mag 0 off, 1 auto (exit toward `toward`), 2 top, 3 right, 4 bottom, 5 left. Returns point {x,y}, outward normal {nx,ny} or nil.
function smk.magnetPoint(c, hw, hh, mag, toward, gap)
  if mag == 0 then return { c[1], c[2] }, nil end
  local nx, ny, px, py
  if mag == 2 then nx, ny, px, py = 0, 1, c[1], c[2] + hh
  elseif mag == 3 then nx, ny, px, py = 1, 0, c[1] + hw, c[2]
  elseif mag == 4 then nx, ny, px, py = 0, -1, c[1], c[2] - hh
  elseif mag == 5 then nx, ny, px, py = -1, 0, c[1] - hw, c[2]
  else
    local dx, dy = toward[1] - c[1], toward[2] - c[2]
    if hyp(dx, dy) < 1e-6 then nx, ny, px, py = 1, 0, c[1] + hw, c[2]
    else
      local tx, ty = hw / math.max(math.abs(dx), 1e-9), hh / math.max(math.abs(dy), 1e-9)
      local t = math.min(tx, ty)
      px, py = c[1] + dx * t, c[2] + dy * t
      if tx < ty then nx, ny = (dx >= 0) and 1 or -1, 0 else nx, ny = 0, (dy >= 0) and 1 or -1 end
    end
  end
  return { px + nx * gap, py + ny * gap }, { nx, ny }
end

local function bez(p0, p1, p2, p3, t)
  local u = 1 - t
  local a, b, c, d = u * u * u, 3 * u * u * t, 3 * u * t * t, t * t * t
  return { a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1], a * p0[2] + b * p1[2] + c * p2[2] + d * p3[2] }
end

-- S: {mode (1 curve, 2 straight, 3 elbow, 4 bezier, 5 spline), pa, pb, h1, h2, mid = {points}, bend, tension, radius,
--     aBox = {hw, hh, mag}, bBox = {hw, hh, mag}, gap}
function smk.connPath(S)
  local pa, pb = { S.pa[1], S.pa[2] }, { S.pb[1], S.pb[2] }
  local ref_a = (S.mode == 4 and S.h1) or (S.mode == 5 and S.mid[1]) or pb          -- what end A looks toward
  local ref_b = (S.mode == 4 and S.h2) or (S.mode == 5 and S.mid[#S.mid]) or pa
  local na, nb
  pa, na = smk.magnetPoint(S.pa, S.aBox.hw, S.aBox.hh, S.aBox.mag, ref_a, S.gap)
  pb, nb = smk.magnetPoint(S.pb, S.bBox.hw, S.bBox.hh, S.bBox.mag, ref_b, S.gap)
  local pts = {}
  local function add(p) pts[#pts + 1] = { p[1], p[2] } end
  local dist = hyp(pb[1] - pa[1], pb[2] - pa[2])
  if S.mode == 2 or dist < 1e-6 then add(pa); add(pb)
  elseif S.mode == 1 then
    local k = (S.bend or 0.45) * dist
    local da = na or { (pb[1] - pa[1]) / dist, (pb[2] - pa[2]) / dist }
    local db = nb or { (pa[1] - pb[1]) / dist, (pa[2] - pb[2]) / dist }
    local c1, c2 = { pa[1] + da[1] * k, pa[2] + da[2] * k }, { pb[1] + db[1] * k, pb[2] + db[2] * k }
    for i = 0, 63 do add(bez(pa, c1, c2, pb, i / 63)) end
  elseif S.mode == 4 then
    for i = 0, 63 do add(bez(pa, S.h1, S.h2, pb, i / 63)) end
  elseif S.mode == 5 then
    local P = { pa }
    for _, m in ipairs(S.mid) do P[#P + 1] = m end
    P[#P + 1] = pb
    local segs = #P - 1
    local per = math.max(3, math.floor(90 / segs))
    local tn = (S.tension or 1) / 6
    for i = 1, segs do
      local p0, p1, p2, p3 = P[math.max(i - 1, 1)], P[i], P[i + 1], P[math.min(i + 2, #P)]
      local c1 = { p1[1] + (p2[1] - p0[1]) * tn, p1[2] + (p2[2] - p0[2]) * tn }
      local c2 = { p2[1] - (p3[1] - p1[1]) * tn, p2[2] - (p3[2] - p1[2]) * tn }
      for j = (i == 1) and 0 or 1, per do add(bez(p1, c1, c2, p2, j / per)) end
    end
  else -- elbow with rounded corners
    local horizontal = (na and math.abs(na[1]) > 0.5) or ((not na) and math.abs(pb[1] - pa[1]) >= math.abs(pb[2] - pa[2]))
    local corners
    if horizontal then local mx = (pa[1] + pb[1]) * 0.5; corners = { pa, { mx, pa[2] }, { mx, pb[2] }, pb }
    else local my = (pa[2] + pb[2]) * 0.5; corners = { pa, { pa[1], my }, { pb[1], my }, pb } end
    add(corners[1])
    local r = S.radius or 0
    for i = 2, 3 do
      local a, c, b = corners[i - 1], corners[i], corners[i + 1]
      local l1, l2 = hyp(c[1] - a[1], c[2] - a[2]), hyp(b[1] - c[1], b[2] - c[2])
      local rr = math.min(r, l1 * 0.5, l2 * 0.5)
      if rr < 0.5 then add(c)
      else
        local s = { c[1] + (a[1] - c[1]) / l1 * rr, c[2] + (a[2] - c[2]) / l1 * rr }
        local e = { c[1] + (b[1] - c[1]) / l2 * rr, c[2] + (b[2] - c[2]) / l2 * rr }
        for j = 0, 8 do add(bez(s, { s[1] + (c[1] - s[1]) * 0.55, s[2] + (c[2] - s[2]) * 0.55 }, { e[1] + (c[1] - e[1]) * 0.55, e[2] + (c[2] - e[2]) * 0.55 }, e, j / 8)) end
      end
    end
    add(corners[4])
  end
  local cum, tot = { 0 }, 0
  for i = 2, #pts do tot = tot + hyp(pts[i][1] - pts[i - 1][1], pts[i][2] - pts[i - 1][2]); cum[i] = tot end
  local n = #pts
  local function dir(a, b) local d = hyp(b[1] - a[1], b[2] - a[2]); if d < 1e-9 then return { 1, 0 } end; return { (b[1] - a[1]) / d, (b[2] - a[2]) / d } end
  return { pts = pts, cum = cum, total = tot, n = n, startDir = dir(pts[2] or pts[1], pts[1]), endDir = dir(pts[n - 1] or pts[n], pts[n]), pa = pa, pb = pb }
end

-- point at arclength s
function smk.connPointAt(path, s)
  s = smk.clamp(s, 0, path.total)
  for i = 2, path.n do
    if path.cum[i] >= s then
      local l = path.cum[i] - path.cum[i - 1]; local t = (l > 0) and (s - path.cum[i - 1]) / l or 0
      return { path.pts[i - 1][1] + (path.pts[i][1] - path.pts[i - 1][1]) * t, path.pts[i - 1][2] + (path.pts[i][2] - path.pts[i - 1][2]) * t }
    end
  end
  return { path.pts[path.n][1], path.pts[path.n][2] }
end

-- ---- reference pixel function ---------------------------------------------------------------
local function triSdf(px, py, T)
  local d = (px - T[1]) ^ 2 + (py - T[2]) ^ 2
  local s = 1.0
  local j = 3
  for i = 1, 3 do
    local ax, ay = T[2 * i - 1], T[2 * i]
    local bx, by = T[2 * j - 1], T[2 * j]
    local ex, ey, wx, wy = bx - ax, by - ay, px - ax, py - ay
    local t = smk.clamp((wx * ex + wy * ey) / (ex * ex + ey * ey), 0, 1)
    local qx, qy = wx - ex * t, wy - ey * t
    d = math.min(d, qx * qx + qy * qy)
    local c1, c2, c3 = (py >= ay), (py < by), (ex * wy > ey * wx)
    if (c1 and c2 and c3) or ((not c1) and (not c2) and (not c3)) then s = -s end
    j = i
  end
  return s * math.sqrt(d)
end
local function over(top, bot) local k = 1 - top[4]; return { top[1] + bot[1] * k, top[2] + bot[2] * k, top[3] + bot[3] * k, top[4] + bot[4] * k } end
local function premul(c, k) return { c[1] * c[4] * k, c[2] * c[4] * k, c[3] * c[4] * k, c[4] * k } end

-- P: n, pts (flat x,y,x,y...), cum, total, thick, trim, dash, dgap, colA, colB, gradOn, mkA/mkB = {kind 0/1/2, cx, cy, r, tri={6}}, pul[1..3]={x,y,r,a}, pulCol, opacity
function smk.connShade(P, x, y)
  local px, py = x + 0.5, y + 0.5
  local best, bu = 1e30, 0
  for i = 1, P.n - 1 do
    local ax, ay, bx, by = P.pts[2 * i - 1], P.pts[2 * i], P.pts[2 * i + 1], P.pts[2 * i + 2]
    local ex, ey = bx - ax, by - ay
    local l2 = ex * ex + ey * ey
    local t = (l2 > 0) and smk.clamp(((px - ax) * ex + (py - ay) * ey) / l2, 0, 1) or 0
    local dx, dy = px - (ax + t * ex), py - (ay + t * ey)
    local d2 = dx * dx + dy * dy
    if d2 < best then best = d2; bu = P.cum[i] + t * math.sqrt(l2) end
  end
  local d = math.sqrt(best) - P.thick * 0.5
  local m = smk.clamp(P.trim * P.total - bu + 0.5, 0, 1)
  if P.dash > 0 then
    local ph = bu % (P.dash + P.dgap)
    m = m * smk.clamp(math.min(ph, P.dash - ph) + 0.5, 0, 1)
  end
  local g = (P.gradOn > 0.5 and P.total > 0) and smk.clamp(bu / P.total, 0, 1) or 0
  local c = { P.colA[1] + (P.colB[1] - P.colA[1]) * g, P.colA[2] + (P.colB[2] - P.colA[2]) * g, P.colA[3] + (P.colB[3] - P.colA[3]) * g,
              P.colA[4] + (P.colB[4] - P.colA[4]) * g }
  local out = premul(c, cov(d) * m)
  local vis = { 1, smk.clamp((P.trim - 0.92) / 0.08, 0, 1) }                                -- end marker shows only when fully drawn
  for e, mk in ipairs({ P.mkA, P.mkB }) do
    local mc = (e == 1) and P.colA or P.colB
    local cv = 0
    if mk.kind == 1 then cv = cov(hyp(px - mk.cx, py - mk.cy) - mk.r)
    elseif mk.kind == 2 then cv = cov(triSdf(px, py, mk.tri)) end
    if cv > 0 then out = over(premul(mc, cv * vis[e]), out) end
  end
  for i = 1, 3 do
    local q = P.pul[i]
    if q[4] > 0 then out = over(premul(P.pulCol, cov(hyp(px - q[1], py - q[2]) - q[3]) * q[4]), out) end
  end
  return out[1] * P.opacity, out[2] * P.opacity, out[3] * P.opacity, out[4] * P.opacity
end
-- SMK2_MOD_END
