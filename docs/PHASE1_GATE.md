# Phase 1 Gate — Motion core (run in Resolve)

Gate from the Master Plan: **20 animated cards at 60 fps in 1080p, same timing at 24/30/60 fps.**
Install with `python scripts/install.py` (Fuses go to `Fuses/SMK2/`), restart Resolve.

| # | Check | Pass criteria |
|---|---|---|
| G1 | `SMK2 Animator` on a Text+/Background, defaults | Slides in from the left with fade over 0.5 s (spring), holds, slides out right over the last 0.5 s. No console errors |
| G2 | Change In engine across all 6 (Ease, Spring, Bounce, Elastic, Overshoot, Inertia) | Each looks distinct; Spring may overshoot and settle past In Duration; no jump at the end |
| G3 | Fade / Slide angle+distance / Scale / Rotation at offset, each alone | Matches the setting; rotation is not sheared on 16:9 and 9:16; slide distance is a fraction of frame width |
| G4 | Pivot X/Y at 0,0 and 1,1 with Scale 0 and Rotation 90 | Scale and rotation happen around the pivot |
| G5 | Trim the clip on the Edit page | Out phase moves with the new clip end (no re-open) |
| G6 | Index 0..5 with Stagger 0.1 | Each card starts 0.1 s later; changing Stagger updates live (no script) |
| G7 | Same comp at 24, 30, 60 fps | Identical seconds-timing; same frames-per-second look |
| G8 | Save, close, reopen | Unchanged; no BezierSpline on any SMK2 input |
| G9 | Two Animators in one comp; rename one | Both work independently (multi-instance safety) |
| G10 | **Benchmark:** 20 Animators (Index 0..19, Stagger 0.05) each on a Background/Text+ merged over a 1080p background | Measure playback fps (target 60) and per-frame render ms; compare with 20 v1 UIBlocks if available |
| G11 | Transparent edges | Premultiplied alpha correct: no dark/light fringes on a text with soft edges at partial opacity |

Known limits (by design, from Phase 0): output is full-frame (DoD shrink unsupported, S4); no in-kernel motion blur — use a native
Transform with Motion Blur for fast moves (S6); `SMK2 Motion` last frame lands within ~0.4% of To.
