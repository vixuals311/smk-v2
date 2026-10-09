-- smk_curl: reference pixel function for SMK2 Page Curl. 2D cylinder-curl model (no 3D): the page rolls over a cylinder of radius R whose axis moves along `dir`.
-- Layers bottom -> top: A flat front, B cylinder front, C cylinder back, D flat back lying on top. `src` = page, `bg` = what the page reveals.
-- SMK2_MOD_BEGIN
local function over(top, bot) local k = 1 - top[4]; return { top[1] + bot[1] * k, top[2] + bot[2] * k, top[3] + bot[3] * k, top[4] + bot[4] * k } end
local function layer(c, shade, cv) return { c[1] * shade * cv, c[2] * shade * cv, c[3] * shade * cv, c[4] * cv } end      -- shading darkens colour only, coverage drives alpha

function smk.curlShade(P, x, y, src, bg)
  local px, py = x + 0.5, y + 0.5
  local up = px * P.cd + py * P.sd
  local qx, qy = px - P.cd * up, py - P.sd * up                              -- perpendicular part (constant along the curl direction)
  local t = up - P.u0
  local function sample(u) local r, g, b, a = src(qx + P.cd * u, qy + P.sd * u); return { r, g, b, a } end
  local function back(c)                                                      -- paper back: tinted, dimmed (premultiplied)
    local k = P.backMix
    return { (c[1] * (1 - k) + P.backTint[1] * c[4] * k) * P.backDim, (c[2] * (1 - k) + P.backTint[2] * c[4] * k) * P.backDim,
             (c[3] * (1 - k) + P.backTint[3] * c[4] * k) * P.backDim, c[4] }
  end
  local res = { 0, 0, 0, 0 }
  if P.hasBG > 0 then local r, g, b, a = bg(px, py); res = { r, g, b, a } end
  -- A: flat front
  if t < 0 then
    local u = P.u0 + t
    local cvg = smk.clamp(u - P.uMin + 0.5, 0, 1)
    if cvg > 0 then
      local c = sample(u)
      local te = math.min(0, math.pi * P.R - P.L)                                  -- leading edge of the curled part: the shadow falls from there
      local sh = (P.L > 0) and (P.shadowStr * math.exp(math.min(t - te, 0) / math.max(P.shadowLen, 1e-3))) or 0
      res = over(layer(c, 1 - sh, cvg), res)
    end
  end
  -- B / C: on the cylinder
  if t >= 0 and t <= P.R then
    local phi = math.asin(smk.clamp(t / P.R, 0, 1))
    local edge = smk.clamp(P.R - t + 0.5, 0, 1)
    local s1 = P.R * phi
    local cv1 = smk.clamp(P.L - s1 + 0.5, 0, 1) * edge
    if cv1 > 0 then
      local shade = P.ambient + (1 - P.ambient) * smk.clamp(math.sin(phi) * P.lx + math.cos(phi) * P.lz, 0, 1)
      res = over(layer(sample(P.u0 + s1), shade, cv1), res)
    end
    local s2 = math.pi * P.R - s1
    local cv2 = smk.clamp(P.L - s2 + 0.5, 0, 1) * edge
    if cv2 > 0 then
      local shade = P.ambient + (1 - P.ambient) * smk.clamp(-math.sin(phi) * P.lx + math.cos(phi) * P.lz, 0, 1)
      res = over(layer(back(sample(P.u0 + s2)), shade, cv2), res)
    end
  end
  -- D: flat back lying over the page
  if t < 0 then
    local s = math.pi * P.R - t
    local cvd = smk.clamp(P.L - s + 0.5, 0, 1)
    if cvd > 0 then
      local shade = P.ambient + (1 - P.ambient) * smk.clamp(P.lz, 0, 1)
      res = over(layer(back(sample(P.u0 + s)), shade, cvd), res)
    end
  end
  return res[1] * P.opacity, res[2] * P.opacity, res[3] * P.opacity, res[4] * P.opacity
end
-- SMK2_MOD_END
