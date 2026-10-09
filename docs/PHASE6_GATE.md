# Phase 6 Gate — SMK2 Callout (and the Shape line additions)

`python scripts/install.py`, restart Resolve, paste macros fresh. Scripting only. Hygiene: deselect before paste, comp rate = timeline rate, cold renders
(Background +0.001), readable graphs (distinct node positions, clear names, notes, one comp per check), `SaveProject()`, project `SMK Phase6 Gate`.

**New in `SMK2 Shape` (Fuse):** *Line Uses End Points* (two Point controls with viewer crosshairs: Line From / Line To; length, angle and centre computed in
pixels, so it is isotropic), *Draw On With Motion* (Trim follows the In/Out amount: draws on during In, un-draws during Out), *Line End Dot Radius* (a dot at
the drawing front). Reference pixel function + GPU kernel verified (41,472 px, max diff 3.0e-6); 47 unit tests.

**New macro `SMK2_Callout`:** card (`UIC_Card` Shape) + label (`UIC_Label` Text+) merged and moved together by one `UIC_Animator`; a leader line
(`UIC_Leader` Shape, From → To, draw-on, end dot) that starts drawing at 60 % of the card's In and un-draws with the card's Out; final Merge.
Pages: Callout (text, card size/position/colour/border/shadow), Leader (start, target, thickness, dot, colour, draw time), Motion, In Motion, Out Motion.
2 Fuses + Text+ + 2 Merges. The leader reads the Animator's inputs (no cycle).

| # | Check | Pass criteria / report |
|---|---|---|
| L1 | Paste `SMK2_Callout` fresh | No red node / dialog; report any error. If the Point inputs or expressions fail, fix `build/make_macros.py` and describe the change |
| L2 | Defaults over time | Card + "Callout" text slide/fade in; the leader draws from the card edge toward the target (≈ 0.82, 0.28) with a dot at the front, then holds; at the end the line un-draws and the card leaves. Report frames: card In start/finish, line draw start/finish, Out start/finish |
| L3 | Hot spots: line start at **Line Start**, dot centre at **Target Point** when fully drawn | Within ±1 px on 1080p, 1080×1920, 4K (measure the dot centroid and the line's first pixel) |
| L4 | Move Target and Line Start (SetInput on the Points), incl. downward, leftward, vertical and near-zero lengths | Line follows; angle correct (CCW positive, y up); no artefacts when length ≈ 0 |
| L5 | Line Thickness 1–12 px, dot radius 0 / 4 / 10, colour with alpha | As set; dot not clipped by the draw-on mask at partial trim; no dark fringe |
| L6 | Draw timing: Line Draw Time 0.2–1.0 s; card In Delay / Duration changes | Draw starts at In Delay + 0.6·In Duration and lasts Line Draw Time (report measured vs expected frames) |
| L7 | Stagger: 4 callouts, Index 0–3, Stagger 0.15 | Cards and leaders stagger together (leader mirrors Index/Stagger) |
| L8 | Out: Enable Out off/on, Out Offset, Out Duration | The leader un-draws with the same Out timing; the last frame is empty with Out on |
| L9 | Engines for the card (six) and the leader keeps its ease | No glitch; the dot follows the line front |
| L10 | 24/30/60 fps (rate = timeline rate); trimmed 46-frame clip | Pixel-identical at equal seconds; Out follows the clip end |
| L11 | Two instances (copy-paste + renamed) | Independent: the copy's expressions point at its own `UIC_Animator_1` etc. |
| L12 | Save, full restart, reopen | Unchanged; no BezierSpline; pixel-identical |
| L13 | Cost: 1, 3 and 6 callouts, cold 60 fps, 300 frames; user: viewer fps | Report ms/frame |
| L14 | Expanded group: readable graph (distinct positions); Inspector pages listed above, Point controls show crosshairs | Describe; crosshair dragging is for the user |
| L15 | Shape regression: standalone Line with Line Uses End Points off (old behaviour), Ring/Bar progress macros, UIBlock | Same as before (no visual change); report any difference |

**For you by hand:** dragging the Line Start / Target crosshairs in the viewer; whether the leader draw-on and end dot look right; viewer fps.
