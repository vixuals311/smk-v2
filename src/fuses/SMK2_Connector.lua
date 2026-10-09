-- SMK2_Connector — connector line between two points / boxes. One Fuse: Curve, Straight, Elbow, Bezier (two draggable handles) or Spline
-- (through up to 6 draggable points); magnetic ends that snap to a box edge or a side port; dashes, gradient, dot/arrow ends, travelling pulses;
-- built-in draw-on / un-draw motion with Index x Stagger. Seconds-based, clip-relative.
-- @include smk_connector
FuRegisterClass("SMK2_Connector", CT_SourceTool, {
  REGS_Name = "SMK2 Connector", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SCn",
  REGS_OpDescription = "Editable connector (handles, points, magnets, dashes, arrows, pulses) with draw-on motion",
  REG_Source_GlobalCtrls = true, REG_Source_SizeCtrls = true, REG_Source_AspectCtrls = true,
  REG_NoPreCalcProcess = true, REG_TimeVariant = true, REG_Version = 2,
})

SMK2ConnParams = [[
  int size[2];
  int n;
  int kindA;
  int kindB;
  float total;
  float thick;
  float trim;
  float dash;
  float dgap;
  float gradOn;
  float opacity;
  float visA;
  float pts[384];
  float cum[192];
  float mkA[9];
  float mkB[9];
  float pul[12];
  float pulCol[4];
  float colA[4];
  float colB[4];
]]

-- GPU port of smk.connShade() (src/core/smk_connector.lua). Keep in sync; tests compile this and compare pixels.
SMK2ConnSource = [[
__KERNEL__ void SMK2ConnKernel(__CONSTANTREF__ SMK2ConnParams *p, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->size[0] || y >= p->size[1]) return;
  float px = (float)x + 0.5f, py = (float)y + 0.5f;
  float best = 1.0e30f, bu = 0.0f;
  for (int i = 0; i < p->n - 1; ++i) {
    float ax = p->pts[2 * i], ay = p->pts[2 * i + 1], bx = p->pts[2 * i + 2], by = p->pts[2 * i + 3];
    float ex = bx - ax, ey = by - ay;
    float l2 = ex * ex + ey * ey;
    float t = (l2 > 0.0f) ? fminf(fmaxf(((px - ax) * ex + (py - ay) * ey) / l2, 0.0f), 1.0f) : 0.0f;
    float dx = px - (ax + t * ex), dy = py - (ay + t * ey);
    float d2 = dx * dx + dy * dy;
    if (d2 < best) { best = d2; bu = p->cum[i] + t * sqrtf(l2); }
  }
  float d = sqrtf(best) - p->thick * 0.5f;
  float m = fminf(fmaxf(p->trim * p->total - bu + 0.5f, 0.0f), 1.0f) * fminf(p->trim * 50.0f, 1.0f);
  if (p->dash > 0.0f) {
    float per = p->dash + p->dgap;
    float ph = bu - per * floorf(bu / per);
    m = m * fminf(fmaxf(fminf(ph, p->dash - ph) + 0.5f, 0.0f), 1.0f);
  }
  float g = (p->gradOn > 0.5f && p->total > 0.0f) ? fminf(fmaxf(bu / p->total, 0.0f), 1.0f) : 0.0f;
  float cr = p->colA[0] + (p->colB[0] - p->colA[0]) * g, cg = p->colA[1] + (p->colB[1] - p->colA[1]) * g;
  float cb = p->colA[2] + (p->colB[2] - p->colA[2]) * g, ca = p->colA[3] + (p->colB[3] - p->colA[3]) * g;
  float la = ca * fminf(fmaxf(0.5f - d, 0.0f), 1.0f) * m;
  float orr = cr * la, og = cg * la, ob = cb * la, oa = la;
  for (int e = 0; e < 2; ++e) {
    int kind = (e == 0) ? p->kindA : p->kindB;
    float vis = (e == 0) ? p->visA : fminf(fmaxf((p->trim - 0.92f) / 0.08f, 0.0f), 1.0f);
    float cv = 0.0f;
    if (kind == 1) {
      float cx = (e == 0) ? p->mkA[0] : p->mkB[0], cy = (e == 0) ? p->mkA[1] : p->mkB[1], r = (e == 0) ? p->mkA[2] : p->mkB[2];
      float ddx = px - cx, ddy = py - cy;
      cv = fminf(fmaxf(0.5f - (sqrtf(ddx * ddx + ddy * ddy) - r), 0.0f), 1.0f);
    } else if (kind == 2) {
      float tv[6];
      for (int k = 0; k < 6; ++k) tv[k] = (e == 0) ? p->mkA[3 + k] : p->mkB[3 + k];
      float dd = (px - tv[0]) * (px - tv[0]) + (py - tv[1]) * (py - tv[1]);
      float s = 1.0f;
      int j = 2;
      for (int i = 0; i < 3; ++i) {
        float ax = tv[2 * i], ay = tv[2 * i + 1], bx = tv[2 * j], by = tv[2 * j + 1];
        float ex = bx - ax, ey = by - ay, wx = px - ax, wy = py - ay;
        float t = fminf(fmaxf((wx * ex + wy * ey) / (ex * ex + ey * ey), 0.0f), 1.0f);
        float qx = wx - ex * t, qy = wy - ey * t;
        dd = fminf(dd, qx * qx + qy * qy);
        int c1 = (py >= ay), c2 = (py < by), c3 = (ex * wy > ey * wx);
        if ((c1 && c2 && c3) || ((!c1) && (!c2) && (!c3))) s = -s;
        j = i;
      }
      cv = fminf(fmaxf(0.5f - s * sqrtf(dd), 0.0f), 1.0f);
    }
    if (cv > 0.0f) {
      float mr = (e == 0) ? p->colA[0] : p->colB[0], mg = (e == 0) ? p->colA[1] : p->colB[1];
      float mb = (e == 0) ? p->colA[2] : p->colB[2], ma = (e == 0) ? p->colA[3] : p->colB[3];
      float ta = ma * cv * vis, k = 1.0f - ta;
      orr = mr * ta + orr * k; og = mg * ta + og * k; ob = mb * ta + ob * k; oa = ta + oa * k;
    }
  }
  for (int i = 0; i < 3; ++i) {
    float qa = p->pul[i * 4 + 3];
    if (qa > 0.0f) {
      float ddx = px - p->pul[i * 4], ddy = py - p->pul[i * 4 + 1];
      float ta = p->pulCol[3] * fminf(fmaxf(0.5f - (sqrtf(ddx * ddx + ddy * ddy) - p->pul[i * 4 + 2]), 0.0f), 1.0f) * qa, k = 1.0f - ta;
      orr = p->pulCol[0] * ta + orr * k; og = p->pulCol[1] * ta + og * k; ob = p->pulCol[2] * ta + ob * k; oa = ta + oa * k;
    }
  }
  float O = p->opacity;
  _tex2DVec4Write(dst, x, y, make_float4(orr * O, og * O, ob * O, oa * O));
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
local function point(key, name, x, y)
  I[key] = self:AddInput(name, key, { LINKID_DataType = "Point", INPID_InputControl = "OffsetControl", INPID_PreviewControl = "CrosshairControl", INP_DefaultX = x, INP_DefaultY = y })
end
local function color(key, name, group, r, g, b, a)
  local ch, def = { "R", "G", "B", "A" }, { r, g, b, a }
  for i = 1, 4 do
    I[key .. ch[i]] = self:AddInput(i == 1 and name or "", key .. ch[i], { LINKID_DataType = "Number",
      INPID_InputControl = "ColorControl", INP_Default = def[i], IC_ControlGroup = group, IC_ControlID = i - 1 })
  end
end

function Create()
  combo("Mode", "Path Style", 0, { "Curve", "Straight", "Elbow", "Bezier (handles)", "Spline (through points)" })
  point("AP", "Start Point", 0.25, 0.5); point("BP", "End Point", 0.75, 0.5)
  combo("AMag", "Start Magnet", 0, { "Off", "Auto (edge toward target)", "Top", "Right", "Bottom", "Left" })
  num("AW", "Start Box Width (frac of frame width)", 0.2, 0.005, 1); num("AH", "Start Box Height (frac of frame width)", 0.1, 0.005, 1)
  combo("BMag", "End Magnet", 0, { "Off", "Auto (edge toward target)", "Top", "Right", "Bottom", "Left" })
  num("BW", "End Box Width (frac of frame width)", 0.2, 0.005, 1); num("BH", "End Box Height (frac of frame width)", 0.1, 0.005, 1)
  num("Gap", "Magnet Gap (px @1920)", 6, 0, 60)
  num("Bend", "Curve Bend", 0.45, 0, 1.5)
  num("Radius", "Elbow Corner Radius (px @1920)", 24, 0, 200)
  point("H1", "Handle 1 (Bezier)", 0.4, 0.8); point("H2", "Handle 2 (Bezier)", 0.6, 0.2)
  num("N", "Spline Points (0-6)", 2, 0, 6, { INP_Integer = true, INP_MinAllowed = 0, INP_MaxAllowed = 6 })
  num("Tension", "Spline Tension (0 = polyline, 1 = smooth)", 1, 0, 2)
  point("P1", "Point 1", 0.4, 0.75); point("P2", "Point 2", 0.6, 0.25); point("P3", "Point 3", 0.5, 0.5)
  point("P4", "Point 4", 0.5, 0.6); point("P5", "Point 5", 0.5, 0.4); point("P6", "Point 6", 0.5, 0.5)
  num("Thick", "Line Thickness (px @1920)", 4, 0.5, 60)
  num("Dash", "Dash Length (px @1920, 0 = solid)", 0, 0, 200); num("DGap", "Dash Gap (px @1920)", 12, 0, 200)
  color("LCA", "Line Color", 1, 0.3, 0.55, 1, 1); color("LCB", "End Color (gradient)", 2, 0.7, 0.4, 1, 1)
  check("GradOn", "Gradient Along Line", 0)
  combo("AEnd", "Start End-Mark", 1, { "None", "Dot", "Arrow" }); combo("BEnd", "End End-Mark", 2, { "None", "Dot", "Arrow" })
  num("EndSize", "End-Mark Size (px @1920)", 18, 2, 100)
  check("PulseOn", "Travelling Pulses", 0); num("PulseSpeed", "Pulse Speed (cycles per second)", 0.4, 0.05, 4)
  num("PulseCount", "Pulse Count (1-3)", 2, 1, 3, { INP_Integer = true, INP_MinAllowed = 1, INP_MaxAllowed = 3 })
  num("PulseSize", "Pulse Size (px @1920)", 12, 2, 80); color("PulC", "Pulse Color", 3, 1, 1, 1, 0.95)
  num("InDelay", "Draw Delay (s)", 0, 0, 10, { INP_MinAllowed = 0 }); num("InDur", "Draw Time (s)", 0.7, 0, 10, { INP_MinAllowed = 0 })
  check("HasOut", "Enable Out (un-draw)", 1)
  num("OutOffset", "Out Offset (s)", 0, 0, 10, { INP_MinAllowed = 0 }); num("OutDur", "Out Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  num("Index", "Index", 0, 0, 500, { INP_Integer = true, INP_MinAllowed = 0 }); num("Stagger", "Stagger (s)", 0, 0, 1, { INP_MinAllowed = 0 })
  num("ClipLen", "Clip Length (s, 0=auto)", 0, 0, 600, { INP_MinAllowed = 0 })
  combo("InEngine", "Draw Engine", 0, smk.ENGINES); combo("OutEngine", "Out Engine", 0, smk.ENGINES)
  num("Stiff", "Spring Stiffness", 180, 1, 1000); num("Damp", "Spring Damping", 18, 0, 100); num("Back", "Overshoot", 1.70158, 0, 5)
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end
local function col(req, k) return { g(req, k .. "R"), g(req, k .. "G"), g(req, k .. "B"), g(req, k .. "A") } end
local function pt(req, k, w, h) local q = I[k]:GetValue(req); return { q.X * w, q.Y * h } end
local function cfg(req, eng) return { engine = math.floor(g(req, eng) + 0.5) + 1, stiffness = g(req, "Stiff"), damping = g(req, "Damp"), mass = 1,
  amp = 1, period = 0.3, s = g(req, "Back"), k = 4, x1 = 0.25, y1 = 0.1, x2 = 0.25, y2 = 1 } end

-- arrow triangle (px) at an end: tip at the end point, pointing outward along dir
local function marker(kind, p, dir, size)
  if kind == 1 then return { kind = 1, cx = p[1], cy = p[2], r = size * 0.5, tri = { 0, 0, 0, 0, 0, 0 } } end
  if kind == 2 then
    local bx, by = p[1] - dir[1] * size, p[2] - dir[2] * size
    local nx, ny = -dir[2] * size * 0.5, dir[1] * size * 0.5
    return { kind = 2, cx = 0, cy = 0, r = 0, tri = { p[1], p[2], bx + nx, by + ny, bx - nx, by - ny } }
  end
  return { kind = 0, cx = 0, cy = 0, r = 0, tri = { 0, 0, 0, 0, 0, 0 } }
end

-- Pure CPU stage (unit-tested): geometry in output pixels + motion.
function SMK2_ConnPrep(req, w, h)
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate"); rate = (rate and rate > 0) and rate or 24
  local rs, re = self.Comp.RenderStart or 0, self.Comp.RenderEnd or 0
  local px = w / 1920
  local mid = {}
  for i = 1, math.floor(g(req, "N") + 0.5) do mid[i] = pt(req, "P" .. i, w, h) end
  local S = { mode = math.floor(g(req, "Mode") + 0.5) + 1, pa = pt(req, "AP", w, h), pb = pt(req, "BP", w, h), h1 = pt(req, "H1", w, h), h2 = pt(req, "H2", w, h),
    mid = mid, bend = g(req, "Bend"), tension = g(req, "Tension"), radius = g(req, "Radius") * px, gap = g(req, "Gap") * px,
    aBox = { hw = g(req, "AW") * w * 0.5, hh = g(req, "AH") * w * 0.5, mag = math.floor(g(req, "AMag") + 0.5) },
    bBox = { hw = g(req, "BW") * w * 0.5, hh = g(req, "BH") * w * 0.5, mag = math.floor(g(req, "BMag") + 0.5) } }
  if S.mode == 5 and #mid == 0 then S.mode = 1 end
  local path = smk.connPath(S)
  local T = g(req, "ClipLen"); if T <= 0 then T = (re - rs) / rate end
  local tm = { inDelay = g(req, "InDelay"), inDur = g(req, "InDur"), outOffset = g(req, "OutOffset"), outDur = g(req, "OutDur"),
    index = g(req, "Index"), stagger = g(req, "Stagger"), hasOut = g(req, "HasOut") > 0.5 }
  local t = smk.framesToSeconds(req.Time, rs, rate)
  local a, phase = smk.animAmount(t, T, tm, cfg(req, "InEngine"), cfg(req, "OutEngine"))
  local trim = 1 - math.max(0, math.min(1, a))
  local visA = (phase == "out") and math.max(0, math.min(1, trim / 0.08)) or 1   -- start mark leaves with the path so the last frame is empty
  local es = g(req, "EndSize") * px
  local colA = col(req, "LCA"); local colB = (g(req, "GradOn") > 0.5) and col(req, "LCB") or colA
  local flat, cum = {}, {}
  for i = 1, 192 do
    local q = path.pts[i] or path.pts[path.n]
    flat[2 * i - 1], flat[2 * i] = q[1], q[2]; cum[i] = path.cum[i] or path.total
  end
  local pul = {}
  local cnt = math.floor(g(req, "PulseCount") + 0.5)
  for j = 0, 2 do
    if g(req, "PulseOn") > 0.5 and j < cnt and path.total > 0 then
      local ph = (t * g(req, "PulseSpeed") + j / cnt) % 1
      local q = smk.connPointAt(path, ph * path.total * trim)
      local fade = math.sin(math.pi * ph) * math.max(0, math.min(1, (trim - 0.95) / 0.05))
      pul[#pul + 1] = q[1]; pul[#pul + 1] = q[2]; pul[#pul + 1] = g(req, "PulseSize") * px * 0.5; pul[#pul + 1] = fade
    else for _ = 1, 4 do pul[#pul + 1] = 0 end end
  end
  local mA = marker(math.floor(g(req, "AEnd") + 0.5), path.pa, path.startDir, es)
  local mB = marker(math.floor(g(req, "BEnd") + 0.5), path.pb, path.endDir, es)
  local function mk(m) local r = { m.cx, m.cy, m.r }; for i = 1, 6 do r[3 + i] = m.tri[i] end; return r end
  return { size = { w, h }, n = path.n, kindA = mA.kind, kindB = mB.kind, total = path.total, thick = g(req, "Thick") * px, trim = trim,
    dash = g(req, "Dash") * px, dgap = g(req, "DGap") * px, gradOn = g(req, "GradOn"), opacity = 1, visA = visA, pts = flat, cum = cum,
    mkA = mk(mA), mkB = mk(mB), pul = pul, pulCol = col(req, "PulC"), colA = colA, colB = colB }, path, a
end

function Process(req)
  local out = Image({ IMG_Width = Width, IMG_Height = Height, IMG_Depth = Depth, IMG_DeferAlloc = true })
  if req:IsPreCalc() then OutImage:Set(req, out) return end        -- P0: DVIPComputeNode is nil on PreCalc requests
  local P = SMK2_ConnPrep(req, out.Width, out.Height)
  local ok, perr = pcall(function()
    local node = DVIPComputeNode(req, "SMK2ConnKernel", SMK2ConnSource, "SMK2ConnParams", SMK2ConnParams)
    local b = node:GetParamBlock(SMK2ConnParams)
    for key, v in pairs(P) do b[key] = v end
    node:SetParamBlock(b)
    node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
    node:AddOutput("dst", out)
    if not node:RunSession(req) then error("RunSession failed") end
  end)
  if not ok then
    print("[SMK2_Connector] GPU failed: " .. tostring(perr))
    out = Image({ IMG_Width = Width, IMG_Height = Height, IMG_Depth = Depth }); out:Fill(Pixel({ R = 0, G = 0, B = 0, A = 0 }))
  end
  OutImage:Set(req, out)
end
