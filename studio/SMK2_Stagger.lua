--[[ SMK2_Stagger — Fusion script (Resolve Studio: Workspace > Scripts > Comp, or Fusion Studio). Numbers the selected SMK elements 0,1,2,... in the order you choose,
so "Index x Stagger" delays them one after another. Works on anything that has an input named "Index" (SMK Fuses and macros); other tools are skipped and reported.
The ordering and numbering logic is pure Lua and unit-tested (tests/test_stagger.py); the dialog / selection code at the bottom runs only inside Fusion and is UNVERIFIED until a Studio run.
Install: copy this file to  .../Fusion/Scripts/Comp/  (Resolve Studio: Support/Fusion/Scripts/Comp). --]]

SMK2Stagger = {}

-- tools: array of {name=, x=, y=, sel=selection order}. mode: "x" (left to right), "y" (top to bottom), "sel" (selection order). Returns a NEW sorted array (stable).
function SMK2Stagger.order(tools, mode)
  local arr = {}
  for i, t in ipairs(tools) do arr[i] = { t = t, i = i } end
  local function key(e)
    if mode == "y" then return e.t.y or 0 end
    if mode == "sel" then return e.t.sel or e.i end
    return e.t.x or 0
  end
  table.sort(arr, function(a, b)
    local ka, kb = key(a), key(b)
    if ka ~= kb then return ka < kb end
    if mode == "x" and (a.t.y or 0) ~= (b.t.y or 0) then return (a.t.y or 0) < (b.t.y or 0) end    -- same column: top first (y grows down in the flow)
    return a.i < b.i
  end)
  local out = {}
  for i, e in ipairs(arr) do out[i] = e.t end
  return out
end

-- Assign Index = start + n*step to every tool that has an "Index" input. `has(tool)` and `set(tool, value)` abstract Fusion. Returns assigned, skipped (names).
function SMK2Stagger.apply(sorted, start, step, has, set)
  local assigned, skipped, n = {}, {}, 0
  for _, t in ipairs(sorted) do
    if has(t) then set(t, start + n * step); n = n + 1; assigned[#assigned + 1] = t.name
    else skipped[#skipped + 1] = t.name end
  end
  return assigned, skipped
end

-- ---- Fusion shell (not executed in the unit tests: `comp` is nil there) ----
if comp ~= nil then
  local sel = comp:GetToolList(true)
  if #sel == 0 then print("[SMK2 Stagger] select the SMK tools first"); return end
  local flow = comp.CurrentFrame.FlowView
  local tools, byName = {}, {}
  for i, t in ipairs(sel) do
    local pos = flow:GetPosTable(t) or { 0, 0 }
    local e = { name = t.Name, x = pos[1], y = pos[2], sel = i }
    tools[#tools + 1] = e; byName[t.Name] = t
  end
  local ans = comp:AskUser("SMK2 Stagger", {
    { "Start", "Screw", Default = 0, Min = -1000, Max = 1000, Integer = true },
    { "Step", "Screw", Default = 1, Min = -1000, Max = 1000, Integer = true },
    { "Order", "Dropdown", Default = 0, Options = { "Left to right", "Top to bottom", "Selection order" } },
  })
  if not ans then return end
  local mode = ({ [0] = "x", [1] = "y", [2] = "sel" })[ans.Order or 0]
  comp:StartUndo("SMK2 Stagger")
  local done, skipped = SMK2Stagger.apply(SMK2Stagger.order(tools, mode), ans.Start or 0, ans.Step or 1,
    function(e) return byName[e.name]:GetInput("Index") ~= nil end,
    function(e, v) byName[e.name]:SetInput("Index", v) end)
  comp:EndUndo(true)
  print(string.format("[SMK2 Stagger] numbered %d tool(s)%s", #done, #skipped > 0 and (", skipped (no Index input): " .. table.concat(skipped, ", ")) or ""))
end
