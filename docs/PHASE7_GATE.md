# Phase 7 Gate — SMK2 Connector and SMK2 Look (run by Agent A, the only agent that drives Resolve)

`python scripts/install.py`, restart Resolve. **Scripting only (no UI automation).** Hygiene: deselect (`FlowView.Select()`) before each paste, comp rate = timeline rate,
cold renders (Background +0.001), readable graphs (distinct node positions, clear names, one comp per check named after the check, a Note per group), `ProjectManager.SaveProject()`,
projects `SMK Phase7 Connector` and `SMK Phase7 Look`. Write `docs/PHASE7_RESULTS.md` (table: check, comp, result, evidence), push `phase7-results`, paste the table. NOT VERIFIED where not observed.
If a generator/Fuse bug is found you may fix `build/make_macros.py` or the Fuse source in `src/fuses/` and `src/core/`; re-run `python build/build.py` and the tests, and describe the change.

## A. SMK2 Connector (Fuse: Effects ▸ Fuses ▸ SMK v2 ▸ SMK2 Connector)
One Fuse: path styles **Curve, Straight, Elbow (rounded), Bezier (2 draggable handles), Spline (through up to 6 draggable points)**; **magnetic ends**
(Start/End Magnet: Off, Auto = exits the box edge toward the target, or a fixed side Top/Right/Bottom/Left, with a gap); dash/gap, thickness, colour + optional gradient,
dot/arrow end-marks, travelling pulses, draw-on / un-draw motion with Index × Stagger. Reference pixel function and GPU kernel verified on 73,728 px (max diff 1.6e-4); 32 + 24 unit tests.
Point controls use `OffsetControl` with a crosshair preview (viewer widgets). Boxes (width/height as a fraction of frame width) are centred on the Start/End Points.

| # | Check | Pass criteria / report |
|---|---|---|
| K1 | Add to a comp; defaults | Loads, transparent output, no error; curve from (0.25, 0.5) to (0.75, 0.5) with a dot at the start and an arrow at the end, drawing on then un-drawing |
| K2 | All five Path Styles | Each renders; the first/last path pixel is within ±1.5 px of Start/End Point (or the magnet exit point); end-mark centres at the end points |
| K3 | **Bezier handles:** set Handle 1 / Handle 2 to several positions (script `SetInput` on the Points) | Curve bends toward the handles; the initial direction (first 30 px) points toward Handle 1 and the final direction comes from Handle 2 (report angles); Start/End unchanged |
| K4 | **Spline points:** N = 0…6; move each point | Passes through every point (±1.5 px); moving point k changes the path locally (report how far the change reaches); Tension 0 = polyline corners at the points, 1 = smooth; N=0 falls back to Curve |
| K5 | **Magnets:** Start/End Magnet Off / Auto / Top / Right / Bottom / Left with box sizes 0.2×0.1 and 0.05×0.05; Gap 0 / 6 / 20 | Exit points on the box edges (±1 px) at the side mid-points, offset outward by Gap; **Auto** with the target at 8 compass positions exits the correct edge (right/left/top/bottom, diagonals by ray hit); the curve leaves the edge perpendicular to it |
| K6 | **Following moving elements:** link Start and End Point by expression to two `SMK2_UIBlock` instances' Center X/Y (e.g. `Point(UIBlock1.Card_CX..., ...)` — find the working syntax) and move the cards (set inputs at different frames / keyframe the cards' CX, CY) | The connector follows live with magnets keeping the ends on the card edges. Report the exact working expression syntax; if the published macro inputs cannot be referenced, say what can |
| K7 | Draw timing: Draw Delay / Time, engines, Out (un-draw), Out Offset, Index 0–5 Stagger 0.15 | Draw-on start/finish frames match seconds; stagger live; last frame empty with Out on; trimmed 46-frame clip follows the clip end |
| K8 | Style: thickness 1–20 px, dash 0 / 20 / 40, gap, gradient, alpha colours, over a UI Block | Dash pattern continuous around curves (no restart per segment); no dark fringe; gradient runs start → end |
| K9 | End-marks None / Dot / Arrow on both ends, sizes 8–60 px on straight, curved and elbow paths | Arrow tip exactly on the end point and aligned with the final tangent (report angle error); end dot only when fully drawn; start mark immediate |
| K10 | Pulses 1–3, speed, size, colour | Pulses stay on the path (distance to path ≤ 1.5 px); only after the line is drawn; fade at the ends |
| K11 | 1080p, 1080×1920, 4K | Same composition (frame fractions); thickness/dash/marks scale with width; **check facets:** long curves at 4K look smooth (path is ≤ 96 sampled points — report the maximum deviation or any visible polygon facets) |
| K12 | 24/30/60 fps; two instances; save, full restart, reopen | Pixel-identical at equal seconds; independent; no BezierSpline on any input; pixel-identical after restart |
| K13 | Cost: 1, 5, 10 connectors, cold 60 fps, 300 frames | ms/frame each; user adds viewer fps |
| K14 | Inspector input list | Report that Point inputs are `OffsetControl` with crosshair; group heading names; any control with a confusing label |

## B. SMK2 Look (Fuse: image in → image out)
One GPU pass, bounded sample counts: **Glow** (from Alpha or Brightness with threshold; radius px@1920; intensity; colour; additive or behind-object; quality Draft 24 / Normal 48 / High 96 / Max 160 samples),
**Outline** (width px@1920, colour), **Shine** (angle, half-width, softness, intensity, colour; manual position or auto sweep with delay/duration/repeat in seconds), **Gradient overlay** (two colours, angle, amount), Opacity.
Reference pixel function and GPU kernel verified on 55,296 px (0 differing by > 3e-3 with nearest-texel sampling); 27 unit tests. (On the GPU the sampler is bilinear, so edges are slightly smoother than the test oracle.)

| # | Check | Pass criteria / report |
|---|---|---|
| M1 | Look on a `SMK2 Shape` card, on a Text+ title, on an `SMK2_TextLetter` macro, on a UI Block | Loads, no error; with every effect off the output equals the input |
| M2 | **Glow:** radius 10 / 40 / 120 px, intensity 0.5 / 1.2 / 3, colours, Alpha vs Brightness source, additive vs behind | Soft symmetric halo; scales with resolution (px@1920); additive brightens the object, behind does not touch it; Brightness mode glows only bright parts |
| M3 | **Glow quality** Draft / Normal / High / Max at radius 40 and 120 | Report visible noise / banding / star-pattern artifacts at each; ms/frame each; recommend defaults. Compare Draft vs Max visually (difference image mean) |
| M4 | **Outline** 2 / 6 / 20 px, colours, on text and on hollow shapes | Even width on all sides; corners acceptable (report roundness); inner edge untouched |
| M5 | **Shine** manual (position −1…1, angle 0 / 25 / 90) and auto sweep (delay, duration, repeat 0 / 2 s) | Band only where the object has alpha; moves left → right along the axis; off-screen before/after; repeats; timing in seconds at 24/60 fps |
| M6 | **Gradient overlay** angle 0 / 45 / 90, amount 0 / 0.5 / 1, alpha colours | Alpha unchanged; transparent areas untouched; direction correct |
| M7 | **Premultiplied correctness** over a bright and a dark background with soft/semi-transparent edges | No dark or light fringe at any effect combination; glow additive composited correctly |
| M8 | **DoD clipping (important):** Look on a Text+ with a small DoD and a large glow radius / outline near the text box edge | Is the glow/outline cut off at the input's DoD or the input image bounds? Report. If clipped, implement a fix in `src/fuses/SMK2_Look.lua`: output `Image({IMG_Like = img, IMG_DataWindow = <input DataWindow padded by glow radius + outline + shine>})` (only `IMG_DataWindow` works for placing, Phase 0/2b), re-test and describe |
| M9 | 1080p, 1080×1920, 4K; 24/30/60 fps | Same look at equal seconds; px@1920 scaling correct |
| M10 | Cost: Look with glow Normal/High/Max on 1080p and 4K, and 5 Looks on 5 elements; cold 60 fps | ms/frame; user adds viewer fps |
| M11 | Two instances; save, full restart, reopen | Independent; unchanged; no BezierSpline; pixel-identical |
| M12 | Chain: Shape → Look → Merge over a background; `UIBlock → Look` | Works; the Look can replace v1-style multi-node glows; report node count vs a native glow stack |

**For the user by hand:** dragging the Connector crosshairs and Bezier handles in the viewer; whether glow / shine / connector motion looks good; viewer fps.
