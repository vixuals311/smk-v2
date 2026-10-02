#!/usr/bin/env python3
"""Generate Fusion macro .setting files (GroupOperator) from small graph descriptions.
Products are presets over core nodes: no logic here beyond wiring + publishing controls.
Usage: python build/make_macros.py  -> dist/templates/*.setting"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist", "templates")

def lua(v):
    if isinstance(v, bool): return "1" if v else "0"
    if isinstance(v, (int, float)): return repr(float(v)) if isinstance(v, float) else str(v)
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'

class Node:
    def __init__(self, name, typ, pos, values=None, expr=None, links=None):
        self.name, self.typ, self.pos = name, typ, pos
        self.values, self.expr, self.links = values or {}, expr or {}, links or {}
    def render(self, ind):
        t = "\t" * ind
        out = [f"{t}{self.name} = {self.typ} {{", f"{t}\tInputs = {{"]
        for k, v in self.values.items(): out.append(f"{t}\t\t{k} = Input {{ Value = {lua(v)}, }},")
        for k, e in self.expr.items(): out.append(f"{t}\t\t{k} = Input {{ Expression = {lua(e)}, }},")
        for k, (op, src) in self.links.items(): out.append(f'{t}\t\t{k} = Input {{ SourceOp = "{op}", Source = "{src}", }},')
        out += [f"{t}\t}},", f"{t}\tViewInfo = OperatorInfo {{ Pos = {{ {self.pos[0]}, {self.pos[1]} }} }},", f"{t}}},"]
        return "\n".join(out)

class Macro:
    def __init__(self, name, nodes, out_op):
        self.name, self.nodes, self.out_op, self.pub = name, nodes, out_op, []
    def publish(self, op, src, name, page, default=None, key=None):
        self.pub.append(dict(op=op, src=src, name=name, page=page, default=default, key=key or f"{op}_{src}"))
    def render(self):
        o = ["{", "\tTools = ordered() {", f"\t\t{self.name} = GroupOperator {{", "\t\t\tCtrlWZoom = false,", "\t\t\tInputs = ordered() {"]
        for p in self.pub:
            o += [f"\t\t\t\t{p['key']} = InstanceInput {{", f'\t\t\t\t\tSourceOp = "{p["op"]}",', f'\t\t\t\t\tSource = "{p["src"]}",',
                  f'\t\t\t\t\tName = {lua(p["name"])},', f'\t\t\t\t\tPage = {lua(p["page"])},']
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
        Node("Shape", "Fuse.SMK2_Shape", (0, 0), values=dict(shape_static, FillAR=0.16, FillAG=0.2, FillAB=0.36, FillAA=1.0, BW=2, BCR=1, BCG=1, BCB=1, BCA=0.35)),
        Node("Label", "TextPlus", (0, 66), values=dict(UseFrameFormatSettings=1, Width=1920, Height=1080, Wrap=0, StyledText="Card", Font="Open Sans",
             Style="Bold", Size=0.04, HorizontalJustificationNew=1, VerticalJustificationNew=3, HorizontalLeftCenterRight=0,
             Red1=1.0, Green1=1.0, Blue1=1.0, Alpha1=1.0), expr={"Center": "Point(Shape.CX, Shape.CY)"}),
        Node("Merge", "Merge", (110, 33), links={"Background": ("Shape", "Output"), "Foreground": ("Label", "Output")}),
        Node("Animator", "Fuse.SMK2_Animator", (220, 33), links={"Image": ("Merge", "Output")},
             expr={"PivotX": "Shape.CX", "PivotY": "Shape.CY"}),
    ]
    m = Macro("SMK2_UIBlock", nodes, "Animator")
    for k, n in (("StyledText", "Text"), ("Font", "Font"), ("Style", "Font Style"), ("Size", "Text Size")): m.publish("Label", k, n, "Card", key=f"Label_{k}")
    for k, n in (("Red1", "Text Red"), ("Green1", "Text Green"), ("Blue1", "Text Blue")): m.publish("Label", k, n, "Card")
    for k, n in (("Shape", "Shape"), ("W", "Width (frac of frame width)"), ("H", "Height (frac of frame width)"), ("Radius", "Corner Radius"),
                 ("CX", "Center X"), ("CY", "Center Y"), ("Angle", "Angle"), ("FillMode", "Fill")): m.publish("Shape", k, n, "Card")
    for k, n in COLOR("FillA") + COLOR("FillB"): m.publish("Shape", k, ("Fill " if "A" == k[4] else "Fill B ") + n, "Card")
    for k, n in (("GradAngle", "Gradient Angle"), ("BW", "Border Width (px @1920)"), ("BPos", "Border Position")): m.publish("Shape", k, n, "Card")
    for k, n in COLOR("BC"): m.publish("Shape", k, "Border " + n, "Card")
    for k, n in COLOR("SC"): m.publish("Shape", k, "Shadow " + n, "Card")
    for k, n in (("SX", "Shadow X"), ("SY", "Shadow Y (down)"), ("SB", "Shadow Blur")): m.publish("Shape", k, n, "Card")
    for k, n in TIMING: m.publish("Animator", k, n, "Motion")
    for ph in ("In", "Out"):
        for k, n in ENGINE_KEYS: m.publish("Animator", ph + k, f"{ph} {n}", f"{ph} Motion")
    return m

MACROS = {"SMK2_UIBlock": ui_block}

if __name__ == "__main__":
    os.makedirs(DIST, exist_ok=True)
    for name, fn in MACROS.items():
        open(os.path.join(DIST, name + ".setting"), "w", newline="\n").write(fn().render()); print("wrote", name + ".setting")
