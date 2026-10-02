-- SMK2_Animator — image tool. One GPU pass: In/Hold/Out move (fade, slide, scale, rotate), seconds-based,
-- clip-relative, own engine per phase, Index x Stagger. Full-frame output (S4: DoD shrink unsupported).
-- Motion blur: use a native Transform (S6). Core is inlined at build time.
FuRegisterClass("SMK2_Animator", CT_Tool, {
  REGS_Name = "SMK2 Animator", REGS_Category = "Fuses\\SMK v2",
  REGS_OpIconString = "SAn", REGS_OpDescription = "Seconds-based In/Hold/Out animator (fade, slide, scale, rotate)",
  REG_TimeVariant = true, REG_NoObjMatCtrls = true, REG_Version = 2,
})

SMK2AnimParams = [[
  int size[2];
  float pivot[2];
  float trans[2];
  float invScale;
  float cosA;
  float sinA;
  float opacity;
]]

SMK2AnimSource = [[
__KERNEL__ void SMK2AnimKernel(__CONSTANTREF__ SMK2AnimParams *p, __TEXTURE2D__ src, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->size[0] || y >= p->size[1]) return;
  float qx = ((float)x + 0.5f) - p->pivot[0] - p->trans[0];
  float qy = ((float)y + 0.5f) - p->pivot[1] - p->trans[1];
  float rx = ( p->cosA * qx + p->sinA * qy) * p->invScale + p->pivot[0];
  float ry = (-p->sinA * qx + p->cosA * qy) * p->invScale + p->pivot[1];
  float u = rx / (float)p->size[0];
  float v = ry / (float)p->size[1];
  float4 c = make_float4(0.0f, 0.0f, 0.0f, 0.0f);
  if (u >= 0.0f && u <= 1.0f && v >= 0.0f && v <= 1.0f) c = _tex2DVecN(src, u, v, 15);
  c = c * p->opacity;                       // premultiplied: scale all channels
  _tex2DVec4Write(dst, x, y, c);
}
]]

local I = {}
local function num(key, name, def, lo, hi, extra)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "SliderControl", INP_Default = def,
              INP_MinScale = lo, INP_MaxScale = hi }
  for k, v in pairs(extra or {}) do t[k] = v end
  I[key] = self:AddInput(name, key, t)
end
local function combo(key, name, def, items)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "ComboControl", INP_Default = def, INP_Integer = true }
  for _, n in ipairs(items) do t[#t + 1] = { CCS_AddString = n } end
  I[key] = self:AddInput(name, key, t)
end
local function phaseControls(p, label)
  self:BeginControlNest(label, label, true)
  combo(p .. "Engine", "Engine", p == "In" and 1 or 0, smk.ENGINES)
  num(p .. "Fade", "Opacity At Offset", 0, 0, 1)
  num(p .. "SlideDist", "Slide Distance", 0.1, -1, 1)
  num(p .. "SlideAngle", "Slide Angle", p == "In" and 180 or 0, -360, 360)
  num(p .. "Scale", "Scale At Offset", 1, 0, 4)
  num(p .. "Rot", "Rotation At Offset (deg)", 0, -360, 360)
  num(p .. "Stiff", "Spring Stiffness", 180, 1, 1000)
  num(p .. "Damp", "Spring Damping", 18, 0, 100)
  num(p .. "Mass", "Spring Mass", 1, 0.1, 10)
  num(p .. "X1", "Bezier x1", 0.25, 0, 1); num(p .. "Y1", "Bezier y1", 0.1, -1, 2)
  num(p .. "X2", "Bezier x2", 0.25, 0, 1); num(p .. "Y2", "Bezier y2", 1, -1, 2)
  num(p .. "Amp", "Elastic Amplitude", 1, 1, 4); num(p .. "Period", "Elastic Period", 0.3, 0.05, 1)
  num(p .. "Back", "Overshoot", 1.70158, 0, 5); num(p .. "Decay", "Inertia Decay", 4, 0.5, 12)
  self:EndControlNest()
end

function Create()
  I.Image = self:AddInput("Image", "Image", { LINKID_DataType = "Image", LINK_Main = 1 })
  self:BeginControlNest("Timing", "Timing", true)
  num("InDelay", "In Delay (s)", 0, 0, 10, { INP_MinAllowed = 0 })
  num("InDur", "In Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  I.HasOut = self:AddInput("Enable Out", "HasOut", { LINKID_DataType = "Number",
    INPID_InputControl = "CheckboxControl", INP_Default = 1 })
  num("OutOffset", "Out Offset (s)", 0, 0, 10, { INP_MinAllowed = 0 })
  num("OutDur", "Out Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  num("Index", "Index", 0, 0, 500, { INP_Integer = true, INP_MinAllowed = 0 })
  num("Stagger", "Stagger (s)", 0, 0, 1, { INP_MinAllowed = 0 })
  num("ClipLen", "Clip Length (s, 0=auto)", 0, 0, 600, { INP_MinAllowed = 0 })
  self:EndControlNest()
  self:BeginControlNest("Pivot", "Pivot", true)
  num("PivotX", "Pivot X", 0.5, 0, 1); num("PivotY", "Pivot Y", 0.5, 0, 1)
  self:EndControlNest()
  phaseControls("In", "In"); phaseControls("Out", "Out")
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end

local function engineCfg(req, p)
  return { engine = math.floor(g(req, p .. "Engine") + 0.5) + 1, stiffness = g(req, p .. "Stiff"),
    damping = g(req, p .. "Damp"), mass = g(req, p .. "Mass"), amp = g(req, p .. "Amp"), period = g(req, p .. "Period"),
    s = g(req, p .. "Back"), k = g(req, p .. "Decay"), x1 = g(req, p .. "X1"), y1 = g(req, p .. "Y1"),
    x2 = g(req, p .. "X2"), y2 = g(req, p .. "Y2") }
end

-- Pure CPU stage (unit-tested): everything except the GPU dispatch.
function SMK2_PrepareFrame(req, w, h)
  local c = self.Comp                       -- P0: ffi FusionDoc*, plain fields (no :GetAttrs())
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate")
  rate = (rate and rate > 0) and rate or 24
  local rs, re = c.RenderStart or 0, c.RenderEnd or 0
  local T = g(req, "ClipLen")
  if T <= 0 then T = smk.clipSeconds(rs, re, rate) end
  local t = smk.framesToSeconds(req.Time, rs, rate)
  local tm = { inDelay = g(req, "InDelay"), inDur = g(req, "InDur"), outOffset = g(req, "OutOffset"),
    outDur = g(req, "OutDur"), index = g(req, "Index"), stagger = g(req, "Stagger"), hasOut = g(req, "HasOut") > 0.5 }
  local a, phase = smk.animAmount(t, T, tm, engineCfg(req, "In"), engineCfg(req, "Out"))
  local p = (phase == "out") and "Out" or "In"
  local x = smk.animXform(a, { w = w, h = h, pivotX = g(req, "PivotX"), pivotY = g(req, "PivotY"),
    slideDist = g(req, p .. "SlideDist"), slideAngle = g(req, p .. "SlideAngle"), scaleFrom = g(req, p .. "Scale"),
    rotFrom = g(req, p .. "Rot"), fadeFrom = g(req, p .. "Fade") })
  return x, a, phase
end

function Process(req)
  local img = I.Image:GetValue(req)
  if not img then OutImage:Set(req, nil) return end
  local out = Image({ IMG_Like = img, IMG_DeferAlloc = true })
  if req:IsPreCalc() then OutImage:Set(req, out) return end      -- P0: DVIPComputeNode is nil on PreCalc requests
  local w, h = img.Width, img.Height
  local x = SMK2_PrepareFrame(req, w, h)
  local ok, perr = pcall(function()
    local node = DVIPComputeNode(req, "SMK2AnimKernel", SMK2AnimSource, "SMK2AnimParams", SMK2AnimParams)
    local p = node:GetParamBlock(SMK2AnimParams)
    p.size = { w, h }; p.pivot = { x.px, x.py }; p.trans = { x.tx, x.ty }
    p.invScale, p.cosA, p.sinA, p.opacity = x.invScale, x.c, x.s, x.opacity
    node:SetParamBlock(p)
    node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
    node:AddInput("src", img); node:AddOutput("dst", out)
    if not node:RunSession(req) then error("RunSession failed") end
  end)
  if not ok then print("[SMK2_Animator] GPU failed: " .. tostring(perr)); out = img end   -- pass-through fallback
  OutImage:Set(req, out)
end
