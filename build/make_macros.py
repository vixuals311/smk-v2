#!/usr/bin/env python3
"""Generate Fusion macro .setting files (GroupOperator) from small graph descriptions.
Products are presets over core nodes: no logic here beyond wiring + publishing controls.
Usage: python build/make_macros.py  -> dist/templates/*.setting"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist", "templates")

class Raw(str):
    """A Lua fragment emitted verbatim (e.g. StyledText { ... })."""

def lua(v):
    if isinstance(v, Raw): return str(v)
    if isinstance(v, bool): return "1" if v else "0"
    if isinstance(v, (int, float)): return repr(float(v)) if isinstance(v, float) else str(v)
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'

class Node:
    def __init__(self, name, typ, pos, values=None, expr=None, links=None, user=None):
        self.name, self.typ, self.pos = name, typ, pos
        self.values, self.expr, self.links = values or {}, expr or {}, links or {}
        self.user = user or []          # [(id, kind, default, lo, hi, page, items)]
    def render(self, ind):
        t = "\t" * ind
        out = [f"{t}{self.name} = {self.typ} {{"]
        if self.user:
            out.append(f"{t}\tUserControls = ordered() {{")
            for uid, kind, default, lo, hi, page, items in self.user:
                out.append(f"{t}\t\t{uid} = {{")
                if kind == "combo":
                    out += [f"{t}\t\t\tINP_Integer = true,", f"{t}\t\t\tLBLC_DropDownButton = true,", f'{t}\t\t\tINPID_InputControl = "ComboControl",', f"{t}\t\t\tCC_Custom = true,"]
                elif kind == "text":
                    out += ['\t\t\tLINKID_DataType = "Text",'.replace("\t\t\t", f"{t}\t\t\t"), f'{t}\t\t\tINPID_InputControl = "TextEditControl",', f"{t}\t\t\tTEC_Lines = 3,",
                            f'{t}\t\t\tINP_Default = {lua(default)},', f'{t}\t\t\tICS_ControlPage = "{page}",', f"{t}\t\t}},"]
                    continue
                elif kind == "check":
                    out += [f"{t}\t\t\tINP_Integer = true,", f'{t}\t\t\tINPID_InputControl = "CheckboxControl",']
                else:
                    out += [f'{t}\t\t\tINPID_InputControl = "SliderControl",', f"{t}\t\t\tINP_MinScale = {float(lo)},", f"{t}\t\t\tINP_MaxScale = {float(hi)},"]
                out += [f'{t}\t\t\tLINKID_DataType = "Number",', f"{t}\t\t\tINP_Default = {float(default)},", f'{t}\t\t\tICS_ControlPage = "{page}",']
                if uid in ("Scale", "InDur", "OutDur"): out.append(f"{t}\t\t\tINP_MinAllowed = {0.01 if uid == 'Scale' else 0.0},")
                out += [f'{t}\t\t\t{{ CCS_AddString = "{i}", }},' for i in (items or [])]
                out.append(f"{t}\t\t}},")
            out.append(f"{t}\t}},")
        out.append(f"{t}\tInputs = {{")
        for uid, kind, default, *_ in self.user:
            out.append(f"{t}\t\t{uid} = Input {{ Value = {lua(default) if kind == 'text' else float(default)}, }},")
        for k, v in self.values.items(): out.append(f"{t}\t\t{k} = Input {{ Value = {lua(v)}, }},")
        for k, e in self.expr.items(): out.append(f"{t}\t\t{k} = Input {{ Expression = {lua(e)}, }},")
        for k, (op, src) in self.links.items(): out.append(f'{t}\t\t{k} = Input {{ SourceOp = "{op}", Source = "{src}", }},')
        out += [f"{t}\t}},", f"{t}\tViewInfo = OperatorInfo {{ Pos = {{ {self.pos[0]}, {self.pos[1]} }} }},", f"{t}}},"]
        return "\n".join(out)

class Macro:
    def __init__(self, name, nodes, out_op):
        self.name, self.nodes, self.out_op, self.pub = name, nodes, out_op, []
    def publish(self, op, src, name, page, default=None, key=None, group=None):
        self.pub.append(dict(op=op, src=src, name=name, page=page, default=default, group=group,
                             key=key or f"{re.sub(r'^UI[BP]_', '', op)}_{src}"))
    def publish_color(self, op, base, label, page, group, alpha=True):
        """One colour picker: channels share a ControlGroup; only the first carries the Name (v1 pattern)."""
        for i, ch in enumerate(("R", "G", "B", "A") if alpha else ("R", "G", "B")):
            self.publish(op, base + ch, label if i == 0 else "", page, group=group)
    def render(self):
        o = ["{", "\tTools = ordered() {", f"\t\t{self.name} = GroupOperator {{", "\t\t\tCtrlWZoom = false,", "\t\t\tInputs = ordered() {"]
        for p in self.pub:
            o += [f"\t\t\t\t{p['key']} = InstanceInput {{", f'\t\t\t\t\tSourceOp = "{p["op"]}",', f'\t\t\t\t\tSource = "{p["src"]}",',
                  f'\t\t\t\t\tPage = {lua(p["page"])},']
            if p["name"]: o.insert(len(o) - 1, f'\t\t\t\t\tName = {lua(p["name"])},')
            if p["group"]: o.append(f"\t\t\t\t\tControlGroup = {p['group']},")
            if p["default"] is not None: o.append(f"\t\t\t\t\tDefault = {lua(p['default'])},")
            o.append("\t\t\t\t},")
        o += ["\t\t\t},", "\t\t\tOutputs = {", "\t\t\t\tMainOutput1 = InstanceOutput {", f'\t\t\t\t\tSourceOp = "{self.out_op}",', '\t\t\t\t\tSource = "Output",', "\t\t\t\t}", "\t\t\t},",
              "\t\t\tViewInfo = GroupInfo { Pos = { 0, 0 } },", "\t\t\tTools = ordered() {"]
        o += [n.render(4) for n in self.nodes]
        o += ["\t\t\t},", "\t\t},", "\t},", "\tActiveTool = \"%s\"" % self.name, "}"]
        return "\n".join(o) + "\n"

# ---- shared lists (keys must exist on the Fuses; tests verify against the real Create()) ----
ENGINE_KEYS = [("Engine", "Engine"), ("Fade", "Opacity At Offset"), ("SlideDist", "Slide Distance"), ("SlideAngle", "Slide Angle"),
               ("Scale", "Scale At Offset"), ("Rot", "Rotation At Offset (deg)"), ("Stiff", "Spring Stiffness"), ("Damp", "Spring Damping"),
               ("Mass", "Spring Mass"), ("X1", "Bezier x1"), ("Y1", "Bezier y1"), ("X2", "Bezier x2"), ("Y2", "Bezier y2"),
               ("Amp", "Elastic Amplitude"), ("Period", "Elastic Period"), ("Back", "Overshoot"), ("Decay", "Inertia Decay")]
TIMING = [("InDelay", "In Delay (s)"), ("InDur", "In Duration (s)"), ("HasOut", "Enable Out"), ("OutOffset", "Out Offset (s)"),
          ("OutDur", "Out Duration (s)"), ("Index", "Index"), ("Stagger", "Stagger (s)"), ("ClipLen", "Clip Length (s, 0=auto)")]
COLOR = lambda k: [(k + c, c2) for c, c2 in zip("RGBA", ("Red", "Green", "Blue", "Alpha"))]

def ui_block():
    shape_static = {f"{p}{k}": v for p in ("In", "Out") for k, v in (("Fade", 1.0), ("SlideDist", 0.0), ("Scale", 1.0), ("Rot", 0.0))}
    nodes = [
        Node("UIB_Shape", "Fuse.SMK2_Shape", (0, 0), values=dict(shape_static, UseFrameFormatSettings=1, Width=1920, Height=1080, FillAR=0.16, FillAG=0.2, FillAB=0.36, FillAA=1.0, BW=2, BCR=1, BCG=1, BCB=1, BCA=0.35)),
        Node("UIB_Label", "TextPlus", (0, 66), values=dict(UseFrameFormatSettings=1, Width=1920, Height=1080, Wrap=0, StyledText="Card", Font="Open Sans",
             Style="Bold", Size=0.04, HorizontalJustificationNew=1, VerticalJustificationNew=3, HorizontalLeftCenterRight=0,
             Red1=1.0, Green1=1.0, Blue1=1.0, Alpha1=1.0), expr={"Center": "Point(UIB_Shape.CX, UIB_Shape.CY)", "AngleZ": "UIB_Shape.Angle"}),
        Node("UIB_Merge", "Merge", (110, 33), links={"Background": ("UIB_Shape", "Output"), "Foreground": ("UIB_Label", "Output")}),
        Node("UIB_Animator", "Fuse.SMK2_Animator", (220, 33), links={"Image": ("UIB_Merge", "Output")},
             expr={"PivotX": "UIB_Shape.CX", "PivotY": "UIB_Shape.CY"}),
    ]
    m = Macro("SMK2_UIBlock", nodes, "UIB_Animator")
    for k, n in (("StyledText", "Text"), ("Font", "Font"), ("Size", "Text Size")): m.publish("UIB_Label", k, n, "Card", key=f"Label_{k}")
    for i, (k, ch) in enumerate((("Red1", "R"), ("Green1", "G"), ("Blue1", "B"))):
        m.publish("UIB_Label", k, "Text Color" if i == 0 else "", "Card", group=1)
    for k, n in (("Shape", "Shape"), ("W", "Width (frac of frame width)"), ("H", "Height (frac of frame width)"), ("Radius", "Corner Radius"),
                 ("CX", "Center X"), ("CY", "Center Y"), ("Angle", "Angle"), ("FillMode", "Fill")): m.publish("UIB_Shape", k, n, "Card")
    m.publish_color("UIB_Shape", "FillA", "Fill Color", "Card", 2); m.publish_color("UIB_Shape", "FillB", "Fill Color B", "Card", 3)
    for k, n in (("GradAngle", "Gradient Angle"), ("BW", "Border Width (px @1920)"), ("BPos", "Border Position")): m.publish("UIB_Shape", k, n, "Card")
    m.publish_color("UIB_Shape", "BC", "Border Color", "Card", 4)
    m.publish_color("UIB_Shape", "SC", "Shadow Color", "Card", 5)
    for k, n in (("SX", "Shadow X"), ("SY", "Shadow Y (down)"), ("SB", "Shadow Blur")): m.publish("UIB_Shape", k, n, "Card")
    for k, n in TIMING: m.publish("UIB_Animator", k, n, "Motion")
    for ph in ("In", "Out"):
        for k, n in ENGINE_KEYS: m.publish("UIB_Animator", ph + k, f"{ph} {n}", f"{ph} Motion")
    return m

# Counter engine: the Motion modifier is UPSTREAM of everything (Shape.Trim is bound to its output), so it owns the
# In timing/engine controls and the Animator (downstream) mirrors them with short expressions. Never the other way
# round: upstream-reading-downstream is the v1 "DAG recursion" trap.
MIRROR = {"InDelay": "InDelay", "InDur": "InDur", "InEngine": "EngineIn", "InStiff": "Stiffness", "InDamp": "Damping",
          "InMass": "Mass", "InAmp": "ElasticAmp", "InPeriod": "ElasticPeriod", "InBack": "Overshoot", "InDecay": "InertiaK",
          "InX1": "X1", "InY1": "Y1", "InX2": "X2", "InY2": "Y2", "Index": "Index", "Stagger": "Stagger", "ClipLen": "ClipLength"}
MOTION_PUB = [("InDelay", "In Delay (s)"), ("InDur", "In Duration (s)"), ("Index", "Index"), ("Stagger", "Stagger (s)"),
              ("ClipLength", "Clip Length (s, 0=auto)"), ("EngineIn", "In Engine"), ("Stiffness", "In Spring Stiffness"),
              ("Damping", "In Spring Damping"), ("Mass", "In Spring Mass"), ("X1", "In Bezier x1"), ("Y1", "In Bezier y1"),
              ("X2", "In Bezier x2"), ("Y2", "In Bezier y2"), ("ElasticAmp", "In Elastic Amplitude"),
              ("ElasticPeriod", "In Elastic Period"), ("Overshoot", "In Overshoot"), ("InertiaK", "In Inertia Decay")]

def progress(kind):
    ring = kind == "ring"
    static = {f"{p}{k}": v for p in ("In", "Out") for k, v in (("Fade", 1.0), ("SlideDist", 0.0), ("Scale", 1.0), ("Rot", 0.0))}
    shape_vals = dict(static, UseFrameFormatSettings=1, Width=1920, Height=1080, Shape=2 if ring else 3, W=0.16 if ring else 0.4,
                      Thick=26 if ring else 18, FillAR=0.3, FillAG=0.55, FillAB=1.0, FillAA=1.0, TCR=1.0, TCG=1.0, TCB=1.0, TCA=0.14,
                      SCA=0.0, BW=0)
    nodes = [
        Node("UIP_Motion", "Fuse.SMK2_Motion", (0, 0), values=dict(From=0.0, Rest=0.75, To=0.75, HasOut=0)),
        Node("UIP_Shape", "Fuse.SMK2_Shape", (110, 0), values=shape_vals, links={"Trim": ("UIP_Motion", "Output")}),
        Node("UIP_Label", "TextPlus", (110, 66), values=dict(UseFrameFormatSettings=1, Width=1920, Height=1080, Wrap=0, StyledText="75%",
             Font="Open Sans", Style="Bold", Size=0.06 if ring else 0.04, HorizontalJustificationNew=1, VerticalJustificationNew=3,
             HorizontalLeftCenterRight=0, Red1=1.0, Green1=1.0, Blue1=1.0, Alpha1=1.0),
             expr={"Center": "Point(UIP_Shape.CX, UIP_Shape.CY)" if ring else "Point(UIP_Shape.CX, UIP_Shape.CY + 0.07)",
                   "StyledText": 'math.max(0, math.min(100, math.floor(UIP_Shape.Trim * 100 + 0.5))) .. "%"'}),
        Node("UIP_Merge", "Merge", (220, 33), links={"Background": ("UIP_Shape", "Output"), "Foreground": ("UIP_Label", "Output")}),
        Node("UIP_Animator", "Fuse.SMK2_Animator", (330, 33), links={"Image": ("UIP_Merge", "Output")},
             expr=dict({"PivotX": "UIP_Shape.CX", "PivotY": "UIP_Shape.CY"}, **{k: f"UIP_Motion.{v}" for k, v in MIRROR.items()})),
    ]
    m = Macro("SMK2_Progress" + ("Ring" if ring else "Bar"), nodes, "UIP_Animator")
    m.publish("UIP_Motion", "Rest", "Progress (0-1)", "Progress", key="Progress")
    for k, n in (("Font", "Font"), ("Size", "Label Size")): m.publish("UIP_Label", k, n, "Progress")
    for i, (k, ch) in enumerate((("Red1", "R"), ("Green1", "G"), ("Blue1", "B"))): m.publish("UIP_Label", k, "Label Color" if i == 0 else "", "Progress", group=1)
    for k, n in (("W", "Diameter" if ring else "Length"), ("Thick", "Thickness (px @1920)"), ("CX", "Center X"), ("CY", "Center Y"), ("Angle", "Angle")):
        m.publish("UIP_Shape", k, n, "Progress")
    m.publish_color("UIP_Shape", "FillA", "Progress Color", "Progress", 2); m.publish_color("UIP_Shape", "TC", "Track Color", "Progress", 3)
    for k, n in MOTION_PUB: m.publish("UIP_Motion", k, n, "Motion")
    for k, n in (("HasOut", "Enable Out"), ("OutOffset", "Out Offset (s)"), ("OutDur", "Out Duration (s)")): m.publish("UIP_Animator", k, n, "Motion")
    for k, n in (("Fade", "Opacity At Offset"), ("SlideDist", "Slide Distance"), ("SlideAngle", "Slide Angle"), ("Scale", "Scale At Offset"), ("Rot", "Rotation At Offset (deg)")):
        m.publish("UIP_Animator", "In" + k, "In " + n, "In Motion")
    for k, n in ENGINE_KEYS: m.publish("UIP_Animator", "Out" + k, f"Out {n}", "Out Motion")
    return m

# ---------------------------------------------------------------------------------------------------
# SMK Text: Text+ -> StyledTextFollower; every animated follower input is bound to a built-in Calculation
# (or Vector) modifier whose expression reads `time`. Phase 0/S9: an expression typed directly on a follower
# input is ignored; inside Calculation it sees each letter's own delayed time, and costs ~19 ms/frame for 12
# letters vs 107 ms for Fuse modifiers. Everything is in seconds, clip-relative (comp.RenderStart/RenderEnd).
# ---------------------------------------------------------------------------------------------------
UNIT_DEF = {  # Lua prelude: L = 0-based index of the LAST CHARACTER (opacity is per character, so Out must finish for it), d = follower delay per character (s)
    "letter": 'local s=U.Text.Value local L=#s-1 local d=U.Stagger ',
    "word": 'local s=U.Text.Value local L=#s-1 local d=U.Stagger*select(2,s:gsub("%S+",""))/math.max(1,#s) ',
    "line": 'local s=U.Text.Value local L=#s-1 local d=U.Stagger*math.max(1,select(2,s:gsub("[^\\n]+","")))/math.max(1,#s) ',
}
DELAY_EXPR = {  # follower Delay (frames) = d * frame rate; same d as in the amount expression
    "letter": 'UIT_Ctrl.Stagger * comp:GetPrefs("Comp.FrameFormat.Rate")',
    "word": 'UIT_Ctrl.Stagger * comp:GetPrefs("Comp.FrameFormat.Rate") * select(2, UIT_Ctrl.Text.Value:gsub("%S+", "")) / math.max(1, #UIT_Ctrl.Text.Value)',
    "line": 'UIT_Ctrl.Stagger * comp:GetPrefs("Comp.FrameFormat.Rate") * math.max(1, select(2, UIT_Ctrl.Text.Value:gsub("[^\\n]+", ""))) / math.max(1, #UIT_Ctrl.Text.Value)',
}

def text_amount_lua(unit="letter"):
    """Lua body computing `a` (0 = settled, 1 = fully offset) for the current (letter-shifted) time. Closed-form engines."""
    U = "UIT_Ctrl."
    return (
        UNIT_DEF[unit] +
        'local r=comp:GetPrefs("Comp.FrameFormat.Rate") local t=(time-comp.RenderStart)/r '
        'local T=(comp.RenderEnd-comp.RenderStart)/r local ti=t-U.InDelay local a=1 '
        'if ti>=0 then local p=math.min(1,ti/math.max(U.InDur,0.001)) local g=U.Engine local e=p '
        'if g<0.5 then e=1-(1-p)^3 '
        'elseif g<1.5 then local k=math.max(U.Stiff,1) local w=math.sqrt(k) local z=math.min(0.999,math.max(0.05,U.Damp/(2*w))) '
        'local wd=w*math.sqrt(1-z*z) e=1-math.exp(-z*w*ti)*(math.cos(wd*ti)+z*w/wd*math.sin(wd*ti)) '
        'elseif g<2.5 then local q=p if q<0.3636 then e=7.5625*q*q elseif q<0.7273 then q=q-0.5454 e=7.5625*q*q+0.75 '
        'elseif q<0.9091 then q=q-0.8182 e=7.5625*q*q+0.9375 else q=q-0.9545 e=7.5625*q*q+0.984375 end '
        'elseif g<3.5 then if p>0 and p<1 then e=2^(-10*p)*math.sin((p-0.075)*20.944)+1 end '
        'elseif g<4.5 then local q=p-1 e=1+(U.Over+1)*q*q*q+U.Over*q*q '
        'else e=(1-math.exp(-4*p))/(1-math.exp(-4)) end a=1-e end '
        'if U.HasOut>0.5 then local po=math.min(1,math.max(0,(t-(T-U.OutOffset-U.OutDur-L*d))/math.max(U.OutDur,0.001))) '
        'a=math.min(1,a+po*po*(3-2*po)) end '
    ).replace("U.", U)

def text_expr(final, unit="letter"):
    body = text_amount_lua(unit)
    return f"(function() {body}return {final} end)()"

TEXT_USER = [  # (id, kind, default, lo, hi, page, items)
    ("Text", "text", "SMK Text", 0, 0, "Text", None),
    ("InDelay", "slider", 0.0, 0, 5, "Motion", None), ("InDur", "slider", 0.5, 0, 5, "Motion", None),
    ("Stagger", "slider", 0.04, 0, 0.5, "Motion", None),
    ("Engine", "combo", 1, 0, 0, "Motion", ["Ease", "Spring", "Bounce", "Elastic", "Overshoot", "Inertia"]),
    ("Stiff", "slider", 180, 1, 1000, "Motion", None), ("Damp", "slider", 18, 0, 100, "Motion", None),
    ("Over", "slider", 1.70158, 0, 5, "Motion", None),
    ("Fade", "slider", 0.0, 0, 1, "Look", None), ("SlideDist", "slider", 0.03, -0.5, 0.5, "Look", None),
    ("SlideAngle", "slider", -90.0, -360, 360, "Look", None), ("Scale", "slider", 1.0, 0, 3, "Look", None),
    ("Rot", "slider", 0.0, -360, 360, "Look", None), ("Blur", "slider", 0.0, 0, 20, "Look", None),
    ("HasOut", "check", 1, 0, 1, "Out", None), ("OutOffset", "slider", 0.0, 0, 5, "Out", None),
    ("OutDur", "slider", 0.5, 0, 5, "Out", None),
]
TEXT_LABELS = {"InDelay": "In Delay (s)", "InDur": "In Duration (s)", "Stagger": "Stagger (s per letter / word / line)", "Engine": "Engine",
               "Stiff": "Spring Stiffness", "Damp": "Spring Damping", "Over": "Overshoot", "Fade": "Opacity At Start",
               "SlideDist": "Slide Distance (frac of width)", "SlideAngle": "Slide Angle (direction of start offset)",
               "Scale": "Scale At Start", "Rot": "Rotation At Start (deg)", "Blur": "Blur At Start", "HasOut": "Enable Out",
               "OutOffset": "Out Offset (s)", "OutDur": "Out Duration (s)", "Text": "Text"}

def text_macro(unit):
    P = {"letter": "Character", "word": "Word", "line": "Line"}[unit]
    d = {"letter": 0.04, "word": 0.1, "line": 0.2}[unit]
    user = [(u[0], u[1], d if u[0] == "Stagger" else u[2], *u[3:]) for u in TEXT_USER]
    N = lambda name, typ, pos, **k: Node(name, typ, pos, **k)
    N = lambda name, typ, pos, **k: Node(name, typ, pos, **k)
    mul = lambda name, pos, src, second_expr: N(name, "Calculation", pos, values={"Operator": 2}, expr={"SecondOperand": second_expr}, links={"FirstOperand": (src, "Result")})
    nodes = [
        Node("UIT_Ctrl", "Background", (0, 132), user=user, values=dict(TopLeftAlpha=0.0)),
        Node("UIT_Text", "TextPlus", (0, 0), values=dict(UseFrameFormatSettings=1, Width=1920, Height=1080, Wrap=1,
             LayoutRotation=1, TransformRotation=1, Font="Open Sans", Style="Bold", Size=0.08, VerticalJustificationNew=3,
             HorizontalJustificationNew=3, Red1=1.0, Green1=1.0, Blue1=1.0, Alpha1=1.0),
             links={"StyledText": ("UIT_Follower", "StyledText")}),
        Node("UIT_Follower", "StyledTextFollower", (110, 0), values=dict(Order=0, TransformRotation=1, TransformSize=1),
             expr={"Delay": DELAY_EXPR[unit], "Text": "UIT_Ctrl.Text"},
             links={P + "Offset": ("UIT_Vector", "Position"), P + "AngleZ": ("UIT_AngleZ", "Result"), P + "SizeX": ("UIT_Scale", "Result"),
                    P + "SizeY": ("UIT_Scale", "Result"), "Opacity1": ("UIT_Opacity", "Result"),
                    "SoftnessX1": ("UIT_Blur", "Result"), "SoftnessY1": ("UIT_Blur", "Result")}),
        Node("UIT_Vector", "Vector", (220, 0), values=dict(Origin=Raw("{ 0, 0 }"), ImageAspect=1),
             expr={"Angle": "UIT_Ctrl.SlideAngle"}, links={"Distance": ("UIT_Dist", "Result")}),
        # ONE long expression (the amount a: 0 settled .. 1 fully offset); everything else is a tiny linked Calculation,
        # so Fusion parses the long text once per letter instead of five times (S10: 57 -> 28 ms for 12 letters).
        N("UIT_Amt", "Calculation", (330, 0), expr={"FirstOperand": text_expr("a", unit)}),
        mul("UIT_Dist", (440, 0), "UIT_Amt", "UIT_Ctrl.SlideDist"),
        mul("UIT_PreOp", (440, 66), "UIT_Amt", "(1-UIT_Ctrl.Fade)"),
        N("UIT_Opacity", "Calculation", (550, 66), values={"Operator": 5, "SecondOperand": 1}, links={"FirstOperand": ("UIT_PreOp", "Result")}),   # Second - First = 1 - a*(1-Fade)
        mul("UIT_PreScale", (440, 132), "UIT_Amt", "(UIT_Ctrl.Scale-1)"),
        N("UIT_Scale", "Calculation", (550, 132), values={"SecondOperand": 1}, links={"FirstOperand": ("UIT_PreScale", "Result")}),                # 1 + a*(Scale-1); feeds Size X and Y
        mul("UIT_AngleZ", (440, 198), "UIT_Amt", "UIT_Ctrl.Rot"),
        mul("UIT_Blur", (440, 264), "UIT_Amt", "UIT_Ctrl.Blur"),                                                                                   # feeds Softness X and Y
    ]
    m = Macro("SMK2_Text" + unit.capitalize(), nodes, "UIT_Text")
    m.publish("UIT_Ctrl", "Text", "Text", "Text")
    m.publish("UIT_Text", "Font", "Font", "Text"); m.publish("UIT_Text", "Size", "Size", "Text")
    for i, k in enumerate(("Red1", "Green1", "Blue1")): m.publish("UIT_Text", k, "Text Color" if i == 0 else "", "Text", group=1)
    m.publish("UIT_Text", "Center", "Position", "Text")
    m.publish("UIT_Follower", "Order", "Order", "Motion", key="Follower_Order")
    for uid, *_ in [u for u in TEXT_USER if u[0] != "Text"]: m.publish("UIT_Ctrl", uid, TEXT_LABELS[uid], next(u[5] for u in TEXT_USER if u[0] == uid))
    return m

MACROS = {"SMK2_TextLetter": lambda: text_macro("letter"), "SMK2_TextWord": lambda: text_macro("word"), "SMK2_TextLine": lambda: text_macro("line"),
          "SMK2_UIBlock": ui_block, "SMK2_ProgressRing": lambda: progress("ring"), "SMK2_ProgressBar": lambda: progress("bar")}

if __name__ == "__main__":
    os.makedirs(DIST, exist_ok=True)
    for name, fn in MACROS.items():
        open(os.path.join(DIST, name + ".setting"), "w", newline="\n").write(fn().render()); print("wrote", name + ".setting")
