-- SMK2_Bloom — pyramid glow in 8 GPU passes (extract+downsample, 5 more downsamples, one composite). Cost is nearly independent of the radius, so big soft glows stay cheap.
-- Glow from Alpha or Brightness; colour, intensity, spread (gamma), behind/additive/glow-only. Output window is padded by the glow reach (IMG_DataWindow). Sizes px @1920.
-- @include smk_bloom
FuRegisterClass("SMK2_Bloom", CT_Tool, {
  REGS_Name = "SMK2 Bloom", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SBl",
  REGS_OpDescription = "Pyramid (multi-pass) glow with a large soft radius at fixed cost",
  REG_NoPreCalcProcess = true, REG_TimeVariant = false, REG_Version = 1,
})

SMK2BloomParams = [[
  int size[2];
  int off[2];
  int osize[2];
  int lw[6];
  int lh[6];
  int lvl;
  int glowSrc;
  int glowBehind;
  int glowOnly;
  float glowThr;
  float glowI;
  float glowGamma;
  float opacity;
  float wts[6];
  float glowCol[4];
]]

-- GPU ports of smk.bloomBuild / smk.bloomShade (src/core/smk_bloom.lua). Keep in sync; tests compile these and compare pixels.
SMK2BloomExtractSource = [[
__KERNEL__ void SMK2BloomExtractKernel(__CONSTANTREF__ SMK2BloomParams *p, __TEXTURE2D__ src, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->lw[0] || y >= p->lh[0]) return;
  float acc = 0.0f;
  for (int j = 0; j < 4; ++j) {
    float wj = (j == 0 || j == 3) ? 0.125f : 0.375f;
    for (int i = 0; i < 4; ++i) {
      float wi = (i == 0 || i == 3) ? 0.125f : 0.375f;
      int qx = 2 * x - 1 + i, qy = 2 * y - 1 + j;
      int gx = qx + p->off[0], gy = qy + p->off[1];
      float v = 0.0f;
      if (!(qx < 0 || qy < 0 || qx >= p->osize[0] || qy >= p->osize[1] || gx < 0 || gy < 0 || gx >= p->size[0] || gy >= p->size[1])) {
        float4 sc = _tex2DVecN(src, ((float)gx + 0.5f) / (float)p->size[0], ((float)gy + 0.5f) / (float)p->size[1], 15);
        v = sc.w;
        if (p->glowSrc != 0) {
          float ia = (sc.w > 0.000001f) ? (1.0f / sc.w) : 0.0f;
          float lum = (0.2126f * sc.x + 0.7152f * sc.y + 0.0722f * sc.z) * ia;
          v = fminf(fmaxf((lum - p->glowThr) / fmaxf(1.0f - p->glowThr, 0.0001f), 0.0f), 1.0f) * sc.w;
        }
      }
      acc += v * wi * wj;
    }
  }
  _tex2DVec4Write(dst, x, y, make_float4(acc, acc, acc, acc));
}
]]
SMK2BloomDownSource = [[
__KERNEL__ void SMK2BloomDownKernel(__CONSTANTREF__ SMK2BloomParams *p, __TEXTURE2D__ prev, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  int k = p->lvl;
  if (x >= p->lw[k] || y >= p->lh[k]) return;
  int pw = p->lw[k - 1], ph = p->lh[k - 1];
  float acc = 0.0f;
  for (int j = 0; j < 4; ++j) {
    float wj = (j == 0 || j == 3) ? 0.125f : 0.375f;
    for (int i = 0; i < 4; ++i) {
      float wi = (i == 0 || i == 3) ? 0.125f : 0.375f;
      int ix = 2 * x - 1 + i, iy = 2 * y - 1 + j;
      float v = 0.0f;
      if (!(ix < 0 || iy < 0 || ix >= pw || iy >= ph)) v = _tex2DVecN(prev, ((float)ix + 0.5f) / (float)pw, ((float)iy + 0.5f) / (float)ph, 15).x;
      acc += v * wi * wj;
    }
  }
  _tex2DVec4Write(dst, x, y, make_float4(acc, acc, acc, acc));
}
]]
SMK2BloomCompSource = [[
#define SMK_TXL(OUT, T, I, J, LW, LH) { int i_ = (I), j_ = (J); OUT = (i_ < 0 || j_ < 0 || i_ >= (LW) || j_ >= (LH)) ? 0.0f : _tex2DVecN(T, ((float)i_ + 0.5f) / (float)(LW), ((float)j_ + 0.5f) / (float)(LH), 15).x; }
#define SMK_BIL(OUT, T, K) { float sc_ = (float)(1 << ((K) + 1)); float u_ = ((float)x + 0.5f) / sc_ - 0.5f, v_ = ((float)y + 0.5f) / sc_ - 0.5f; int i0_ = (int)floorf(u_), j0_ = (int)floorf(v_); float fx_ = u_ - (float)i0_, fy_ = v_ - (float)j0_; float a00_, a10_, a01_, a11_; SMK_TXL(a00_, T, i0_, j0_, p->lw[K], p->lh[K]); SMK_TXL(a10_, T, i0_ + 1, j0_, p->lw[K], p->lh[K]); SMK_TXL(a01_, T, i0_, j0_ + 1, p->lw[K], p->lh[K]); SMK_TXL(a11_, T, i0_ + 1, j0_ + 1, p->lw[K], p->lh[K]); OUT = (a00_ * (1.0f - fx_) + a10_ * fx_) * (1.0f - fy_) + (a01_ * (1.0f - fx_) + a11_ * fx_) * fy_; }
__KERNEL__ void SMK2BloomCompKernel(__CONSTANTREF__ SMK2BloomParams *p, __TEXTURE2D__ src, __TEXTURE2D__ L1, __TEXTURE2D__ L2, __TEXTURE2D__ L3, __TEXTURE2D__ L4, __TEXTURE2D__ L5, __TEXTURE2D__ L6, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->osize[0] || y >= p->osize[1]) return;
  float f0, f1, f2, f3, f4, f5;
  SMK_BIL(f0, L1, 0); SMK_BIL(f1, L2, 1); SMK_BIL(f2, L3, 2); SMK_BIL(f3, L4, 3); SMK_BIL(f4, L5, 4); SMK_BIL(f5, L6, 5);
  float field = p->wts[0] * f0 + p->wts[1] * f1 + p->wts[2] * f2 + p->wts[3] * f3 + p->wts[4] * f4 + p->wts[5] * f5;
  int gx = x + p->off[0], gy = y + p->off[1];
  float r = 0.0f, g = 0.0f, b = 0.0f, a = 0.0f;
  if (!(gx < 0 || gy < 0 || gx >= p->size[0] || gy >= p->size[1])) {
    float4 s0 = _tex2DVecN(src, ((float)gx + 0.5f) / (float)p->size[0], ((float)gy + 0.5f) / (float)p->size[1], 15);
    r = s0.x; g = s0.y; b = s0.z; a = s0.w;
  }
  float v = ((field > 0.0f) ? powf(field, p->glowGamma) : 0.0f) * p->glowI;
  float ga = fminf(fmaxf(v * p->glowCol[3], 0.0f), 1.0f);
  float gr = p->glowCol[0] * ga, gg = p->glowCol[1] * ga, gb = p->glowCol[2] * ga;
  float O = p->opacity;
  if (p->glowOnly > 0) { _tex2DVec4Write(dst, x, y, make_float4(gr * O, gg * O, gb * O, ga * O)); return; }
  if (p->glowBehind > 0) {
    float k2 = 1.0f - a;
    _tex2DVec4Write(dst, x, y, make_float4((r + gr * k2) * O, (g + gg * k2) * O, (b + gb * k2) * O, (a + ga * k2) * O));
    return;
  }
  _tex2DVec4Write(dst, x, y, make_float4((r + gr) * O, (g + gg) * O, (b + gb) * O, fminf(fmaxf(a + ga * (1.0f - a), 0.0f), 1.0f) * O));
}
]]

I = {}
local function num(key, name, def, lo, hi, extra)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "SliderControl", INP_Default = def, INP_MinScale = lo, INP_MaxScale = hi }
  for k, v in pairs(extra or {}) do t[k] = v end
  I[key] = self:AddInput(name, key, t)
end
local function combo(key, name, def, items)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "ComboControl", INP_Default = def, INP_Integer = true }
  for _, n in ipairs(items) do t[#t + 1] = { CCS_AddString = n } end
  I[key] = self:AddInput(name, key, t)
end
local function check(key, name, def) I[key] = self:AddInput(name, key, { LINKID_DataType = "Number", INPID_InputControl = "CheckboxControl", INP_Default = def }) end
local function color(key, name, group, r, g, b, a)
  local ch, def = { "R", "G", "B", "A" }, { r, g, b, a }
  for i = 1, 4 do
    I[key .. ch[i]] = self:AddInput(i == 1 and name or "", key .. ch[i], { LINKID_DataType = "Number",
      INPID_InputControl = "ColorControl", INP_Default = def[i], IC_ControlGroup = group, IC_ControlID = i - 1 })
  end
end

function Create()
  I.Image = self:AddInput("Image", "Image", { LINKID_DataType = "Image", LINK_Main = 1 })
  combo("GlowSrc", "Glow From", 0, { "Alpha", "Brightness" })
  num("GlowR", "Radius (px @1920)", 120, 4, 400); num("GlowI", "Intensity", 1.2, 0, 6); num("GlowThr", "Brightness Threshold", 0.6, 0, 0.99)
  num("GlowGamma", "Spread (gamma; below 1 = wider, brighter tails)", 1, 0.3, 3)
  color("GlowC", "Glow Colour", 1, 0.45, 0.65, 1, 1)
  check("GlowBehind", "Glow Behind Object (off = additive)", 0); check("GlowOnly", "Glow Only (no object)", 0)
  num("Opacity", "Opacity", 1, 0, 1)
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end

-- how far the glow reaches beyond the input (px)
function SMK2_BloomPad(req, w)
  return math.ceil(g(req, "GlowR") * (w / 1920) * 1.3) + 2
end

-- Pure CPU stage (unit-tested). ow = padded output window {left, bottom, right, top} or nil (no padding).
function SMK2_BloomPrep(req, w, h, ow)
  local px = w / 1920
  local R = math.max(g(req, "GlowR") * px, 1)
  local off, osize = { 0, 0 }, { w, h }
  if ow then off = { ow.left, ow.bottom }; osize = { ow.right - ow.left, ow.top - ow.bottom } end
  local lw, lh, wts, sum = {}, {}, {}, 0
  for k = 1, 6 do
    lw[k] = math.ceil(osize[1] / 2 ^ k); lh[k] = math.ceil(osize[2] / 2 ^ k)
    wts[k] = 1 / (1 + (2 ^ k / R) ^ 4); sum = sum + wts[k]
  end
  for k = 1, 6 do wts[k] = wts[k] / sum end
  return { size = { w, h }, off = off, osize = osize, lw = lw, lh = lh, lvl = 0, glowSrc = math.floor(g(req, "GlowSrc") + 0.5),
    glowBehind = g(req, "GlowBehind") > 0.5 and 1 or 0, glowOnly = g(req, "GlowOnly") > 0.5 and 1 or 0,
    glowThr = g(req, "GlowThr"), glowI = g(req, "GlowI"), glowGamma = g(req, "GlowGamma"), opacity = g(req, "Opacity"), wts = wts,
    glowCol = { g(req, "GlowCR"), g(req, "GlowCG"), g(req, "GlowCB"), g(req, "GlowCA") } }
end

local function runPass(req, name, source, P, lvl, inputs, output)
  local node = DVIPComputeNode(req, name, source, "SMK2BloomParams", SMK2BloomParams)
  local b = node:GetParamBlock(SMK2BloomParams)
  for key, v in pairs(P) do b[key] = v end
  b.lvl = lvl
  node:SetParamBlock(b)
  node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
  for i, im in ipairs(inputs) do node:AddInput(im.name, im.img) end
  node:AddOutput("dst", output)
  if not node:RunSession(req) then error("RunSession failed: " .. name) end
end

function Process(req)
  local img = I.Image:GetValue(req)
  if not img then OutImage:Set(req, nil) return end
  local dw, pad = img.DataWindow, SMK2_BloomPad(req, img.Width)
  local out, ow
  if dw then
    ow = ImgRectI(dw.left - pad, dw.bottom - pad, dw.right + pad, dw.top + pad)       -- only IMG_DataWindow places an image (Phase 0 / 2b)
    out = Image({ IMG_Like = img, IMG_DeferAlloc = true, IMG_DataWindow = ow })
    ow = out.DataWindow or ow
  else
    out = Image({ IMG_Like = img, IMG_DeferAlloc = true })
  end
  if req:IsPreCalc() then OutImage:Set(req, out) return end
  local P = SMK2_BloomPrep(req, img.Width, img.Height, ow)
  local ok, perr = pcall(function()
    local L = {}
    for k = 1, 6 do L[k] = Image({ IMG_Width = P.lw[k], IMG_Height = P.lh[k], IMG_Depth = img.Depth, IMG_DeferAlloc = true }) end      -- S12: intermediates of any size work
    runPass(req, "SMK2BloomExtractKernel", SMK2BloomExtractSource, P, 0, { { name = "src", img = img } }, L[1])
    for k = 2, 6 do runPass(req, "SMK2BloomDownKernel", SMK2BloomDownSource, P, k - 1, { { name = "prev", img = L[k - 1] } }, L[k]) end
    runPass(req, "SMK2BloomCompKernel", SMK2BloomCompSource, P, 0, { { name = "src", img = img }, { name = "L1", img = L[1] }, { name = "L2", img = L[2] },
      { name = "L3", img = L[3] }, { name = "L4", img = L[4] }, { name = "L5", img = L[5] }, { name = "L6", img = L[6] } }, out)
  end)
  if not ok then print("[SMK2_Bloom] GPU failed: " .. tostring(perr)); out = img end      -- pass-through fallback
  OutImage:Set(req, out)
end
