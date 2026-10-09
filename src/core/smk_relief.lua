-- smk_relief: reference pixel function for SMK2 Relief (bevel / emboss). `src(sx, sy)` returns premultiplied r,g,b,a of the texel containing the pixel position.
-- Height h = Gaussian-blurred (alpha or brightness); its gradient comes from ONE gather with Gaussian-derivative weights (no repeated blurs, no mirrored-crop tricks).
-- SMK2_MOD_BEGIN
local function heightVal(P, r, g, b, a)
  if P.srcKind == 0 then return a end
  local ia = (a > 1e-6) and (1 / a) or 0
  return (0.2126 * r + 0.7152 * g + 0.0722 * b) * ia * a
end

function smk.reliefShade(P, x, y, src)
  local px, py = x + 0.5, y + 0.5
  local r, g, b, a = src(px, py)
  local gx, gy, norm = 0, 0, 0
  local sig2 = P.sigma * P.sigma
  local R = 3 * P.sigma
  for i = 0, P.samples - 1 do
    local ang = i * 2.39996323
    local rr = R * math.sqrt((i + 0.5) / P.samples)
    local ox, oy = math.cos(ang) * rr, math.sin(ang) * rr
    local w = math.exp(-(rr * rr) / (2 * sig2))
    local sr, sg, sb, sa = src(px + ox, py + oy)
    local v = heightVal(P, sr, sg, sb, sa)
    gx = gx + ox * w * v; gy = gy + oy * w * v; norm = norm + w
  end
  local gradx, grady = 0, 0
  if norm > 0 then gradx, grady = gx / (norm * sig2), gy / (norm * sig2) end
  local sx, sy = P.depth * P.sigma * gradx, P.depth * P.sigma * grady               -- dimensionless slope
  local len = math.sqrt(sx * sx + sy * sy + 1)
  local relief = (-sx * P.lx - sy * P.ly) / len                                       -- signed tilt toward the light (saturates; steeper never gets dimmer)
  local hi = smk.clamp(math.max(relief, 0) * P.hiAmt, 0, 1) * P.hiCol[4]
  local sh = smk.clamp(math.max(-relief, 0) * P.shAmt, 0, 1) * P.shCol[4]
  local O = P.opacity
  if P.reliefOnly > 0 then
    local gray = smk.clamp(0.5 + relief * 0.5 * (P.hiAmt + P.shAmt) * 0.5, 0, 1) * a
    return gray * O, gray * O, gray * O, a * O
  end
  local nr, ng, nb = r, g, b
  nr, ng, nb = nr + (P.shCol[1] * a - nr) * sh, ng + (P.shCol[2] * a - ng) * sh, nb + (P.shCol[3] * a - nb) * sh
  nr, ng, nb = nr + (P.hiCol[1] * a - nr) * hi, ng + (P.hiCol[2] * a - ng) * hi, nb + (P.hiCol[3] * a - nb) * hi
  local k = P.blend
  return (r + (nr - r) * k) * O, (g + (ng - g) * k) * O, (b + (nb - b) * k) * O, a * O
end
-- SMK2_MOD_END
