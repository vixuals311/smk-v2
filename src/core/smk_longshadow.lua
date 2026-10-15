-- smk_longshadow: reference for SMK2 Long Shadow (multi-pass). F(p) = max over t in [0, L] of ( alpha(p - d t) - t / L ), built by DOUBLING:
-- F0 = alpha; F_k(p) = max( F_{k-1}(p), bilinear F_{k-1}(p - d 2^(k-1)) - slope 2^(k-1) ). After K passes the reach is 2^K - 1 >= L px. Coordinates are padded-window pixels.
-- Needs smk_core.
-- SMK2_MOD_BEGIN
local function bilF(F, w, h, qx, qy)
  local u, v = qx - 0.5, qy - 0.5
  local i0, j0 = math.floor(u), math.floor(v)
  local fx, fy = u - i0, v - j0
  local function t(i, j) if i < 0 or j < 0 or i >= w or j >= h then return 0 end return F[j + 1][i + 1] end
  return (t(i0, j0) * (1 - fx) + t(i0 + 1, j0) * fx) * (1 - fy) + (t(i0, j0 + 1) * (1 - fx) + t(i0 + 1, j0 + 1) * fx) * fy
end

function smk.lsPasses(L) return math.max(1, math.min(12, math.ceil(math.log(math.max(L, 1) + 1) / math.log(2)))) end

function smk.lsBuild(P, src)
  local w, h = P.osize[1], P.osize[2]
  local F = {}
  for y = 0, h - 1 do
    local row = {}
    for x = 0, w - 1 do
      local gx, gy = x + P.off[1], y + P.off[2]
      local a = 0
      if not (gx < 0 or gy < 0 or gx >= P.size[1] or gy >= P.size[2]) then local _, _, _, sa = src(gx + 0.5, gy + 0.5); a = sa end
      row[x + 1] = a
    end
    F[y + 1] = row
  end
  for k = 1, P.passes do
    local s = 2 ^ (k - 1)
    local G = {}
    for y = 0, h - 1 do
      local row = {}
      for x = 0, w - 1 do
        local v = bilF(F, w, h, x + 0.5 - P.dx * s, y + 0.5 - P.dy * s) - P.slope * s
        local c = F[y + 1][x + 1]
        row[x + 1] = (v > c) and v or c
      end
      G[y + 1] = row
    end
    F = G
  end
  return F
end

function smk.lsShade(P, F, x, y, src)
  local gx, gy = x + P.off[1], y + P.off[2]
  local r, g, b, a = 0, 0, 0, 0
  if not (gx < 0 or gy < 0 or gx >= P.size[1] or gy >= P.size[2]) then r, g, b, a = src(gx + 0.5, gy + 0.5) end
  local f = smk.clamp(F[y + 1][x + 1], 0, 1)
  local sa = ((f > 0) and f ^ P.curve or 0) * P.col[4]
  local k2 = 1 - a
  local O = P.opacity
  return (r + P.col[1] * sa * k2) * O, (g + P.col[2] * sa * k2) * O, (b + P.col[3] * sa * k2) * O, (a + sa * k2) * O
end
-- SMK2_MOD_END
