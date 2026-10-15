-- smk_bloom: reference for SMK2 Bloom (pyramid glow, multi-pass). Scalar glow field (alpha or thresholded brightness) -> 6 levels (each half the size of the previous,
-- 4x4 [1 3 3 1]/8 tent filter per axis) -> weighted sum of bilinear upsamples -> glow colour -> composite. Coordinates are PADDED-window pixels; off = window origin in source pixels.
-- Needs smk_core. Level k (1..6) texel (i,j) is centred at padded pixel (2^k (i+0.5), 2^k (j+0.5)).
-- SMK2_MOD_BEGIN
local function bloomVal(P, r, g, b, a)
  if P.glowSrc == 0 then return a end
  local ia = (a > 1e-6) and (1 / a) or 0
  local lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) * ia
  return smk.clamp((lum - P.glowThr) / math.max(1 - P.glowThr, 1e-4), 0, 1) * a
end
local function srcAt(P, src, gx, gy)                      -- integer source pixel, zero outside
  if gx < 0 or gy < 0 or gx >= P.size[1] or gy >= P.size[2] then return 0, 0, 0, 0 end
  return src(gx + 0.5, gy + 0.5)
end
local TAP = { 1 / 8, 3 / 8, 3 / 8, 1 / 8 }

function smk.bloomBuild(P, src)
  local L = {}
  for k = 1, 6 do
    local w, h = P.lw[k], P.lh[k]
    local rows = {}
    for y = 0, h - 1 do
      local row = {}
      for x = 0, w - 1 do
        local acc = 0
        for j = 0, 3 do
          for i = 0, 3 do
            local v
            if k == 1 then
              local px, py = 2 * x - 1 + i, 2 * y - 1 + j                              -- padded L0 pixel
              if px < 0 or py < 0 or px >= P.osize[1] or py >= P.osize[2] then v = 0
              else v = bloomVal(P, srcAt(P, src, px + P.off[1], py + P.off[2])) end
            else
              local ix, iy = 2 * x - 1 + i, 2 * y - 1 + j
              local pw, ph = P.lw[k - 1], P.lh[k - 1]
              v = (ix < 0 or iy < 0 or ix >= pw or iy >= ph) and 0 or L[k - 1][iy + 1][ix + 1]
            end
            acc = acc + v * TAP[i + 1] * TAP[j + 1]
          end
        end
        row[x + 1] = acc
      end
      rows[y + 1] = row
    end
    L[k] = rows
  end
  return L
end

local function bil(L, w, h, scale, x, y)
  local u, v = (x + 0.5) / scale - 0.5, (y + 0.5) / scale - 0.5
  local i0, j0 = math.floor(u), math.floor(v)
  local fx, fy = u - i0, v - j0
  local function t(i, j) if i < 0 or j < 0 or i >= w or j >= h then return 0 end return L[j + 1][i + 1] end
  return (t(i0, j0) * (1 - fx) + t(i0 + 1, j0) * fx) * (1 - fy) + (t(i0, j0 + 1) * (1 - fx) + t(i0 + 1, j0 + 1) * fx) * fy
end

function smk.bloomShade(P, L, x, y, src)
  local field = 0
  for k = 1, 6 do field = field + P.wts[k] * bil(L[k], P.lw[k], P.lh[k], 2 ^ k, x, y) end
  local r, g, b, a = srcAt(P, src, x + P.off[1], y + P.off[2])
  local v = ((field > 0) and field ^ P.glowGamma or 0) * P.glowI
  local ga = smk.clamp(v * P.glowCol[4], 0, 1)
  local gr, gg, gb = P.glowCol[1] * ga, P.glowCol[2] * ga, P.glowCol[3] * ga
  local O = P.opacity
  if P.glowOnly > 0 then return gr * O, gg * O, gb * O, ga * O end
  if P.glowBehind > 0 then
    local k2 = 1 - a
    return (r + gr * k2) * O, (g + gg * k2) * O, (b + gb * k2) * O, (a + ga * k2) * O
  end
  return (r + gr) * O, (g + gg) * O, (b + gb) * O, smk.clamp(a + ga * (1 - a), 0, 1) * O
end
-- SMK2_MOD_END
