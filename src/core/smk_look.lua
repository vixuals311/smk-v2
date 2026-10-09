-- smk_look: reference pixel function for SMK2 Look (glow / outline / shine / gradient). `src(sx, sy)` returns premultiplied r,g,b,a of the texel
-- containing the continuous pixel position (nearest, clamped) — the GPU kernel samples with the same positions. Needs smk_core.
-- SMK2_MOD_BEGIN
local function over(top, bot) local k = 1 - top[4]; return { top[1] + bot[1] * k, top[2] + bot[2] * k, top[3] + bot[3] * k, top[4] + bot[4] * k } end

-- glow value of a texel: alpha, or luminance above a threshold (src 0 = alpha, 1 = luminance)
local function glowVal(P, r, g, b, a)
  if P.glowSrc == 0 then return a end
  local ia = (a > 1e-6) and (1 / a) or 0
  local lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) * ia
  return smk.clamp((lum - P.glowThr) / math.max(1 - P.glowThr, 1e-4), 0, 1) * a
end

function smk.lookShade(P, x, y, src)
  local px, py = x + 0.5, y + 0.5
  local r, g, b, a = src(px, py)
  -- shine + gradient modify the object colour (masked by its alpha)
  if P.gradOn > 0 and a > 0 then
    local t = smk.clamp(((px - P.size[1] * 0.5) * P.gC + (py - P.size[2] * 0.5) * P.gS) / (2 * P.gExt) + 0.5, 0, 1)
    local ia = 1 / a
    local ur, ug, ub = r * ia, g * ia, b * ia
    local gr, gg, gb = P.gA[1] + (P.gB[1] - P.gA[1]) * t, P.gA[2] + (P.gB[2] - P.gA[2]) * t, P.gA[3] + (P.gB[3] - P.gA[3]) * t
    local k = P.gAmt * (P.gA[4] + (P.gB[4] - P.gA[4]) * t)
    r, g, b = (ur + (gr - ur) * k) * a, (ug + (gg - ug) * k) * a, (ub + (gb - ub) * k) * a
  end
  if P.shineOn > 0 and a > 0 then
    local s = (px - P.size[1] * 0.5) * P.shC + (py - P.size[2] * 0.5) * P.shS - P.shPos
    local soft = math.max(P.shSoft, 0.5)
    local bnd = smk.clamp((P.shW + soft - math.abs(s)) / soft, 0, 1)
    bnd = bnd * bnd * (3 - 2 * bnd)
    local k = bnd * P.shI * P.shCol[4] * a
    r, g, b = r + P.shCol[1] * k, g + P.shCol[2] * k, b + P.shCol[3] * k
  end
  local out = { r, g, b, a }
  local glow = { 0, 0, 0, 0 }
  if P.glowOn > 0 and P.glowR > 0.5 then
    local acc, norm = 0, 0
    for i = 0, P.glowSamples - 1 do
      local ang = i * 2.39996323
      local rr = P.glowR * math.sqrt((i + 0.5) / P.glowSamples)
      local w = math.exp(-3 * (rr / P.glowR) ^ 2)
      local sr, sg, sb, sa = src(px + math.cos(ang) * rr, py + math.sin(ang) * rr)
      acc = acc + glowVal(P, sr, sg, sb, sa) * w; norm = norm + w
    end
    local v0 = (norm > 0) and (acc / norm) or 0
    local v = ((v0 > 0) and (v0 ^ P.glowGamma) or 0) * P.glowI
    local ga = smk.clamp(v * P.glowCol[4], 0, 1)
    glow = { P.glowCol[1] * ga, P.glowCol[2] * ga, P.glowCol[3] * ga, ga }
  end
  local base = { 0, 0, 0, 0 }
  if P.glowOn > 0 and P.glowBehind > 0 then base = glow end
  if P.outOn > 0 and P.outW > 0.25 then
    local m = a
    for k = 1, P.outRings do
      local rad = P.outW * k / P.outRings
      for i = 0, 23 do
        local ang = i * 0.26179939 + k * 0.3
        local _, _, _, sa = src(px + math.cos(ang) * rad, py + math.sin(ang) * rad)
        if sa > m then m = sa end
      end
    end
    local oc = smk.clamp(m - a, 0, 1)
    local oa = oc * P.outCol[4]
    base = over({ P.outCol[1] * oa, P.outCol[2] * oa, P.outCol[3] * oa, oa }, base)
  end
  if P.glowOn > 0 and P.glowOnly > 0 then return glow[1] * P.opacity, glow[2] * P.opacity, glow[3] * P.opacity, glow[4] * P.opacity end
  local res = over(out, base)
  if P.glowOn > 0 and P.glowBehind == 0 then res = { res[1] + glow[1], res[2] + glow[2], res[3] + glow[3], smk.clamp(res[4] + glow[4] * (1 - res[4]), 0, 1) } end
  local O = P.opacity
  return res[1] * O, res[2] * O, res[3] * O, res[4] * O
end
-- SMK2_MOD_END
