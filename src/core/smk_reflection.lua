-- smk_reflection: reference pixel function for SMK2 Reflection. Mirror about a horizontal baseline (y up), blur that GROWS with distance,
-- distance falloff, optional animated ripple. `src(sx, sy)` returns premultiplied r,g,b,a.
-- SMK2_MOD_BEGIN
local function over(top, bot) local k = 1 - top[4]; return { top[1] + bot[1] * k, top[2] + bot[2] * k, top[3] + bot[3] * k, top[4] + bot[4] * k } end

function smk.reflectShade(P, x, y, src)
  local px, py = x + 0.5, y + 0.5
  local orig = { 0, 0, 0, 0 }
  if P.keepOrig > 0 then local r, g, b, a = src(px, py); orig = { r, g, b, a } end
  local refl = { 0, 0, 0, 0 }
  local S = P.baseY - P.gap                                  -- reflection starts here and runs downward
  local d = S - py
  if d > 0 and d < P.fadeLen then
    local ys = P.baseY + d                                   -- mirrored source row
    local dx = P.rippleAmp * math.sin(P.rippleFreq * d + P.phase) * math.min(1, d / 40)
    local rad = P.blur0 + P.blurGrow * d
    local ar, ag, ab, aa
    if rad < 0.5 then
      ar, ag, ab, aa = src(px + dx, ys)
    else
      local sr, sg, sb, sa, sw = 0, 0, 0, 0, 0
      for i = 0, P.samples - 1 do
        local ang = i * 2.39996323
        local rr = rad * math.sqrt((i + 0.5) / P.samples)
        local w = math.exp(-3 * (rr / rad) ^ 2)
        local r, g, b, a = src(px + dx + math.cos(ang) * rr, ys + math.sin(ang) * rr)
        sr, sg, sb, sa, sw = sr + r * w, sg + g * w, sb + b * w, sa + a * w, sw + w
      end
      ar, ag, ab, aa = sr / sw, sg / sw, sb / sw, sa / sw
    end
    local f = smk.clamp(1 - d / P.fadeLen, 0, 1) ^ P.fadePow * P.reflOpacity
    refl = { ar * P.tint[1] * f * P.tint[4], ag * P.tint[2] * f * P.tint[4], ab * P.tint[3] * f * P.tint[4], aa * f * P.tint[4] }
  end
  local res = over(orig, refl)
  local O = P.opacity
  return res[1] * O, res[2] * O, res[3] * O, res[4] * O
end
-- SMK2_MOD_END
