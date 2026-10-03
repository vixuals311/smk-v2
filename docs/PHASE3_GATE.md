# Phase 3 Gate — Progress Ring / Bar (Shape track + counter)

New: `SMK2 Shape` gains **Track Color** (draws the part removed by Trim, so a ring/bar is one Fuse: coloured progress over a dim track).
New macros `SMK2_ProgressRing`, `SMK2_ProgressBar` (generated; `python scripts/install.py`, restart Resolve):
`UIP_Motion` (SMK2 Motion modifier, count-up 0 → Progress) → binds **Shape.Trim** directly (no `.Output` in expressions); label text is
`floor(Shape.Trim*100)%`; one `SMK2_Animator` moves ring + label together. The Animator mirrors the Motion timing/engine (short expressions,
Motion is upstream: no DAG cycle). Controls: pages Progress, Motion, In Motion, Out Motion.

**Test hygiene (from Phase 2d):** deselect everything (`FlowView.Select()`) before each paste so Fusion doesn't auto-add a Merge;
change the Background by 0.001 before each timed render so cached frames aren't reused; keep nodes at distinct positions.

| # | Check | Pass criteria / report |
|---|---|---|
| P1 | Paste `SMK2_ProgressRing` fresh; no red node / dialog | Loads; report exact error otherwise (generator bug → fix `build/make_macros.py`, describe change) |
| P2 | Defaults | Ring: blue sweep from 12 o'clock clockwise to 75 % over a dim white track; label counts 0 % → 75 % in step with the sweep (spring settles, may overshoot slightly); card slides/fades in; ring+label move together |
| P3 | Progress 0, 0.5, 1.0 and 1.0+ via control | Sweep length = value; label matches (rounded); at 1.0 no gap |
| P4 | Engines for In (Ease/Spring/Bounce/Elastic/Overshoot/Inertia) | Label and sweep move on the same curve; elastic/overshoot never show label < 0 % or > 100 % |
| P5 | `SMK2_ProgressBar` | Rounded bar (capsule) fills left→right over a dim track, label above, count-up in step |
| P6 | Track Color alpha 0 / 0.14 / 1; Progress Color; Thickness; Diameter/Length; Center | All work; colours show as grouped pickers |
| P7 | Timing: In Delay / Duration, Index + Stagger (6 rings staggered), Clip Length auto; trim the clip on the Edit page | Count-up and sweep start together; Out phase follows the clip end |
| P8 | Two instances (one copy-pasted) | Independent counts; no cross-talk |
| P9 | Save, close, full restart, reopen | Unchanged; no BezierSpline on published controls; renders pixel-identical |
| P10 | Benchmark: 5 and 8 rings, cold render ms/frame; viewer fps (user) | Report; compare with 5/8 UIBlocks (clean: 65.9 / 67.5 ms) |
| P11 | Inner graph readable (expanded group): Motion, Shape, Label, Merge, Animator left→right, distinct positions | Yes/no + screenshot |
| P12 | Does `UIP_Motion` output reach `Shape.Trim` and does Trim show as animated/linked in the Inspector? | Describe (a bound input is expected; no keyframes) |
