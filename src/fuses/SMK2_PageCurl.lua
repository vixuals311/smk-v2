-- SMK2_PageCurl — page-curl transition / reveal in ONE GPU pass. The page rolls over a cylinder; the back of the paper (tinted, dimmed) lies over the front.
-- Input = the page; optional Reveal input = what shows underneath (transparent if not connected). Auto In/Out in seconds (clip-relative) or a manual Progress.
-- Curl direction = the direction the curl travels (deg, positive = counter-clockwise; 180 = right to left, peeling from the right edge). Sizes are px @1920.
-- @include smk_curl
FuRegisterClass("SMK2_PageCurl", CT_Tool, {
  REGS_Name = "SMK2 Page Curl", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SPc",
  REGS_OpDescription = "Page curl reveal with shaded cylinder, paper back and shadow, one GPU pass",
  REG_NoPreCalcProcess = true, REG_TimeVariant = true, REG_Version = 1,
})

SMK2CurlParams = [[
  int size[2];
  int hasBG;
  float cd;
  float sd;
  float u0;
  float uMin;
  float L;
  float R;
  float shadowStr;
  float shadowLen;
  float ambient;
  float lx;
  float lz;
  float backMix;
  float backDim;
  float opacity;
  float backTint[4];
]]

-- GPU port of smk.curlShade() (src/core/smk_curl.lua). Keep in sync; tests compile this and compare pixels.
SMK2CurlSource = [[
#define SMK_SAMPLE(OUT, U) { float sx_ = qx + p->cd * (U), sy_ = qy + p->sd * (U); OUT = (sx_ < 0.0f || sy_ < 0.0f || sx_ > W || sy_ > H) ? make_float4(0.0f, 0.0f, 0.0f, 0.0f) : _tex2DVecN(src, sx_ / W, sy_ / H, 15); }
#define SMK_OVER(C, SH, CV) { float ta_ = (C).w * (CV), kk_ = 1.0f - ta_; rr = (C).x * (SH) * (CV) + rr * kk_; rg = (C).y * (SH) * (CV) + rg * kk_; rb = (C).z * (SH) * (CV) + rb * kk_; ra = ta_ + ra * kk_; }
#define SMK_BACK(C) { float bk_ = p->backMix; (C).x = ((C).x * (1.0f - bk_) + p->backTint[0] * (C).w * bk_) * p->backDim; (C).y = ((C).y * (1.0f - bk_) + p->backTint[1] * (C).w * bk_) * p->backDim; (C).z = ((C).z * (1.0f - bk_) + p->backTint[2] * (C).w * bk_) * p->backDim; }
__KERNEL__ void SMK2CurlKernel(__CONSTANTREF__ SMK2CurlParams *p, __TEXTURE2D__ src, __TEXTURE2D__ bg, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->size[0] || y >= p->size[1]) return;
  float W = (float)p->size[0], H = (float)p->size[1];
  float px = (float)x + 0.5f, py = (float)y + 0.5f;
  float up = px * p->cd + py * p->sd;
  float qx = px - p->cd * up, qy = py - p->sd * up;
  float t = up - p->u0;
  float rr = 0.0f, rg = 0.0f, rb = 0.0f, ra = 0.0f;
  if (p->hasBG > 0) { float4 b0 = _tex2DVecN(bg, px / W, py / H, 15); rr = b0.x; rg = b0.y; rb = b0.z; ra = b0.w; }
  float4 c;
  if (t < 0.0f) {
    float u = p->u0 + t;
    float cvg = fminf(fmaxf(u - p->uMin + 0.5f, 0.0f), 1.0f);
    if (cvg > 0.0f) {
      SMK_SAMPLE(c, u);
      float te = fminf(0.0f, 3.14159265f * p->R - p->L);
      float sh = (p->L > 0.0f) ? (p->shadowStr * expf(fminf(t - te, 0.0f) / fmaxf(p->shadowLen, 0.001f))) : 0.0f;
      float k = 1.0f - sh;
      SMK_OVER(c, k, cvg);
    }
  }
  if (t >= 0.0f && t <= p->R + 0.5f) {
    float phi = asinf(fminf(fmaxf(t / p->R, 0.0f), 1.0f));
    float edge = fminf(fmaxf(p->R - t + 0.5f, 0.0f), 1.0f);
    float s1 = p->R * phi;
    float cv1 = fminf(fmaxf(p->L - s1 + 0.5f, 0.0f), 1.0f) * edge;
    if (cv1 > 0.0f) {
      float shade = p->ambient + (1.0f - p->ambient) * fminf(fmaxf(sinf(phi) * p->lx + cosf(phi) * p->lz, 0.0f), 1.0f);
      SMK_SAMPLE(c, p->u0 + s1);
      SMK_OVER(c, shade, cv1);
    }
    float s2 = 3.14159265f * p->R - s1;
    float cv2 = fminf(fmaxf(p->L - s2 + 0.5f, 0.0f), 1.0f) * edge;
    if (cv2 > 0.0f) {
      float shade = p->ambient + (1.0f - p->ambient) * fminf(fmaxf(-sinf(phi) * p->lx + cosf(phi) * p->lz, 0.0f), 1.0f);
      SMK_SAMPLE(c, p->u0 + s2);
      SMK_BACK(c);
      SMK_OVER(c, shade, cv2);
    }
  }
  if (t < 0.0f) {
    float s = 3.14159265f * p->R - t;
    float cvd = fminf(fmaxf(p->L - s + 0.5f, 0.0f), 1.0f);
    if (cvd > 0.0f) {
      float shade = p->ambient + (1.0f - p->ambient) * fminf(fmaxf(p->lz, 0.0f), 1.0f);
      SMK_SAMPLE(c, p->u0 + s);
      SMK_BACK(c);
      SMK_OVER(c, shade, cvd);
    }
  }
  float O = p->opacity;
  _tex2DVec4Write(dst, x, y, make_float4(rr * O, rg * O, rb * O, ra * O));
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
local function color(key, name, group, r, g, b, a)
  local ch, def = { "R", "G", "B", "A" }, { r, g, b, a }
  for i = 1, 4 do
    I[key .. ch[i]] = self:AddInput(i == 1 and name or "", key .. ch[i], { LINKID_DataType = "Number",
      INPID_InputControl = "ColorControl", INP_Default = def[i], IC_ControlGroup = group, IC_ControlID = i - 1 })
  end
end

function Create()
  I.Image = self:AddInput("Page", "Image", { LINKID_DataType = "Image", LINK_Main = 1 })
  I.Reveal = self:AddInput("Reveal (optional)", "Reveal", { LINKID_DataType = "Image", LINK_Main = 2, INP_Required = false })
  combo("Mode", "Mode", 0, { "Auto Out (page peels away)", "Auto In (page rolls back on)", "Manual (use Progress)" })
  num("Progress", "Progress (manual)", 0.5, 0, 1)
  num("Delay", "Delay (s)", 0.2, 0, 20, { INP_MinAllowed = 0 }); num("Duration", "Duration (s)", 1.2, 0.05, 20)
  num("Direction", "Curl Direction (deg, 180 = right to left)", 180, -360, 360)
  num("Radius", "Roll Radius (px @1920)", 70, 8, 400)
  num("ShadowStr", "Shadow Strength", 0.55, 0, 1); num("ShadowLen", "Shadow Length (px @1920)", 120, 5, 600)
  num("Ambient", "Ambient Light (0 = deep shading)", 0.45, 0, 1); num("LightAngle", "Light Angle (deg from the viewer)", 35, -80, 80)
  color("BackC", "Paper Back Tint", 1, 0.93, 0.9, 0.82, 1); num("BackMix", "Paper Back Tint Amount", 0.55, 0, 1); num("BackDim", "Paper Back Brightness", 0.85, 0, 1.5)
  num("Opacity", "Opacity", 1, 0, 1)
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end

-- Pure CPU stage (unit-tested)
function SMK2_CurlPrep(req, w, h, hasBG)
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate"); rate = (rate and rate > 0) and rate or 24
  local rs = self.Comp.RenderStart or 0
  local t = smk.framesToSeconds(req.Time, rs, rate)
  local px = w / 1920
  local R = g(req, "Radius") * px
  local th = g(req, "Direction") * math.pi / 180
  local cd, sd = -math.cos(th), -math.sin(th)                         -- u axis points AGAINST the travel direction: the curl moves toward smaller u
  local uMin, uMax = math.huge, -math.huge
  for _, c in ipairs({ { 0, 0 }, { w, 0 }, { 0, h }, { w, h } }) do
    local u = c[1] * cd + c[2] * sd
    uMin, uMax = math.min(uMin, u), math.max(uMax, u)
  end
  local mode = math.floor(g(req, "Mode") + 0.5)
  local p
  if mode == 2 then p = g(req, "Progress")
  else
    local e = smk.cubicBezier(0.65, 0, 0.35, 1, smk.clamp((t - g(req, "Delay")) / math.max(g(req, "Duration"), 1e-3), 0, 1))
    p = (mode == 0) and e or (1 - e)
  end
  p = smk.clamp(p, 0, 1)
  local u0 = (uMax + 1) + ((uMin - R - 1) - (uMax + 1)) * p
  local la = g(req, "LightAngle") * math.pi / 180
  return { size = { w, h }, hasBG = hasBG and 1 or 0, cd = cd, sd = sd, u0 = u0, uMin = uMin, L = math.max(uMax - u0, 0), R = R,
    shadowStr = g(req, "ShadowStr"), shadowLen = g(req, "ShadowLen") * px, ambient = g(req, "Ambient"), lx = math.sin(la), lz = math.cos(la),
    backMix = g(req, "BackMix"), backDim = g(req, "BackDim"), opacity = g(req, "Opacity"),
    backTint = { g(req, "BackCR"), g(req, "BackCG"), g(req, "BackCB"), g(req, "BackCA") }, progress = p }
end

function Process(req)
  local img = I.Image:GetValue(req)
  if not img then OutImage:Set(req, nil) return end
  local rev = I.Reveal:GetValue(req)
  local out = Image({ IMG_Like = img, IMG_DeferAlloc = true })
  if req:IsPreCalc() then OutImage:Set(req, out) return end        -- P0: DVIPComputeNode is nil on PreCalc requests
  local P = SMK2_CurlPrep(req, img.Width, img.Height, rev ~= nil)
  P.progress = nil
  local ok, perr = pcall(function()
    local node = DVIPComputeNode(req, "SMK2CurlKernel", SMK2CurlSource, "SMK2CurlParams", SMK2CurlParams)
    local b = node:GetParamBlock(SMK2CurlParams)
    for key, v in pairs(P) do b[key] = v end
    node:SetParamBlock(b)
    node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
    node:AddInput("src", img); node:AddInput("bg", rev or img); node:AddOutput("dst", out)      -- bg is unused when hasBG = 0 but the slot must be bound
    if not node:RunSession(req) then error("RunSession failed") end
  end)
  if not ok then print("[SMK2_PageCurl] GPU failed: " .. tostring(perr)); out = img end      -- pass-through fallback
  OutImage:Set(req, out)
end
