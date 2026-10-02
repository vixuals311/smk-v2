-- SMK2_MotionRig — modifier with several outputs. Attach ONE rig to an existing Merge (or Transform) and wire its
-- outputs to Blend / Size / Angle / Center. Zero extra nodes per element (Phase 1 G10: every extra node costs ms).
-- Same In/Hold/Out model as SMK2_Animator. Core is inlined at build time.
FuRegisterClass("SMK2_MotionRig", CT_Modifier, {
  REGS_Name = "SMK2 Motion Rig", REGS_Category = "Fuses\\SMK v2",
  REGS_OpDescription = "Seconds-based In/Hold/Out rig: Opacity, Scale, Angle, Offset and Center outputs for an existing Merge",
  REGID_DataType = "Number", REGID_InputDataType = "Number", REG_TimeVariant = true, REG_Version = 2,
})

I = {}
local function num(key, name, def, lo, hi, extra)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "SliderControl", INP_Default = def,
              INP_MinScale = lo, INP_MaxScale = hi }
  for k, v in pairs(extra or {}) do t[k] = v end
  I[key] = self:AddInput(name, key, t)
end
local function combo(key, name, def)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "ComboControl", INP_Default = def, INP_Integer = true }
  for _, n in ipairs(smk.ENGINES) do t[#t + 1] = { CCS_AddString = n } end
  I[key] = self:AddInput(name, key, t)
end
local function phaseControls(p)
  combo(p .. "Engine", p .. " Engine", p == "In" and 1 or 0)
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
  num("InDelay", "In Delay (s)", 0, 0, 10, { INP_MinAllowed = 0 })
  num("InDur", "In Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  I.HasOut = self:AddInput("Enable Out", "HasOut", { LINKID_DataType = "Number",
    INPID_InputControl = "CheckboxControl", INP_Default = 1 })
  num("OutOffset", "Out Offset (s)", 0, 0, 10, { INP_MinAllowed = 0 })
  num("OutDur", "Out Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  num("Index", "Index", 0, 0, 500, { INP_Integer = true, INP_MinAllowed = 0 })
  num("Stagger", "Stagger (s)", 0, 0, 1, { INP_MinAllowed = 0 })
  num("ClipLen", "Clip Length (s, 0=auto)", 0, 0, 600, { INP_MinAllowed = 0 })
  num("BaseX", "Base Center X", 0.5, -2, 3); num("BaseY", "Base Center Y", 0.5, -2, 3)
  phaseControls("In"); phaseControls("Out")
  OutOpacity = self:AddOutput("Opacity", "Opacity", { LINKID_DataType = "Number", LINK_Main = 1 })
  OutScale = self:AddOutput("Scale", "Scale", { LINKID_DataType = "Number" })
  OutAngle = self:AddOutput("Angle", "Angle", { LINKID_DataType = "Number" })
  OutX = self:AddOutput("Offset X", "OffsetX", { LINKID_DataType = "Number" })
  OutY = self:AddOutput("Offset Y", "OffsetY", { LINKID_DataType = "Number" })
  OutCenter = self:AddOutput("Center", "Center", { LINKID_DataType = "Point" })
end

local function g(req, k) return I[k]:GetValue(req).Value end

local function engineCfg(req, p)
  return { engine = math.floor(g(req, p .. "Engine") + 0.5) + 1, stiffness = g(req, p .. "Stiff"),
    damping = g(req, p .. "Damp"), mass = g(req, p .. "Mass"), amp = g(req, p .. "Amp"), period = g(req, p .. "Period"),
    s = g(req, p .. "Back"), k = g(req, p .. "Decay"), x1 = g(req, p .. "X1"), y1 = g(req, p .. "Y1"),
    x2 = g(req, p .. "X2"), y2 = g(req, p .. "Y2") }
end

function SMK2_Rig(req)
  local c = self.Comp                       -- P0: plain-field comp object
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate")
  rate = (rate and rate > 0) and rate or 24
  local w = self.Comp:GetPrefs("Comp.FrameFormat.Width") or 1920
  local h = self.Comp:GetPrefs("Comp.FrameFormat.Height") or 1080
  local rs, re = c.RenderStart or 0, c.RenderEnd or 0
  local T = g(req, "ClipLen")
  if T <= 0 then T = smk.clipSeconds(rs, re, rate) end
  local t = smk.framesToSeconds(req.Time, rs, rate)
  local tm = { inDelay = g(req, "InDelay"), inDur = g(req, "InDur"), outOffset = g(req, "OutOffset"),
    outDur = g(req, "OutDur"), index = g(req, "Index"), stagger = g(req, "Stagger"), hasOut = g(req, "HasOut") > 0.5 }
  local a, phase = smk.animAmount(t, T, tm, engineCfg(req, "In"), engineCfg(req, "Out"))
  local p = (phase == "out") and "Out" or "In"
  local r = smk.rigOut(a, { w = w, h = h, slideDist = g(req, p .. "SlideDist"), slideAngle = g(req, p .. "SlideAngle"),
    scaleFrom = g(req, p .. "Scale"), rotFrom = g(req, p .. "Rot"), fadeFrom = g(req, p .. "Fade") })
  r.cx, r.cy = g(req, "BaseX") + r.dx, g(req, "BaseY") + r.dy
  return r
end

function Process(req)
  local r = SMK2_Rig(req)
  OutOpacity:Set(req, Number(r.opacity)); OutScale:Set(req, Number(r.scale)); OutAngle:Set(req, Number(r.angle))
  OutX:Set(req, Number(r.dx)); OutY:Set(req, Number(r.dy)); OutCenter:Set(req, Point(r.cx, r.cy))
end
