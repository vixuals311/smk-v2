-- SMK2_Shape — SDF shape generator with built-in In/Hold/Out motion. One Fuse per element (Phase 1: each Fuse
-- instance costs ~3 ms/frame, so shape + motion live in the same node). Anti-aliased, resolution-independent.
-- @include smk_shape
FuRegisterClass("SMK2_Shape", CT_SourceTool, {
  REGS_Name = "SMK2 Shape", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SSh",
  REGS_OpDescription = "Rect / rounded / pill / ellipse / ring / line with fill, border, shadow, trim and built-in motion",
  REG_Source_GlobalCtrls = true, REG_Source_SizeCtrls = true, REG_Source_AspectCtrls = true,
  REG_NoPreCalcProcess = true, REG_TimeVariant = true, REG_Version = 2,
})

SMK2ShapeParams = [[
  int size[2];
  int shape;
  int fillMode;
  int borderPos;
  float center[2];
  float half[2];
  float radius;
  float thick;
  float bw;
  float cosA;
  float sinA;
  float gradC;
  float gradS;
  float trim;
  float trimStart;
  float shadowOff[2];
  float shadowBlur;
  float opacity;
  float fillA[4];
  float fillB[4];
  float borderCol[4];
  float shadowCol[4];
  float trackCol[4];
]]

-- GPU port of smk.shade() (src/core/smk_shape.lua). Keep both in sync; tests render the Lua oracle.
SMK2ShapeSource = [[
__KERNEL__ void SMK2ShapeKernel(__CONSTANTREF__ SMK2ShapeParams *p, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->size[0] || y >= p->size[1]) return;
  float dx = (float)x + 0.5f - p->center[0];
  float dy = (float)y + 0.5f - p->center[1];
  float lx = p->cosA * dx + p->sinA * dy;
  float ly = -p->sinA * dx + p->cosA * dy;
  float hx = p->half[0], hy = p->half[1];
  float res[2][2];                              // [pass][d, mask]; pass 1 = shadow (offset)
  for (int pass = 0; pass < 2; ++pass) {
    float qx = lx - (pass == 1 ? p->shadowOff[0] : 0.0f);
    float qy = ly - (pass == 1 ? p->shadowOff[1] : 0.0f);
    float d = 0.0f, m = 1.0f;
    if (p->shape == 0) {
      float r = fminf(p->radius, fminf(hx, hy));
      float bx = fabsf(qx) - (hx - r), by = fabsf(qy) - (hy - r);
      d = sqrtf(fmaxf(bx, 0.0f) * fmaxf(bx, 0.0f) + fmaxf(by, 0.0f) * fmaxf(by, 0.0f)) + fminf(fmaxf(bx, by), 0.0f) - r;
    } else if (p->shape == 1) {
      float ax = fmaxf(hx, 0.0001f), ay = fmaxf(hy, 0.0001f);
      d = (sqrtf((qx / ax) * (qx / ax) + (qy / ay) * (qy / ay)) - 1.0f) * fminf(ax, ay);
    } else if (p->shape == 2) {
      float rad = sqrtf(qx * qx + qy * qy);
      d = fabsf(rad - (hx - p->thick * 0.5f)) - p->thick * 0.5f;
      if (p->trim < 0.9999f) {
        float t = atan2f(qx, qy) / 6.28318530718f;
        if (t < 0.0f) t += 1.0f;
        float u = t - p->trimStart;
        u = u - floorf(u);
        m = fminf(fmaxf((p->trim - u) * 6.28318530718f * fmaxf(rad, 1.0f) + 0.5f, 0.0f), 1.0f);
      }
    } else {
      float cx = fminf(fmaxf(qx, -hx), hx);
      d = sqrtf((qx - cx) * (qx - cx) + qy * qy) - p->thick * 0.5f;
      if (p->trim < 0.9999f) {
        float u = qx + hx;
        m = fminf(fmaxf(p->trim * 2.0f * hx - u + 0.5f, 0.0f), 1.0f);
        if (p->trimStart > 0.0001f) m = m * fminf(fmaxf(u - p->trimStart * 2.0f * hx + 0.5f, 0.0f), 1.0f);
      }
    }
    res[pass][0] = d; res[pass][1] = m;
  }
  float d = res[0][0], m = res[0][1];
  float g = 0.0f;
  if (p->fillMode == 1) {
    float gx = p->gradC * lx + p->gradS * ly;
    float ext = fabsf(p->gradC) * hx + fabsf(p->gradS) * hy + 0.0001f;
    g = fminf(fmaxf(gx / (2.0f * ext) + 0.5f, 0.0f), 1.0f);
  } else if (p->fillMode == 2) {
    g = fminf(fmaxf(sqrtf(lx * lx + ly * ly) / (fmaxf(hx, hy) + 0.0001f), 0.0f), 1.0f);
  }
  float fcov = fminf(fmaxf(0.5f - d, 0.0f), 1.0f) * m;
  float fa = (p->fillA[3] + (p->fillB[3] - p->fillA[3]) * g) * fcov;
  float fr = (p->fillA[0] + (p->fillB[0] - p->fillA[0]) * g) * fa;
  float fg = (p->fillA[1] + (p->fillB[1] - p->fillA[1]) * g) * fa;
  float fb = (p->fillA[2] + (p->fillB[2] - p->fillA[2]) * g) * fa;
  float bmin = -p->bw, bmax = 0.0f;
  if (p->borderPos == 1) { bmin = -p->bw * 0.5f; bmax = p->bw * 0.5f; }
  else if (p->borderPos == 2) { bmin = 0.0f; bmax = p->bw; }
  float bcov = 0.0f;
  if (p->bw > 0.0f) {
    float c1 = fminf(fmaxf(0.5f - (d - bmax), 0.0f), 1.0f);
    float c0 = fminf(fmaxf(0.5f - (d - bmin), 0.0f), 1.0f);
    bcov = fmaxf(c1 - c0, 0.0f) * m;
  }
  float ba = p->borderCol[3] * bcov;
  float sa = 0.0f;
  if (p->shadowCol[3] > 0.0f) {
    float blur = fmaxf(p->shadowBlur, 0.5f);
    float t = fminf(fmaxf((res[1][0] + blur) / (2.0f * blur), 0.0f), 1.0f);
    sa = p->shadowCol[3] * (1.0f - t * t * (3.0f - 2.0f * t)) * res[1][1];
  }
  float sr = p->shadowCol[0] * sa, sg = p->shadowCol[1] * sa, sb = p->shadowCol[2] * sa;
  float ta = 0.0f;
  if (p->trackCol[3] > 0.0f && m < 1.0f) ta = p->trackCol[3] * fminf(fmaxf(0.5f - d, 0.0f), 1.0f) * (1.0f - m);
  float tr = p->trackCol[0] * ta, tg = p->trackCol[1] * ta, tb = p->trackCol[2] * ta;
  float kt = 1.0f - ta;
  sr = tr + sr * kt; sg = tg + sg * kt; sb = tb + sb * kt; sa = ta + sa * kt;      // track over shadow
  float k1 = 1.0f - fa;
  float orr = fr + sr * k1, og = fg + sg * k1, ob = fb + sb * k1, oa = fa + sa * k1;
  float k2 = 1.0f - ba;
  float O = p->opacity;
  float4 c = make_float4((p->borderCol[0] * ba + orr * k2) * O, (p->borderCol[1] * ba + og * k2) * O,
                         (p->borderCol[2] * ba + ob * k2) * O, (ba + oa * k2) * O);
  _tex2DVec4Write(dst, x, y, c);
}
]]

I = {}
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
local function color(key, name, group, r, g, b, a)
  local ch, def = { "R", "G", "B", "A" }, { r, g, b, a }
  for i = 1, 4 do
    I[key .. ch[i]] = self:AddInput(i == 1 and name or "", key .. ch[i], { LINKID_DataType = "Number",
      INPID_InputControl = "ColorControl", INP_Default = def[i], IC_ControlGroup = group, IC_ControlID = i - 1 })
  end
end
local function phaseControls(p)
  combo(p .. "Engine", p .. " Engine", p == "In" and 1 or 0, smk.ENGINES)
  num(p .. "Fade", p .. " Opacity At Offset", 0, 0, 1)
  num(p .. "SlideDist", p .. " Slide Distance", 0.1, -1, 1)
  num(p .. "SlideAngle", p .. " Slide Angle", p == "In" and 180 or 0, -360, 360)
  num(p .. "Scale", p .. " Scale At Offset", 1, 0, 4)
  num(p .. "Rot", p .. " Rotation At Offset (deg)", 0, -360, 360)
  num(p .. "Stiff", p .. " Spring Stiffness", 180, 1, 1000)
  num(p .. "Damp", p .. " Spring Damping", 18, 0, 100)
  num(p .. "Mass", p .. " Spring Mass", 1, 0.1, 10)
  num(p .. "X1", p .. " Bezier x1", 0.25, 0, 1); num(p .. "Y1", p .. " Bezier y1", 0.1, -1, 2)
  num(p .. "X2", p .. " Bezier x2", 0.25, 0, 1); num(p .. "Y2", p .. " Bezier y2", 1, -1, 2)
  num(p .. "Amp", p .. " Elastic Amplitude", 1, 1, 4); num(p .. "Period", p .. " Elastic Period", 0.3, 0.05, 1)
  num(p .. "Back", p .. " Overshoot", 1.70158, 0, 5); num(p .. "Decay", p .. " Inertia Decay", 4, 0.5, 12)
end

function Create()
  combo("Shape", "Shape", 0, { "Rectangle", "Ellipse", "Ring / Arc", "Line" })
  num("W", "Width (frac of frame width)", 0.3, 0.001, 2); num("H", "Height (frac of frame width)", 0.15, 0.001, 2)
  num("Radius", "Corner Radius (0.5 = pill)", 0.15, 0, 0.5)
  num("Thick", "Ring / Line Thickness (px @1920)", 24, 0.5, 400)
  num("Trim", "Trim / Sweep", 1, 0, 1); num("TrimStart", "Trim Start", 0, 0, 1)
  num("Angle", "Angle (deg, CCW)", 0, -360, 360)
  num("CX", "Center X", 0.5, -2, 3); num("CY", "Center Y", 0.5, -2, 3)
  combo("FillMode", "Fill", 0, { "Solid", "Linear Gradient", "Radial Gradient" })
  color("FillA", "Fill Color", 1, 1, 1, 1, 1); color("FillB", "Fill Color B", 2, 0.4, 0.6, 1, 1)
  num("GradAngle", "Gradient Angle (deg)", 90, -360, 360)
  num("BW", "Border Width (px @1920)", 0, 0, 100)
  combo("BPos", "Border Position", 0, { "Inside", "Center", "Outside" })
  color("BC", "Border Color", 3, 1, 1, 1, 1)
  color("SC", "Shadow Color", 4, 0, 0, 0, 0.35)
  color("TC", "Track Color (Trim remainder)", 6, 1, 1, 1, 0)
  num("SX", "Shadow X (px @1920)", 0, -200, 200); num("SY", "Shadow Y, down (px @1920)", 12, -200, 200)
  num("SB", "Shadow Blur (px @1920)", 16, 0, 200)
  num("InDelay", "In Delay (s)", 0, 0, 10, { INP_MinAllowed = 0 })
  num("InDur", "In Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  I.HasOut = self:AddInput("Enable Out", "HasOut", { LINKID_DataType = "Number",
    INPID_InputControl = "CheckboxControl", INP_Default = 1 })
  num("OutOffset", "Out Offset (s)", 0, 0, 10, { INP_MinAllowed = 0 })
  num("OutDur", "Out Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  num("Index", "Index", 0, 0, 500, { INP_Integer = true, INP_MinAllowed = 0 })
  num("Stagger", "Stagger (s)", 0, 0, 1, { INP_MinAllowed = 0 })
  num("ClipLen", "Clip Length (s, 0=auto)", 0, 0, 600, { INP_MinAllowed = 0 })
  phaseControls("In"); phaseControls("Out")
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end
local function col(req, k) return { g(req, k .. "R"), g(req, k .. "G"), g(req, k .. "B"), g(req, k .. "A") } end

local function engineCfg(req, p)
  return { engine = math.floor(g(req, p .. "Engine") + 0.5) + 1, stiffness = g(req, p .. "Stiff"),
    damping = g(req, p .. "Damp"), mass = g(req, p .. "Mass"), amp = g(req, p .. "Amp"), period = g(req, p .. "Period"),
    s = g(req, p .. "Back"), k = g(req, p .. "Decay"), x1 = g(req, p .. "X1"), y1 = g(req, p .. "Y1"),
    x2 = g(req, p .. "X2"), y2 = g(req, p .. "Y2") }
end

-- Pure CPU stage (unit-tested): all geometry in output pixels, motion applied (scale about the shape centre).
function SMK2_ShapePrep(req, w, h)
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate")
  rate = (rate and rate > 0) and rate or 24
  local rs, re = self.Comp.RenderStart or 0, self.Comp.RenderEnd or 0
  local T = g(req, "ClipLen"); if T <= 0 then T = smk.clipSeconds(rs, re, rate) end
  local tm = { inDelay = g(req, "InDelay"), inDur = g(req, "InDur"), outOffset = g(req, "OutOffset"),
    outDur = g(req, "OutDur"), index = g(req, "Index"), stagger = g(req, "Stagger"), hasOut = g(req, "HasOut") > 0.5 }
  local a, phase = smk.animAmount(smk.framesToSeconds(req.Time, rs, rate), T, tm, engineCfg(req, "In"), engineCfg(req, "Out"))
  local p = (phase == "out") and "Out" or "In"
  local r = smk.rigOut(a, { w = w, h = h, slideDist = g(req, p .. "SlideDist"), slideAngle = g(req, p .. "SlideAngle"),
    scaleFrom = g(req, p .. "Scale"), rotFrom = g(req, p .. "Rot"), fadeFrom = g(req, p .. "Fade") })
  local k, px = r.scale, w / 1920                    -- px@1920 -> output pixels
  local hx, hy = g(req, "W") * w * 0.5 * k, g(req, "H") * w * 0.5 * k
  local shape = math.floor(g(req, "Shape") + 0.5)
  local rot = (g(req, "Angle") + r.angle) * math.pi / 180
  local ga = g(req, "GradAngle") * math.pi / 180
  local P = {
    size = { w, h }, shape = shape, fillMode = math.floor(g(req, "FillMode") + 0.5), borderPos = math.floor(g(req, "BPos") + 0.5),
    center = { (g(req, "CX") + r.dx) * w, (g(req, "CY") + r.dy) * h }, half = { hx, hy },
    radius = g(req, "Radius") * math.min(hx, hy) * 2, thick = g(req, "Thick") * px * k, bw = g(req, "BW") * px * k,
    cosA = math.cos(rot), sinA = math.sin(rot), gradC = math.cos(ga), gradS = math.sin(ga),
    trim = g(req, "Trim"), trimStart = g(req, "TrimStart"),
    shadowOff = { g(req, "SX") * px * k, -g(req, "SY") * px * k }, shadowBlur = g(req, "SB") * px * k,
    opacity = r.opacity, fillA = col(req, "FillA"), fillB = col(req, "FillB"), borderCol = col(req, "BC"), shadowCol = col(req, "SC"), trackCol = col(req, "TC"),
  }
  if shape == 2 then P.half = { hx, hx }; P.radius = 0 end          -- ring: Width = diameter
  if shape == 3 then P.half = { hx, 0 } end                          -- line: Width = length
  return P, a, phase
end

function Process(req)
  local out = Image({ IMG_Width = Width, IMG_Height = Height, IMG_Depth = Depth, IMG_DeferAlloc = true })
  if req:IsPreCalc() then OutImage:Set(req, out) return end        -- P0: DVIPComputeNode is nil on PreCalc requests
  local w, h = out.Width, out.Height
  local P = SMK2_ShapePrep(req, w, h)
  local ok, perr = pcall(function()
    local node = DVIPComputeNode(req, "SMK2ShapeKernel", SMK2ShapeSource, "SMK2ShapeParams", SMK2ShapeParams)
    local b = node:GetParamBlock(SMK2ShapeParams)
    for key, v in pairs(P) do b[key] = v end
    node:SetParamBlock(b)
    node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
    node:AddOutput("dst", out)
    if not node:RunSession(req) then error("RunSession failed") end
  end)
  if not ok then
    print("[SMK2_Shape] GPU failed: " .. tostring(perr))
    out = Image({ IMG_Width = Width, IMG_Height = Height, IMG_Depth = Depth }); out:Fill(Pixel({ R = 0, G = 0, B = 0, A = 0 }))
  end
  OutImage:Set(req, out)
end
