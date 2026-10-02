-- SMK2_Motion — Number modifier. One engine dropdown, seconds-based, clip-relative, In/Hold/Out.
-- Only the active phase's engine is evaluated. Core is inlined at build time (see build/build.py).
FuRegisterClass("SMK2_Motion", CT_Modifier, {
  REGS_Name = "SMK2 Motion", REGS_Category = "Fuses\\SMK v2",
  REGS_OpDescription = "Seconds-based In/Hold/Out motion modifier (Ease, Spring, Bounce, Elastic, Overshoot, Inertia)",
  REGID_DataType = "Number", REGID_InputDataType = "Number", REG_TimeVariant = true, REG_Version = 2,
})

local function num(id, name, def, lo, hi, extra)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "SliderControl", INP_Default = def,
              INP_MinScale = lo, INP_MaxScale = hi }
  for k, v in pairs(extra or {}) do t[k] = v end
  return self:AddInput(name, id, t)
end
local function engineCombo(name, id, def)
  local t = { LINKID_DataType = "Number", INPID_InputControl = "ComboControl", INP_Default = def, INP_Integer = true }
  for i, n in ipairs(smk.ENGINES) do t[#t + 1] = { CCS_AddString = n } end
  return self:AddInput(name, id, t)
end

function Create()
  I = {}
  I.From = num("From", "From", 0, -10, 10)
  I.Rest = num("Rest", "Rest", 1, -10, 10)
  I.To = num("To", "To", 0, -10, 10)
  I.InDelay = num("InDelay", "In Delay (s)", 0, 0, 10, { INP_MinAllowed = 0 })
  I.InDur = num("InDur", "In Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  I.HasOut = self:AddInput("Enable Out", "HasOut", { LINKID_DataType = "Number",
    INPID_InputControl = "CheckboxControl", INP_Default = 1 })
  I.OutOffset = num("OutOffset", "Out Offset (s)", 0, 0, 10, { INP_MinAllowed = 0 })
  I.OutDur = num("OutDur", "Out Duration (s)", 0.5, 0, 10, { INP_MinAllowed = 0 })
  I.Index = num("Index", "Index", 0, 0, 200, { INP_Integer = true, INP_MinAllowed = 0 })
  I.Stagger = num("Stagger", "Stagger (s)", 0, 0, 1, { INP_MinAllowed = 0 })
  I.EngIn = engineCombo("In Engine", "EngineIn", 1)
  I.EngOut = engineCombo("Out Engine", "EngineOut", 0)
  I.Stiff = num("Stiffness", "Spring Stiffness", 180, 1, 1000)
  I.Damp = num("Damping", "Spring Damping", 18, 0, 100)
  I.Mass = num("Mass", "Spring Mass", 1, 0.1, 10)
  I.Amp = num("ElasticAmp", "Elastic Amplitude", 1, 1, 4)
  I.Period = num("ElasticPeriod", "Elastic Period", 0.3, 0.05, 1)
  I.Back = num("Overshoot", "Overshoot", 1.70158, 0, 5)
  I.Decay = num("InertiaK", "Inertia Decay", 4, 0.5, 12)
  I.X1 = num("X1", "Bezier x1", 0.25, 0, 1); I.Y1 = num("Y1", "Bezier y1", 0.1, -1, 2)
  I.X2 = num("X2", "Bezier x2", 0.25, 0, 1); I.Y2 = num("Y2", "Bezier y2", 1, -1, 2)
  I.ClipLen = num("ClipLength", "Clip Length (s, 0=auto)", 0, 0, 600, { INP_MinAllowed = 0 })
  Out = self:AddOutput("Output", "Output", { LINKID_DataType = "Number", LINK_Main = 1 })
  Phase = self:AddOutput("Phase", "Phase", { LINKID_DataType = "Number" })
end

local function g(req, k) return I[k]:GetValue(req).Value end

function Process(req)
  local c = self.Comp   -- FIX(P0): self.Comp is an ffi FusionDoc*; read RenderStart/RenderEnd as fields (no :GetAttrs())
  local rate = self.Comp:GetPrefs("Comp.FrameFormat.Rate")
  rate = (rate and rate > 0) and rate or 24
  local rs, re = c.RenderStart or 0, c.RenderEnd or 0
  local T = g(req, "ClipLen")
  if T <= 0 then T = smk.clipSeconds(rs, re, rate) end
  local t = smk.framesToSeconds(req.Time, rs, rate)
  local function cfg(e)
    return { engine = e + 1, stiffness = g(req, "Stiff"), damping = g(req, "Damp"), mass = g(req, "Mass"),
      amp = g(req, "Amp"), period = g(req, "Period"), s = g(req, "Back"), k = g(req, "Decay"),
      x1 = g(req, "X1"), y1 = g(req, "Y1"), x2 = g(req, "X2"), y2 = g(req, "Y2") }
  end
  local tm = { inDelay = g(req, "InDelay"), inDur = g(req, "InDur"), outOffset = g(req, "OutOffset"),
    outDur = g(req, "OutDur"), index = g(req, "Index"), stagger = g(req, "Stagger"), hasOut = g(req, "HasOut") > 0.5 }
  local v, ph = smk.value(t, T, g(req, "From"), g(req, "Rest"), g(req, "To"), tm,
    cfg(math.floor(g(req, "EngIn") + 0.5)), cfg(math.floor(g(req, "EngOut") + 0.5)))
  Out:Set(req, Number(v))
  Phase:Set(req, Number(({ pre = 0, ["in"] = 1, hold = 2, out = 3 })[ph] or 0))
end
