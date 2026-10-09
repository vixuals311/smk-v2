-- SMK2_Reflection — mirror reflection about a horizontal baseline, one GPU pass: blur that GROWS with distance, distance fade, optional animated ripple, tint.
-- Baseline is a fraction of the frame height from the bottom. Sizes are px @1920. Ripple animates in seconds (clip-relative).
-- @include smk_reflection
FuRegisterClass("SMK2_Reflection", CT_Tool, {
  REGS_Name = "SMK2 Reflection", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SRf",
  REGS_OpDescription = "Floor reflection with distance blur, fade and ripple, one GPU pass",
  REG_NoPreCalcProcess = true, REG_TimeVariant = true, REG_Version = 1,
})

SMK2ReflectParams = [[
  int size[2];
  int off[2];
  int osize[2];
  int keepOrig;
  int samples;
  float baseY;
  float gap;
  float fadeLen;
  float fadePow;
  float reflOpacity;
  float blur0;
  float blurGrow;
  float rippleAmp;
  float rippleFreq;
  float phase;
  float opacity;
  float tint[4];
]]

-- GPU port of smk.reflectShade() (src/core/smk_reflection.lua). Keep in sync; tests compile this and compare pixels.
SMK2ReflectSource = [[
__KERNEL__ void SMK2ReflectKernel(__CONSTANTREF__ SMK2ReflectParams *p, __TEXTURE2D__ src, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->osize[0] || y >= p->osize[1]) return;
  float W = (float)p->size[0], H = (float)p->size[1];
  float px = (float)(x + p->off[0]) + 0.5f, py = (float)(y + p->off[1]) + 0.5f;
  float or_ = 0.0f, og = 0.0f, ob = 0.0f, oa = 0.0f;
  if (p->keepOrig > 0 && px >= 0.0f && py >= 0.0f && px <= W && py <= H) { float4 s0 = _tex2DVecN(src, px / W, py / H, 15); or_ = s0.x; og = s0.y; ob = s0.z; oa = s0.w; }
  float rr_ = 0.0f, rg_ = 0.0f, rb_ = 0.0f, ra_ = 0.0f;
  float d = (p->baseY - p->gap) - py;
  if (d > 0.0f && d < p->fadeLen) {
    float ys = p->baseY + d;
    float dx = p->rippleAmp * sinf(p->rippleFreq * d + p->phase) * fminf(1.0f, d / 40.0f);
    float rad = p->blur0 + p->blurGrow * d;
    float ar, ag, ab, aa;
    if (rad < 0.5f) {
      float sx = px + dx;
      float4 sc = (sx < 0.0f || ys < 0.0f || sx > W || ys > H) ? make_float4(0.0f, 0.0f, 0.0f, 0.0f) : _tex2DVecN(src, sx / W, ys / H, 15);
      ar = sc.x; ag = sc.y; ab = sc.z; aa = sc.w;
    } else {
      float sr = 0.0f, sg = 0.0f, sb = 0.0f, sa = 0.0f, sw = 0.0f;
      for (int i = 0; i < p->samples; ++i) {
        float ang = (float)i * 2.39996323f;
        float rr = rad * sqrtf(((float)i + 0.5f) / (float)p->samples);
        float q = rr / rad;
        float w = expf(-3.0f * q * q);
        float sx = px + dx + cosf(ang) * rr, sy = ys + sinf(ang) * rr;
        float4 sc = (sx < 0.0f || sy < 0.0f || sx > W || sy > H) ? make_float4(0.0f, 0.0f, 0.0f, 0.0f) : _tex2DVecN(src, sx / W, sy / H, 15);
        sr += sc.x * w; sg += sc.y * w; sb += sc.z * w; sa += sc.w * w; sw += w;
      }
      ar = sr / sw; ag = sg / sw; ab = sb / sw; aa = sa / sw;
    }
    float f = powf(fminf(fmaxf(1.0f - d / p->fadeLen, 0.0f), 1.0f), p->fadePow) * p->reflOpacity;
    float ta = p->tint[3];
    rr_ = ar * p->tint[0] * f * ta; rg_ = ag * p->tint[1] * f * ta; rb_ = ab * p->tint[2] * f * ta; ra_ = aa * f * ta;
  }
  float k = 1.0f - oa;
  float O = p->opacity;
  _tex2DVec4Write(dst, x, y, make_float4((or_ + rr_ * k) * O, (og + rg_ * k) * O, (ob + rb_ * k) * O, (oa + ra_ * k) * O));
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
  num("Base", "Baseline (frac of height from the bottom)", 0.4, 0, 1); num("Gap", "Gap (px @1920)", 0, -200, 400)
  num("Length", "Reflection Length (px @1920)", 400, 10, 2000); num("FadePow", "Fade Curve (1 = linear)", 1.5, 0.3, 4)
  num("ReflOpacity", "Reflection Opacity", 0.5, 0, 1)
  num("Blur0", "Blur at Baseline (px @1920)", 0, 0, 40); num("BlurGrow", "Blur Growth (px per 100 px)", 4, 0, 30)
  num("RippleAmp", "Ripple Amount (px @1920)", 0, 0, 40); num("RippleFreq", "Ripple Frequency (per 100 px)", 6, 0.5, 40); num("RippleSpeed", "Ripple Speed (cycles per second)", 0.5, -5, 5)
  color("TintC", "Tint", 1, 1, 1, 1, 1)
  num("Quality", "Quality", 1, 0, 2, { INP_Integer = true, INP_MinAllowed = 0, INP_MaxAllowed = 2 })
  check("KeepOrig", "Keep Original (off = reflection only)", 1)
  num("Opacity", "Opacity", 1, 0, 1)
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end

-- Pure CPU stage (unit-tested)
function SMK2_ReflectPrep(req, w, h)
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate"); rate = (rate and rate > 0) and rate or 24
  local rs = self.Comp.RenderStart or 0
  local t = smk.framesToSeconds(req.Time, rs, rate)
  local px = w / 1920
  local samples = ({ 16, 32, 64 })[math.floor(g(req, "Quality") + 0.5) + 1] or 32
  return { size = { w, h }, off = { 0, 0 }, osize = { w, h }, keepOrig = g(req, "KeepOrig") > 0.5 and 1 or 0, samples = samples,
    baseY = g(req, "Base") * h, gap = g(req, "Gap") * px, fadeLen = g(req, "Length") * px, fadePow = g(req, "FadePow"), reflOpacity = g(req, "ReflOpacity"),
    blur0 = g(req, "Blur0") * px, blurGrow = g(req, "BlurGrow") / 100,                                           -- growth is a ratio (px per px): resolution independent
    rippleAmp = g(req, "RippleAmp") * px, rippleFreq = g(req, "RippleFreq") / (100 * px), phase = 2 * math.pi * g(req, "RippleSpeed") * t,
    opacity = g(req, "Opacity"), tint = { g(req, "TintCR"), g(req, "TintCG"), g(req, "TintCB"), g(req, "TintCA") } }
end

-- How far the reflection reaches beyond the input window (px): below the lowest mirrored row, and sideways by ripple + blur.
function SMK2_ReflectPad(req, w, h, dw)
  local px = w / 1920
  local base, gap, len = g(req, "Base") * h, g(req, "Gap") * px, g(req, "Length") * px
  local dmax = math.min(len, math.max(h - base, 0))
  local lowest = base - gap - dmax
  local side = g(req, "RippleAmp") * px + g(req, "Blur0") * px + g(req, "BlurGrow") / 100 * dmax
  side = side > 0 and (math.ceil(side) + 2) or 0
  local bottom = math.max(0, math.ceil(dw.bottom - lowest) + 2)
  if bottom <= 2 then bottom = (side > 0) and (side) or 0 end
  return side, bottom
end

function Process(req)
  local img = I.Image:GetValue(req)
  if not img then OutImage:Set(req, nil) return end
  local out
  local dw = img.DataWindow
  local side, bottom = 0, 0
  if dw then side, bottom = SMK2_ReflectPad(req, img.Width, img.Height, dw) end
  if side > 0 or bottom > 0 then
    -- output window = input data window grown below / sideways by the reflection reach (only IMG_DataWindow places an image, Phase 0 / 2b)
    out = Image({ IMG_Like = img, IMG_DeferAlloc = true, IMG_DataWindow = ImgRectI(dw.left - side, dw.bottom - bottom, dw.right + side, dw.top) })
  else
    out = Image({ IMG_Like = img, IMG_DeferAlloc = true })
  end
  if req:IsPreCalc() then OutImage:Set(req, out) return end        -- P0: DVIPComputeNode is nil on PreCalc requests
  local P = SMK2_ReflectPrep(req, img.Width, img.Height)
  if side > 0 or bottom > 0 then
    local ow = out.DataWindow
    P.off = { ow.left, ow.bottom }; P.osize = { ow.right - ow.left, ow.top - ow.bottom }
  end
  local ok, perr = pcall(function()
    local node = DVIPComputeNode(req, "SMK2ReflectKernel", SMK2ReflectSource, "SMK2ReflectParams", SMK2ReflectParams)
    local b = node:GetParamBlock(SMK2ReflectParams)
    for key, v in pairs(P) do b[key] = v end
    node:SetParamBlock(b)
    node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
    node:AddInput("src", img); node:AddOutput("dst", out)
    if not node:RunSession(req) then error("RunSession failed") end
  end)
  if not ok then print("[SMK2_Reflection] GPU failed: " .. tostring(perr)); out = img end      -- pass-through fallback
  OutImage:Set(req, out)
end
