-- SMK2_Cursor — cursor + click generator. One Fuse: anti-aliased pointer (polygon SDF, no image file), waypoints with move / hold /
-- click, a gentle arc, press dip, up to 3 simultaneous click ripples, fade in/out. Seconds-based and clip-relative.
-- @include smk_cursor
FuRegisterClass("SMK2_Cursor", CT_SourceTool, {
  REGS_Name = "SMK2 Cursor", REGS_Category = "Fuses\\SMK v2", REGS_OpIconString = "SCu",
  REGS_OpDescription = "Cursor path with waypoints, press and click ripples",
  REG_Source_GlobalCtrls = true, REG_Source_SizeCtrls = true, REG_Source_AspectCtrls = true,
  REG_NoPreCalcProcess = true, REG_TimeVariant = true, REG_Version = 2,
})

SMK2CursorParams = [[
  int size[2];
  float tip[2];
  float S;
  float press;
  float bw;
  float shadowOff[2];
  float shadowBlur;
  float ripThick;
  float opacity;
  float rip[12];
  float fillCol[4];
  float borderCol[4];
  float shadowCol[4];
  float ripCol[4];
]]

-- GPU port of smk.cursorShade() (src/core/smk_cursor.lua). Keep in sync; tests compile this and compare pixels.
SMK2CursorSource = [[
__KERNEL__ void SMK2CursorKernel(__CONSTANTREF__ SMK2CursorParams *p, __TEXTURE2D_WRITE__ dst)
{
  DEFINE_KERNEL_ITERATORS_XY(x, y);
  if (x >= p->size[0] || y >= p->size[1]) return;
  float vx[7] = {0.0f, 0.0f, 0.19f, 0.33f, 0.45f, 0.31f, 0.58f};
  float vy[7] = {0.0f, -0.84f, -0.66f, -1.0f, -0.95f, -0.62f, -0.62f};
  float lx = ((float)x + 0.5f - p->tip[0]) / p->press;
  float ly = ((float)y + 0.5f - p->tip[1]) / p->press;
  float dd[2];                                   // [0] cursor distance, [1] shadow distance (px)
  for (int pass = 0; pass < 2; ++pass) {
    float qx = lx - (pass == 1 ? p->shadowOff[0] / p->press : 0.0f);
    float qy = ly - (pass == 1 ? p->shadowOff[1] / p->press : 0.0f);
    float d = (qx - vx[0] * p->S) * (qx - vx[0] * p->S) + (qy - vy[0] * p->S) * (qy - vy[0] * p->S);
    float s = 1.0f;
    int j = 6;
    for (int i = 0; i < 7; ++i) {
      float ex = (vx[j] - vx[i]) * p->S, ey = (vy[j] - vy[i]) * p->S;
      float wx = qx - vx[i] * p->S, wy = qy - vy[i] * p->S;
      float t = fminf(fmaxf((wx * ex + wy * ey) / (ex * ex + ey * ey), 0.0f), 1.0f);
      float bx = wx - ex * t, by = wy - ey * t;
      d = fminf(d, bx * bx + by * by);
      int c1 = (qy >= vy[i] * p->S), c2 = (qy < vy[j] * p->S), c3 = (ex * wy > ey * wx);
      if ((c1 && c2 && c3) || ((!c1) && (!c2) && (!c3))) s = -s;
      j = i;
    }
    dd[pass] = s * sqrtf(d) * p->press;
  }
  float d = dd[0];
  float fa = p->fillCol[3] * fminf(fmaxf(0.5f - d, 0.0f), 1.0f);
  float ba = 0.0f;
  if (p->bw > 0.0f) ba = p->borderCol[3] * fmaxf(fminf(fmaxf(0.5f - d, 0.0f), 1.0f) - fminf(fmaxf(0.5f - (d + p->bw), 0.0f), 1.0f), 0.0f);
  float sa = 0.0f;
  if (p->shadowCol[3] > 0.0f) {
    float blur = fmaxf(p->shadowBlur, 0.5f);
    float t = fminf(fmaxf((dd[1] + blur) / (2.0f * blur), 0.0f), 1.0f);
    sa = p->shadowCol[3] * (1.0f - t * t * (3.0f - 2.0f * t));
  }
  float rr = 0.0f, rg = 0.0f, rb = 0.0f, ra = 0.0f;       // ripples, bottom-up in array order
  for (int i = 0; i < 3; ++i) {
    float ca = p->rip[i * 4 + 3];
    if (ca > 0.0f) {
      float ddx = (float)x + 0.5f - p->rip[i * 4], ddy = (float)y + 0.5f - p->rip[i * 4 + 1];
      float rd = fabsf(sqrtf(ddx * ddx + ddy * ddy) - p->rip[i * 4 + 2]) - p->ripThick * 0.5f;
      float ta = p->ripCol[3] * fminf(fmaxf(0.5f - rd, 0.0f), 1.0f) * ca;
      float k = 1.0f - ta;
      rr = p->ripCol[0] * ta + rr * k; rg = p->ripCol[1] * ta + rg * k; rb = p->ripCol[2] * ta + rb * k; ra = ta + ra * k;
    }
  }
  float shr = p->shadowCol[0] * sa + rr * (1.0f - sa), shg = p->shadowCol[1] * sa + rg * (1.0f - sa);
  float shb = p->shadowCol[2] * sa + rb * (1.0f - sa), sha = sa + ra * (1.0f - sa);
  float k1 = 1.0f - fa;
  float orr = p->fillCol[0] * fa + shr * k1, og = p->fillCol[1] * fa + shg * k1, ob = p->fillCol[2] * fa + shb * k1, oa = fa + sha * k1;
  float k2 = 1.0f - ba;
  float O = p->opacity;
  float4 c = make_float4((p->borderCol[0] * ba + orr * k2) * O, (p->borderCol[1] * ba + og * k2) * O,
                         (p->borderCol[2] * ba + ob * k2) * O, (ba + oa * k2) * O);
  _tex2DVec4Write(dst, x, y, c);
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

local DEF = { { 0.25, 0.65, 0, 0.3, 0 }, { 0.7, 0.4, 1.2, 0.5, 1 }, { 0.45, 0.25, 0.9, 0.4, 1 } }   -- x, y, move, hold, click

function Create()
  num("N", "Waypoints (2-8)", 3, 2, 8, { INP_Integer = true, INP_MinAllowed = 2, INP_MaxAllowed = 8 })
  combo("Ease", "Move Style", 0, { "Smooth", "Snappy", "Spring" })
  num("Arc", "Path Arc", 0.12, -0.5, 0.5)
  num("StartDelay", "Start Delay (s)", 0.4, 0, 10, { INP_MinAllowed = 0 })
  num("FadeIn", "Fade In (s)", 0.25, 0, 3, { INP_MinAllowed = 0 }); num("FadeOut", "Fade Out (s)", 0.3, 0, 3, { INP_MinAllowed = 0 })
  num("ClipLen", "Clip Length (s, 0=auto)", 0, 0, 600, { INP_MinAllowed = 0 })
  num("Size", "Cursor Size (frac of frame width)", 0.03, 0.005, 0.2)
  color("FillC", "Cursor Color", 1, 1, 1, 1, 1); color("BorderC", "Outline Color", 2, 0.05, 0.05, 0.08, 1)
  num("BW", "Outline Width (px @1920)", 2, 0, 20)
  color("ShadowC", "Shadow Color", 3, 0, 0, 0, 0.35)
  num("SX", "Shadow X (px @1920)", 2, -50, 50); num("SY", "Shadow Y, down (px @1920)", 4, -50, 50); num("SB", "Shadow Blur (px @1920)", 6, 0, 50)
  num("ClickDelay", "Click Delay After Arrival (s)", 0.12, 0, 2, { INP_MinAllowed = 0 })
  num("PressDur", "Press Duration (s)", 0.18, 0.02, 1); num("PressAmt", "Press Depth", 0.14, 0, 0.5)
  color("RippleC", "Ripple Color", 4, 0.25, 0.55, 1, 0.9)
  num("RippleR", "Ripple Radius (frac of frame width)", 0.04, 0.005, 0.3)
  num("RippleW", "Ripple Thickness (px @1920)", 5, 0.5, 40)
  num("RippleDur", "Ripple Duration (s)", 0.6, 0.05, 3)
  for i = 1, 8 do
    local d = DEF[i] or DEF[3]
    I["P" .. i] = self:AddInput("Waypoint " .. i, "P" .. i, { LINKID_DataType = "Point", INPID_InputControl = "OffsetControl",
      INPID_PreviewControl = "CrosshairControl", INP_DefaultX = d[1], INP_DefaultY = d[2] })
    if i > 1 then num("M" .. i, "  Move to " .. i .. " (s)", d[3] > 0 and d[3] or 1, 0, 10, { INP_MinAllowed = 0 }) end
    num("H" .. i, "  Hold at " .. i .. " (s)", d[4] or 0.3, 0, 10, { INP_MinAllowed = 0 })
    I["K" .. i] = self:AddInput("  Click at " .. i, "K" .. i, { LINKID_DataType = "Number", INPID_InputControl = "CheckboxControl", INP_Default = d[5] or 0 })
  end
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
end

local function g(req, k) return I[k]:GetValue(req).Value end
local function col(req, k) return { g(req, k .. "R"), g(req, k .. "G"), g(req, k .. "B"), g(req, k .. "A") } end

-- Pure CPU stage (unit-tested): all geometry in output pixels.
function SMK2_CursorPrep(req, w, h)
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate"); rate = (rate and rate > 0) and rate or 24
  local rs, re = self.Comp.RenderStart or 0, self.Comp.RenderEnd or 0
  local n = math.max(2, math.min(8, math.floor(g(req, "N") + 0.5)))
  local wp = {}
  for i = 1, n do
    local pt = I["P" .. i]:GetValue(req)
    wp[i] = { x = pt.X, y = pt.Y, move = (i > 1) and g(req, "M" .. i) or 0, hold = g(req, "H" .. i), click = g(req, "K" .. i) > 0.5 }
  end
  local T = g(req, "ClipLen"); if T <= 0 then T = (re - rs) / rate end
  local o = { n = n, startDelay = g(req, "StartDelay"), arc = g(req, "Arc"), ease = math.floor(g(req, "Ease") + 0.5) + 1,
    clickDelay = g(req, "ClickDelay"), pressDur = g(req, "PressDur"), pressAmt = g(req, "PressAmt"), rippleDur = g(req, "RippleDur"),
    fadeIn = g(req, "FadeIn"), fadeOut = g(req, "FadeOut"), T = T, aspect = w / h }
  local st = smk.cursorState(smk.framesToSeconds(req.Time, rs, rate), wp, o)
  local px, rr = w / 1920, g(req, "RippleR") * w
  local rip = {}
  for i = 1, 3 do
    local r = st.ripples[i]
    if r then rip[#rip + 1] = r.x * w; rip[#rip + 1] = r.y * h; rip[#rip + 1] = r.r * rr; rip[#rip + 1] = r.a
    else for _ = 1, 4 do rip[#rip + 1] = 0 end end
  end
  return { size = { w, h }, tip = { st.x * w, st.y * h }, S = g(req, "Size") * w, press = math.max(st.press, 0.05), bw = g(req, "BW") * px,
    shadowOff = { g(req, "SX") * px, -g(req, "SY") * px }, shadowBlur = g(req, "SB") * px, ripThick = g(req, "RippleW") * px,
    opacity = st.opacity, rip = rip, fillCol = col(req, "FillC"), borderCol = col(req, "BorderC"), shadowCol = col(req, "ShadowC"),
    ripCol = col(req, "RippleC") }, st
end

function Process(req)
  local out = Image({ IMG_Width = Width, IMG_Height = Height, IMG_Depth = Depth, IMG_DeferAlloc = true })
  if req:IsPreCalc() then OutImage:Set(req, out) return end        -- P0: DVIPComputeNode is nil on PreCalc requests
  local P = SMK2_CursorPrep(req, out.Width, out.Height)
  local ok, perr = pcall(function()
    local node = DVIPComputeNode(req, "SMK2CursorKernel", SMK2CursorSource, "SMK2CursorParams", SMK2CursorParams)
    local b = node:GetParamBlock(SMK2CursorParams)
    for key, v in pairs(P) do b[key] = v end
    node:SetParamBlock(b)
    node:AddSampler("RowSampler", TEX_FILTER_MODE_LINEAR, TEX_ADDRESS_MODE_CLAMP, TEX_NORMALIZED_COORDS_TRUE)
    node:AddOutput("dst", out)
    if not node:RunSession(req) then error("RunSession failed") end
  end)
  if not ok then
    print("[SMK2_Cursor] GPU failed: " .. tostring(perr))
    out = Image({ IMG_Width = Width, IMG_Height = Height, IMG_Depth = Depth }); out:Fill(Pixel({ R = 0, G = 0, B = 0, A = 0 }))
  end
  OutImage:Set(req, out)
end
