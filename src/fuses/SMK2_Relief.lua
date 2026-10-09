-- SMK2_Relief — bevel / emboss for any image in ONE GPU pass. Height = alpha or brightness; the slope comes from a single Gaussian-derivative gather
-- (no repeated blurs). Light is a direction (deg, positive = counter-clockwise) plus an elevation. Sizes are px @1920.
-- @include smk_relief
FuRegisterClass("SMK2_Relief", CT_Tool, {
  REGS_Name = "SMK2 Relief", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SRl",
  REGS_OpDescription = "Bevel and emboss from alpha or brightness, one GPU pass",
  REG_NoPreCalcProcess = true, REG_TimeVariant = false, REG_Version = 1,
})

SMK2ReliefParams = [[
  int size[2];
  int samples;
  int srcKind;
  int reliefOnly;
  float sigma;
  float depth;
  float lx;
  float ly;
  float hiAmt;
  float shAmt;
  float blend;
  float opacity;
  float hiCol[4];
  float shCol[4];
]]

-- GPU port of smk.reliefShade() (src/core/smk_relief.lua). Keep in sync; tests compile this and compare pixels.
SMK2ReliefSource = [[
__KERNEL__ void SMK2ReliefKernel(__CONSTANTREF__ SMK2ReliefParams *p, __TEXTURE2D__ src, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->size[0] || y >= p->size[1]) return;
  float W = (float)p->size[0], H = (float)p->size[1];
  float px = (float)x + 0.5f, py = (float)y + 0.5f;
  float4 s0 = _tex2DVecN(src, px / W, py / H, 15);
  float r = s0.x, g = s0.y, b = s0.z, a = s0.w;
  float gx = 0.0f, gy = 0.0f, norm = 0.0f;
  float sig2 = p->sigma * p->sigma;
  float R = 3.0f * p->sigma;
  for (int i = 0; i < p->samples; ++i) {
    float ang = (float)i * 2.39996323f;
    float rr = R * sqrtf(((float)i + 0.5f) / (float)p->samples);
    float ox = cosf(ang) * rr, oy = sinf(ang) * rr;
    float w = expf(-(rr * rr) / (2.0f * sig2));
    float sx = px + ox, sy = py + oy;
    float4 sc = (sx < 0.0f || sy < 0.0f || sx > W || sy > H) ? make_float4(0.0f, 0.0f, 0.0f, 0.0f) : _tex2DVecN(src, sx / W, sy / H, 15);
    float v = sc.w;
    if (p->srcKind != 0) {
      float ia = (sc.w > 0.000001f) ? (1.0f / sc.w) : 0.0f;
      v = (0.2126f * sc.x + 0.7152f * sc.y + 0.0722f * sc.z) * ia * sc.w;
    }
    gx += ox * w * v; gy += oy * w * v; norm += w;
  }
  float gradx = 0.0f, grady = 0.0f;
  if (norm > 0.0f) { gradx = gx / (norm * sig2); grady = gy / (norm * sig2); }
  float sxs = p->depth * p->sigma * gradx, sys = p->depth * p->sigma * grady;
  float len = sqrtf(sxs * sxs + sys * sys + 1.0f);
  float relief = (-sxs * p->lx - sys * p->ly) / len;
  float O = p->opacity;
  if (p->reliefOnly > 0) {
    float gray = fminf(fmaxf(0.5f + relief * 0.5f * (p->hiAmt + p->shAmt) * 0.5f, 0.0f), 1.0f) * a;
    _tex2DVec4Write(dst, x, y, make_float4(gray * O, gray * O, gray * O, a * O));
    return;
  }
  float hi = fminf(fmaxf(fmaxf(relief, 0.0f) * p->hiAmt, 0.0f), 1.0f) * p->hiCol[3];
  float sh = fminf(fmaxf(fmaxf(-relief, 0.0f) * p->shAmt, 0.0f), 1.0f) * p->shCol[3];
  float nr = r + (p->shCol[0] * a - r) * sh, ng = g + (p->shCol[1] * a - g) * sh, nb = b + (p->shCol[2] * a - b) * sh;
  nr = nr + (p->hiCol[0] * a - nr) * hi; ng = ng + (p->hiCol[1] * a - ng) * hi; nb = nb + (p->hiCol[2] * a - nb) * hi;
  float k = p->blend;
  _tex2DVec4Write(dst, x, y, make_float4((r + (nr - r) * k) * O, (g + (ng - g) * k) * O, (b + (nb - b) * k) * O, a * O));
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
  I.Image = self:AddInput("Image", "Image", { LINKID_DataType = "Image", LINK_Main = 1 })
  combo("Mode", "Mode", 0, { "Bevel (coloured highlight + shadow)", "Relief Map (grey)" })
  combo("HeightFrom", "Height From", 0, { "Alpha", "Brightness" })
  num("Size", "Size (px @1920)", 8, 0.5, 80); num("Depth", "Depth", 2, 0, 12)
  num("Direction", "Light Direction (deg, + = counter-clockwise)", 135, -360, 360); num("Elevation", "Light Elevation (deg)", 45, 5, 89)
  num("Highlight", "Highlight Amount", 1.5, 0, 5); num("Shadow", "Shadow Amount", 1.5, 0, 5)
  color("HiC", "Highlight Colour", 1, 1, 1, 1, 1); color("ShC", "Shadow Colour", 2, 0, 0, 0, 1)
  num("Blend", "Blend", 1, 0, 1); combo("Quality", "Quality", 1, { "Draft (24)", "Normal (48)", "High (96)" })
  num("Opacity", "Opacity", 1, 0, 1)
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end
local function col(req, k) return { g(req, k .. "R"), g(req, k .. "G"), g(req, k .. "B"), g(req, k .. "A") } end

-- Pure CPU stage (unit-tested)
function SMK2_ReliefPrep(req, w, h)
  local px = w / 1920
  local dir, el = g(req, "Direction") * math.pi / 180, g(req, "Elevation") * math.pi / 180
  local sigma = math.max(0.5, g(req, "Size") * px)
  local samples = ({ 24, 48, 96 })[math.floor(g(req, "Quality") + 0.5) + 1] or 48
  samples = math.min(160, math.max(samples, math.floor(sigma * 3)))                        -- big sizes need more taps
  return { size = { w, h }, samples = samples, srcKind = math.floor(g(req, "HeightFrom") + 0.5), reliefOnly = math.floor(g(req, "Mode") + 0.5),
    sigma = sigma, depth = g(req, "Depth"), lx = math.cos(el) * math.cos(dir), ly = math.cos(el) * math.sin(dir),
    hiAmt = g(req, "Highlight"), shAmt = g(req, "Shadow"), blend = g(req, "Blend"), opacity = g(req, "Opacity"), hiCol = col(req, "HiC"), shCol = col(req, "ShC") }
end

function Process(req)
  local img = I.Image:GetValue(req)
  if not img then OutImage:Set(req, nil) return end
  local out = Image({ IMG_Like = img, IMG_DeferAlloc = true })
  if req:IsPreCalc() then OutImage:Set(req, out) return end        -- P0: DVIPComputeNode is nil on PreCalc requests
  local P = SMK2_ReliefPrep(req, img.Width, img.Height)
  local ok, perr = pcall(function()
    local node = DVIPComputeNode(req, "SMK2ReliefKernel", SMK2ReliefSource, "SMK2ReliefParams", SMK2ReliefParams)
    local b = node:GetParamBlock(SMK2ReliefParams)
    for key, v in pairs(P) do b[key] = v end
    node:SetParamBlock(b)
    node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
    node:AddInput("src", img); node:AddOutput("dst", out)
    if not node:RunSession(req) then error("RunSession failed") end
  end)
  if not ok then print("[SMK2_Relief] GPU failed: " .. tostring(perr)); out = img end      -- pass-through fallback
  OutImage:Set(req, out)
end
