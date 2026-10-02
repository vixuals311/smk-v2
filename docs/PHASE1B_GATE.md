# Phase 1b Gate — zero-extra-node motion (SMK2 Motion Rig)

**Why:** Phase 1 G10 showed per-node cost dominates: 20 Animators 67 ms/frame, 20 native Transforms 27.5 ms, baseline (20 Text+ + Merges,
no animation node) 7.5 ms. A 60 fps budget is 16.6 ms, so *any* extra node per card misses it. New design: one `SMK2 Motion Rig`
modifier per card drives the Merge the card already has (Blend, Size, Angle, Center). The Animator Fuse stays as the simple
single-element tool; the rig is the path for stacks of cards.

Install: `python scripts/install.py`, restart Resolve.

| # | Check | Pass criteria |
|---|---|---|
| R1 | Right-click Merge.Blend → Modify With → `SMK2 Motion Rig` (Opacity output). Then connect Merge.Size ← Rig Scale, Merge.Angle ← Rig Angle | Defaults slide/fade like the Animator. Report how each output can be wired in the GUI/scripting (what worked) |
| R2 | Merge.Center ← Rig **Center** (Point output). If a Point output cannot connect, instead set Merge.Center to the expression `Point(<rig>.Center.X, <rig>.Center.Y)` or `Point(0.5 + RigOffsetX...)`; report which works | Slide moves the card; vertical slide is aspect-correct |
| R3 | One Rig shared by Opacity/Scale/Angle/Center on the same Merge (single modifier, 4 connections) — save, reopen | Intact, no BezierSpline, identical render |
| R4 | Stagger: 20 cards, each with its own Rig, Index 0..19, Stagger 0.05 | Staggered, live-editable |
| R5 | Pixel parity: card animated by Rig-on-Merge vs the same card through `SMK2 Animator` at frames 0, 3, 6, 12 | Positions within 1–2 px, opacity within 1/255; note any difference in scale/rotation pivot behaviour |
| R6 | **Benchmark (same graph as G10):** 20 Text+ cards merged over a 1080p Background, 60 fps timeline, 300 frames to PNG: (a) no animation, (b) 20 Rigs on the Merges, (c) 20 Animators, (d) 20 native Transforms by expression | Report ms/frame and fps for each. **Target: (b) ≤ 16.6 ms/frame**; note if Merge Size≠1/Angle≠0 raises the Merge cost vs (a) |
| R7 | Modifier evaluation cost | Report ms/frame of 20 Rigs where only Blend is wired vs all four outputs wired |

If Merge cost with Size/Angle animated is itself the bottleneck, say so and report (b) with only Blend + Center wired.
