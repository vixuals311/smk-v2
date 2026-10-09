-- SMK2_Look — finishing pass for any image: glow, outline, shine sweep, gradient overlay. One Fuse, one GPU pass (bounded sample counts).
-- Premultiplied-correct; sizes in px @1920 so it looks the same at any resolution. Shine can auto-sweep (seconds, clip-relative).
-- @include smk_look
FuRegisterClass("SMK2_Look", CT_Tool, {
  REGS_Name = "SMK2 Look", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SLk",
  REGS_OpDescription = "Glow, outline, shine sweep and gradient overlay in one GPU pass",
  REG_NoPreCalcProcess = true, REG_TimeVariant = true, REG_Version = 2,
})

SMK2LookParams = [[
  int size[2];
  int off[2];
  int osize[2];
  int glowOn;
  int glowSamples;
  int glowSrc;
  int glowBehind;
  int outOn;
  int shineOn;
  int gradOn;
  int glowOnly;
  int outRings;
  float glowR;
  float glowI;
  float glowThr;
  float glowGamma;
  float outW;
  float shC;
  float shS;
  float shPos;
  float shW;
  float shSoft;
  float shI;
  float gC;
  float gS;
  float gExt;
  float gAmt;
  float opacity;
  float glowCol[4];
  float outCol[4];
  float shCol[4];
  float gA[4];
  float gB[4];
]]

-- GPU port of smk.lookShade() (src/core/smk_look.lua). Keep in sync; tests compile this and compare pixels.
SMK2LookSource = [[
__KERNEL__ void SMK2LookKernel(__CONSTANTREF__ SMK2LookParams *p, __TEXTURE2D__ src, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->osize[0] || y >= p->osize[1]) return;
  float W = (float)p->size[0], H = (float)p->size[1];
  float px = (float)(x + p->off[0]) + 0.5f, py = (float)(y + p->off[1]) + 0.5f;
  float4 s0 = (px < 0.0f || py < 0.0f || px > W || py > H) ? make_float4(0.0f, 0.0f, 0.0f, 0.0f) : _tex2DVecN(src, px / W, py / H, 15);
  float r = s0.x, g = s0.y, b = s0.z, a = s0.w;
  if (p->gradOn > 0 && a > 0.0f) {
    float t = fminf(fmaxf(((px - W * 0.5f) * p->gC + (py - H * 0.5f) * p->gS) / (2.0f * p->gExt) + 0.5f, 0.0f), 1.0f);
    float ia = 1.0f / a;
    float ur = r * ia, ug = g * ia, ub = b * ia;
    float gr = p->gA[0] + (p->gB[0] - p->gA[0]) * t, gg = p->gA[1] + (p->gB[1] - p->gA[1]) * t, gb = p->gA[2] + (p->gB[2] - p->gA[2]) * t;
    float k = p->gAmt * (p->gA[3] + (p->gB[3] - p->gA[3]) * t);
    r = (ur + (gr - ur) * k) * a; g = (ug + (gg - ug) * k) * a; b = (ub + (gb - ub) * k) * a;
  }
  if (p->shineOn > 0 && a > 0.0f) {
    float s = (px - W * 0.5f) * p->shC + (py - H * 0.5f) * p->shS - p->shPos;
    float soft = fmaxf(p->shSoft, 0.5f);
    float bnd = fminf(fmaxf((p->shW + soft - fabsf(s)) / soft, 0.0f), 1.0f);
    bnd = bnd * bnd * (3.0f - 2.0f * bnd);
    float k = bnd * p->shI * p->shCol[3] * a;
    r += p->shCol[0] * k; g += p->shCol[1] * k; b += p->shCol[2] * k;
  }
  float gl[4] = {0.0f, 0.0f, 0.0f, 0.0f};
  if (p->glowOn > 0 && p->glowR > 0.5f) {
    float acc = 0.0f, norm = 0.0f;
    for (int i = 0; i < p->glowSamples; ++i) {
      float ang = (float)i * 2.39996323f;
      float rr = p->glowR * sqrtf(((float)i + 0.5f) / (float)p->glowSamples);
      float q = rr / p->glowR;
      float w = expf(-3.0f * q * q);
      float sx = px + cosf(ang) * rr, sy = py + sinf(ang) * rr;
      float4 sc = (sx < 0.0f || sy < 0.0f || sx > W || sy > H) ? make_float4(0.0f, 0.0f, 0.0f, 0.0f) : _tex2DVecN(src, sx / W, sy / H, 15);
      float v = sc.w;
      if (p->glowSrc != 0) {
        float ia = (sc.w > 0.000001f) ? (1.0f / sc.w) : 0.0f;
        float lum = (0.2126f * sc.x + 0.7152f * sc.y + 0.0722f * sc.z) * ia;
        v = fminf(fmaxf((lum - p->glowThr) / fmaxf(1.0f - p->glowThr, 0.0001f), 0.0f), 1.0f) * sc.w;
      }
      acc += v * w; norm += w;
    }
    float v0 = (norm > 0.0f) ? (acc / norm) : 0.0f;
    float v = ((v0 > 0.0f) ? powf(v0, p->glowGamma) : 0.0f) * p->glowI;
    float ga = fminf(fmaxf(v * p->glowCol[3], 0.0f), 1.0f);
    gl[0] = p->glowCol[0] * ga; gl[1] = p->glowCol[1] * ga; gl[2] = p->glowCol[2] * ga; gl[3] = ga;
  }
  float br = 0.0f, bg = 0.0f, bb = 0.0f, ba = 0.0f;
  if (p->glowOn > 0 && p->glowBehind > 0) { br = gl[0]; bg = gl[1]; bb = gl[2]; ba = gl[3]; }
  if (p->outOn > 0 && p->outW > 0.25f) {
    float m = a;
    for (int k = 1; k <= p->outRings; ++k) {
      float rad = p->outW * (float)k / (float)p->outRings;
      for (int i = 0; i < 24; ++i) {
        float ang = (float)i * 0.26179939f + (float)k * 0.3f;
        float sx = px + cosf(ang) * rad, sy = py + sinf(ang) * rad;
        float4 sc = (sx < 0.0f || sy < 0.0f || sx > W || sy > H) ? make_float4(0.0f, 0.0f, 0.0f, 0.0f) : _tex2DVecN(src, sx / W, sy / H, 15);
        if (sc.w > m) m = sc.w;
      }
    }
    float oc = fminf(fmaxf(m - a, 0.0f), 1.0f);
    float oa = oc * p->outCol[3], kk = 1.0f - oa;
    br = p->outCol[0] * oa + br * kk; bg = p->outCol[1] * oa + bg * kk; bb = p->outCol[2] * oa + bb * kk; ba = oa + ba * kk;
  }
  if (p->glowOn > 0 && p->glowOnly > 0) {
    float O0 = p->opacity;
    _tex2DVec4Write(dst, x, y, make_float4(gl[0] * O0, gl[1] * O0, gl[2] * O0, gl[3] * O0));
    return;
  }
  float k2 = 1.0f - a;
  float rr2 = r + br * k2, rg = g + bg * k2, rb = b + bb * k2, ra = a + ba * k2;
  if (p->glowOn > 0 && p->glowBehind == 0) {
    rr2 += gl[0]; rg += gl[1]; rb += gl[2];
    ra = fminf(fmaxf(ra + gl[3] * (1.0f - ra), 0.0f), 1.0f);
  }
  float O = p->opacity;
  _tex2DVec4Write(dst, x, y, make_float4(rr2 * O, rg * O, rb * O, ra * O));
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
  check("GlowOn", "Glow", 1); combo("GlowSrc", "Glow From", 0, { "Alpha", "Brightness" })
  num("GlowR", "Glow Radius (px @1920)", 40, 1, 300); num("GlowI", "Glow Intensity", 1.2, 0, 6); num("GlowThr", "Brightness Threshold", 0.6, 0, 0.99)
  combo("GlowQ", "Glow Quality", 1, { "Draft (24)", "Normal (48)", "High (96)", "Max (160)" })
  num("GlowGamma", "Glow Spread (gamma; below 1 = wider, brighter tails)", 1, 0.3, 3); check("GlowOnly", "Glow Only (no object)", 0)
  check("GlowBehind", "Glow Behind Object (off = additive)", 0); color("GlowC", "Glow Color", 1, 0.45, 0.65, 1, 1)
  check("OutOn", "Outline", 0); num("OutW", "Outline Width (px @1920)", 6, 0.5, 60); color("OutC", "Outline Color", 2, 1, 1, 1, 1)
  check("ShineOn", "Shine", 0); num("ShineAngle", "Shine Angle (deg)", 25, -180, 180)
  num("ShineW", "Shine Half-Width (frac of frame width)", 0.04, 0.002, 0.5); num("ShineSoft", "Shine Softness (frac of frame width)", 0.03, 0, 0.3)
  num("ShineI", "Shine Intensity", 0.8, 0, 3); color("ShineC", "Shine Color", 3, 1, 1, 1, 1)
  num("ShinePos", "Shine Position (manual, -1..1)", -1, -1.5, 1.5)
  check("ShineAuto", "Shine Auto Sweep (seconds, clip-relative)", 1)
  num("ShineDelay", "Sweep Delay (s)", 0.4, 0, 10, { INP_MinAllowed = 0 }); num("ShineDur", "Sweep Duration (s)", 0.9, 0.05, 10)
  num("ShineRepeat", "Repeat Every (s, 0 = once)", 0, 0, 20, { INP_MinAllowed = 0 })
  check("GradOn", "Gradient Overlay", 0); color("GradA", "Gradient Color A", 4, 1, 0.5, 0.2, 1); color("GradB", "Gradient Color B", 5, 0.4, 0.3, 1, 1)
  num("GradAngle", "Gradient Angle (deg)", 90, -360, 360); num("GradAmt", "Gradient Amount", 1, 0, 1)
  num("Opacity", "Opacity", 1, 0, 1)
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end
local function col(req, k) return { g(req, k .. "R"), g(req, k .. "G"), g(req, k .. "B"), g(req, k .. "A") } end

-- Pure CPU stage (unit-tested)
function SMK2_LookPrep(req, w, h)
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate"); rate = (rate and rate > 0) and rate or 24
  local rs = self.Comp.RenderStart or 0
  local t = smk.framesToSeconds(req.Time, rs, rate)
  local px = w / 1920
  local ang = g(req, "ShineAngle") * math.pi / 180
  local sc, ss = math.cos(ang), math.sin(ang)
  local ext = math.abs(sc) * w * 0.5 + math.abs(ss) * h * 0.5                                  -- half extent of the frame along the shine axis
  local halfW = g(req, "ShineW") * w
  local pos
  if g(req, "ShineAuto") > 0.5 then
    local tt = t - g(req, "ShineDelay")
    local rep = g(req, "ShineRepeat")
    if rep > 0 and tt >= 0 then tt = tt % rep end
    local p = smk.clamp(tt / math.max(g(req, "ShineDur"), 1e-3), 0, 1)
    local e = smk.cubicBezier(0.65, 0, 0.35, 1, p)
    pos = (tt < 0 or (rep <= 0 and tt > g(req, "ShineDur"))) and (ext + halfW + 1e4) or (-(ext + halfW) + e * 2 * (ext + halfW))
  else
    pos = g(req, "ShinePos") * (ext + halfW)
  end
  local ga = g(req, "GradAngle") * math.pi / 180
  local samples = ({ 24, 48, 96, 160 })[math.floor(g(req, "GlowQ") + 0.5) + 1] or 48
  samples = math.min(160, math.max(samples, math.floor(g(req, "GlowR") * px * 0.8)))      -- wide glows need more taps (no blocky ghosts at big radii)
  local rings = math.max(3, math.min(8, math.ceil(g(req, "OutW") * px / 3)))              -- wide outlines need more rings (no stair-steps)
  return { size = { w, h }, off = { 0, 0 }, osize = { w, h }, glowOn = g(req, "GlowOn") > 0.5 and 1 or 0, glowSamples = samples, glowOnly = g(req, "GlowOnly") > 0.5 and 1 or 0, outRings = rings, glowGamma = g(req, "GlowGamma"), glowSrc = math.floor(g(req, "GlowSrc") + 0.5),
    glowBehind = g(req, "GlowBehind") > 0.5 and 1 or 0, outOn = g(req, "OutOn") > 0.5 and 1 or 0, shineOn = g(req, "ShineOn") > 0.5 and 1 or 0,
    gradOn = g(req, "GradOn") > 0.5 and 1 or 0, glowR = g(req, "GlowR") * px, glowI = g(req, "GlowI"), glowThr = g(req, "GlowThr"), outW = g(req, "OutW") * px,
    shC = sc, shS = ss, shPos = pos, shW = halfW, shSoft = g(req, "ShineSoft") * w, shI = g(req, "ShineI"),
    gC = math.cos(ga), gS = math.sin(ga), gExt = math.abs(math.cos(ga)) * w * 0.5 + math.abs(math.sin(ga)) * h * 0.5 + 1e-4, gAmt = g(req, "GradAmt"),
    opacity = g(req, "Opacity"), glowCol = col(req, "GlowC"), outCol = col(req, "OutC"), shCol = col(req, "ShineC"), gA = col(req, "GradA"), gB = col(req, "GradB") }
end

-- how far glow / outline reach beyond the input (px). Shine and gradient only act where the input has alpha, so they need no padding.
function SMK2_LookPad(req, w)
  local px = w / 1920
  local pad = 0
  if g(req, "GlowOn") > 0.5 then pad = pad + g(req, "GlowR") * px end
  if g(req, "OutOn") > 0.5 then pad = pad + g(req, "OutW") * px end
  return pad > 0 and (math.ceil(pad) + 2) or 0
end

function Process(req)
  local img = I.Image:GetValue(req)
  if not img then OutImage:Set(req, nil) return end
  local pad = SMK2_LookPad(req, img.Width)
  local out
  local dw = img.DataWindow
  if pad > 0 and dw then
    -- output window = input data window grown by glow + outline reach (only IMG_DataWindow places an image, Phase 0 / 2b)
    out = Image({ IMG_Like = img, IMG_DeferAlloc = true, IMG_DataWindow = ImgRectI(dw.left - pad, dw.bottom - pad, dw.right + pad, dw.top + pad) })
  else
    out = Image({ IMG_Like = img, IMG_DeferAlloc = true }); pad = 0
  end
  if req:IsPreCalc() then OutImage:Set(req, out) return end        -- P0: DVIPComputeNode is nil on PreCalc requests
  local P = SMK2_LookPrep(req, img.Width, img.Height)
  if pad > 0 then
    local ow = out.DataWindow
    P.off = { ow.left, ow.bottom }; P.osize = { ow.right - ow.left, ow.top - ow.bottom }
  end
  local ok, perr = pcall(function()
    local node = DVIPComputeNode(req, "SMK2LookKernel", SMK2LookSource, "SMK2LookParams", SMK2LookParams)
    local b = node:GetParamBlock(SMK2LookParams)
    for key, v in pairs(P) do b[key] = v end
    node:SetParamBlock(b)
    node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
    node:AddInput("src", img); node:AddOutput("dst", out)
    if not node:RunSession(req) then error("RunSession failed") end
  end)
  if not ok then print("[SMK2_Look] GPU failed: " .. tostring(perr)); out = img end      -- pass-through fallback
  OutImage:Set(req, out)
end
