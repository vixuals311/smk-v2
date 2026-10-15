-- SMK2_LongShadow — flat "long shadow" behind any element, multi-pass GPU (init + log2(length) doubling passes + one composite). Cost grows with log(length), not length.
-- The shadow falls in the chosen direction (deg, positive = counter-clockwise; -45 = down-right) and fades linearly to nothing at Length (px @1920).
-- The output window is padded only on the shadow's side. Shadow alpha comes from the element's alpha; colour and opacity are controls.
-- @include smk_longshadow
FuRegisterClass("SMK2_LongShadow", CT_Tool, {
  REGS_Name = "SMK2 Long Shadow", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SLs",
  REGS_OpDescription = "Long flat shadow with distance fade, multi-pass GPU",
  REG_NoPreCalcProcess = true, REG_TimeVariant = false, REG_Version = 1,
})

SMK2LSParams = [[
  int size[2];
  int off[2];
  int osize[2];
  int passes;
  float shift;
  float dx;
  float dy;
  float slope;
  float curve;
  float opacity;
  float col[4];
]]

-- GPU ports of smk.lsBuild / smk.lsShade (src/core/smk_longshadow.lua). Keep in sync; tests compile these and compare pixels.
SMK2LSInitSource = [[
__KERNEL__ void SMK2LSInitKernel(__CONSTANTREF__ SMK2LSParams *p, __TEXTURE2D__ src, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->osize[0] || y >= p->osize[1]) return;
  int gx = x + p->off[0], gy = y + p->off[1];
  float a = 0.0f;
  if (!(gx < 0 || gy < 0 || gx >= p->size[0] || gy >= p->size[1])) a = _tex2DVecN(src, ((float)gx + 0.5f) / (float)p->size[0], ((float)gy + 0.5f) / (float)p->size[1], 15).w;
  _tex2DVec4Write(dst, x, y, make_float4(a, a, a, a));
}
]]
SMK2LSStepSource = [[
#define SMK_TX(OUT, I, J) { int i_ = (I), j_ = (J); OUT = (i_ < 0 || j_ < 0 || i_ >= w || j_ >= h) ? 0.0f : _tex2DVecN(prev, ((float)i_ + 0.5f) / (float)w, ((float)j_ + 0.5f) / (float)h, 15).x; }
__KERNEL__ void SMK2LSStepKernel(__CONSTANTREF__ SMK2LSParams *p, __TEXTURE2D__ prev, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  int w = p->osize[0], h = p->osize[1];
  if (x >= w || y >= h) return;
  float u = (float)x + 0.5f - p->dx * p->shift - 0.5f, v = (float)y + 0.5f - p->dy * p->shift - 0.5f;
  int i0 = (int)floorf(u), j0 = (int)floorf(v);
  float fx = u - (float)i0, fy = v - (float)j0;
  float a00, a10, a01, a11, c;
  SMK_TX(a00, i0, j0); SMK_TX(a10, i0 + 1, j0); SMK_TX(a01, i0, j0 + 1); SMK_TX(a11, i0 + 1, j0 + 1); SMK_TX(c, x, y);
  float s = (a00 * (1.0f - fx) + a10 * fx) * (1.0f - fy) + (a01 * (1.0f - fx) + a11 * fx) * fy - p->slope * p->shift;
  float m = (s > c) ? s : c;
  _tex2DVec4Write(dst, x, y, make_float4(m, m, m, m));
}
]]
SMK2LSCompSource = [[
__KERNEL__ void SMK2LSCompKernel(__CONSTANTREF__ SMK2LSParams *p, __TEXTURE2D__ src, __TEXTURE2D__ F, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  int w = p->osize[0], h = p->osize[1];
  if (x >= w || y >= h) return;
  int gx = x + p->off[0], gy = y + p->off[1];
  float r = 0.0f, g = 0.0f, b = 0.0f, a = 0.0f;
  if (!(gx < 0 || gy < 0 || gx >= p->size[0] || gy >= p->size[1])) {
    float4 s0 = _tex2DVecN(src, ((float)gx + 0.5f) / (float)p->size[0], ((float)gy + 0.5f) / (float)p->size[1], 15);
    r = s0.x; g = s0.y; b = s0.z; a = s0.w;
  }
  float f = fminf(fmaxf(_tex2DVecN(F, ((float)x + 0.5f) / (float)w, ((float)y + 0.5f) / (float)h, 15).x, 0.0f), 1.0f);
  float sa = ((f > 0.0f) ? powf(f, p->curve) : 0.0f) * p->col[3];
  float k2 = 1.0f - a, O = p->opacity;
  _tex2DVec4Write(dst, x, y, make_float4((r + p->col[0] * sa * k2) * O, (g + p->col[1] * sa * k2) * O, (b + p->col[2] * sa * k2) * O, (a + sa * k2) * O));
}
]]

I = {}
local function num(key, name, def, lo, hi, extra)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "SliderControl", INP_Default = def, INP_MinScale = lo, INP_MaxScale = hi }
  for k, v in pairs(extra or {}) do t[k] = v end
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
  num("Direction", "Shadow Direction (deg: 0 = right, 90 = up, -45 = down-right)", -45, -360, 360)
  num("Length", "Length (px @1920)", 400, 5, 1500)
  num("Curve", "Fade Curve (1 = linear, <1 = longer, brighter)", 1, 0.3, 3)
  color("ShadowC", "Shadow Colour", 1, 0, 0, 0, 0.5)
  num("Opacity", "Opacity", 1, 0, 1)
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end

-- padding only on the shadow's side (px)
function SMK2_LSPad(req, w)
  local L = g(req, "Length") * (w / 1920); local a = g(req, "Direction") * math.pi / 180
  local dx, dy = math.cos(a), math.sin(a)
  return { left = math.ceil(math.max(0, -dx) * L) + 2, right = math.ceil(math.max(0, dx) * L) + 2, bottom = math.ceil(math.max(0, -dy) * L) + 2, top = math.ceil(math.max(0, dy) * L) + 2 }
end

-- Pure CPU stage (unit-tested). ow = padded output window or nil.
function SMK2_LSPrep(req, w, h, ow)
  local L = math.max(g(req, "Length") * (w / 1920), 1)
  local a = g(req, "Direction") * math.pi / 180
  local off, osize = { 0, 0 }, { w, h }
  if ow then off = { ow.left, ow.bottom }; osize = { ow.right - ow.left, ow.top - ow.bottom } end
  return { size = { w, h }, off = off, osize = osize, passes = smk.lsPasses(L), shift = 1, dx = math.cos(a), dy = math.sin(a), slope = 1 / L,
    curve = g(req, "Curve"), opacity = g(req, "Opacity"), col = { g(req, "ShadowCR"), g(req, "ShadowCG"), g(req, "ShadowCB"), g(req, "ShadowCA") } }
end

local function runPass(req, name, source, P, shift, inputs, output)
  local node = DVIPComputeNode(req, name, source, "SMK2LSParams", SMK2LSParams)
  local b = node:GetParamBlock(SMK2LSParams)
  for key, v in pairs(P) do b[key] = v end
  b.shift = shift
  node:SetParamBlock(b)
  node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
  for _, im in ipairs(inputs) do node:AddInput(im.name, im.img) end
  node:AddOutput("dst", output)
  if not node:RunSession(req) then error("RunSession failed: " .. name) end
end

function Process(req)
  local img = I.Image:GetValue(req)
  if not img then OutImage:Set(req, nil) return end
  local dw = img.DataWindow
  local out, ow
  if dw then
    local pd = SMK2_LSPad(req, img.Width)
    ow = ImgRectI(dw.left - pd.left, dw.bottom - pd.bottom, dw.right + pd.right, dw.top + pd.top)       -- only IMG_DataWindow places an image (Phase 0 / 2b)
    out = Image({ IMG_Like = img, IMG_DeferAlloc = true, IMG_DataWindow = ow })
    ow = out.DataWindow or ow
  else
    out = Image({ IMG_Like = img, IMG_DeferAlloc = true })
  end
  if req:IsPreCalc() then OutImage:Set(req, out) return end
  local P = SMK2_LSPrep(req, img.Width, img.Height, ow)
  local ok, perr = pcall(function()
    local function mid() return Image({ IMG_Width = P.osize[1], IMG_Height = P.osize[2], IMG_Depth = img.Depth, IMG_DeferAlloc = true }) end
    local cur = mid()
    runPass(req, "SMK2LSInitKernel", SMK2LSInitSource, P, 0, { { name = "src", img = img } }, cur)
    for k = 1, P.passes do
      local nxt = mid()
      runPass(req, "SMK2LSStepKernel", SMK2LSStepSource, P, 2 ^ (k - 1), { { name = "prev", img = cur } }, nxt)
      cur = nxt
    end
    runPass(req, "SMK2LSCompKernel", SMK2LSCompSource, P, 0, { { name = "src", img = img }, { name = "F", img = cur } }, out)
  end)
  if not ok then print("[SMK2_LongShadow] GPU failed: " .. tostring(perr)); out = img end      -- pass-through fallback
  OutImage:Set(req, out)
end
