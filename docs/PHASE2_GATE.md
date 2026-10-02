# Phase 2 Gate — SMK2 Shape (first slice)

Install: `python scripts/install.py`, restart Resolve. Fuse: **SMK2 Shape** (Fuses ▸ SMK v2). It is a generator (no input) with
the same In/Hold/Out motion as the Animator built in, so a card is **one Fuse node + the Merge**.

The GPU kernel was compiled on CPU in CI-style tests and matches the reference pixel function (41k pixels, max diff 5e-6), so
Resolve checks focus on API behaviour, looks and speed.

| # | Check | Pass criteria |
|---|---|---|
| H1 | Add it. Defaults: white rounded pill, soft shadow, slides in from left with fade (spring), out on the last 0.5 s | No console errors; transparent background (alpha) |
| H2 | Every Shape: Rectangle (radius 0 / 0.15 / 0.5=pill), Ellipse, Ring, Line | Edges anti-aliased at 100% zoom and when zoomed 800% |
| H3 | Resolution: 1920×1080, 1080×1920, 3840×2160 | Same composition (sizes are fractions of width), border/shadow px scale with width |
| H4 | Fill: Solid, Linear (angles 0/90/45), Radial; colours with alpha < 1 | Gradient direction correct; alpha colour gives a translucent fill with no dark fringe over a light background |
| H5 | Border 0/4/12 px at Inside / Center / Outside; border colour with alpha | Band on the expected side; no gap or double edge where it meets the fill |
| H6 | Shadow X/Y/Blur; shadow colour alpha 0 | Soft falloff, follows rotation/scale; alpha 0 = no shadow |
| H7 | Ring Trim 0→1 animated by keyframe (and by an `SMK2 Motion` modifier on Trim), Trim Start 0.25 | Sweep starts at 12 o'clock and runs **clockwise**; Line draws left→right |
| H8 | Angle 30°, In Rotation 90, In Scale 0.5 | Rotation CCW (positive), scale about the shape's own centre |
| H9 | Stagger: 20 shapes, Index 0..19, Stagger 0.05 | Live stagger, no script |
| H10 | Multi-instance, two shapes renamed | Independent |
| H11 | Save/close/reopen (full app restart) | Unchanged; no BezierSpline on any SMK2 input |
| H12 | Colour pickers | Each of the 4 colour controls shows as one swatch + alpha (not 4 loose sliders); Inspector layout acceptable |
| H13 | **Benchmark:** 20 Shape cards (rounded rect, border, shadow) + 20 Text+ merged over a 1080p background, 60 fps timeline | Report render ms/frame, **viewer first-playback fps and cached fps**; compare with the G10 variants (baseline 7.5, Animators 72, Transforms 36) and v1 UIBlock if installed |
| H14 | Compare one shape card to the v1 `SMK_UIBlock` look | Visual notes: what the Shape cannot match yet |

Not in this slice (tracked in `docs/DEFERRED_WORK.md`): arrow, glass/backdrop blur, Look pass (glow), inverted/spotlight mode, `Progress` bar preset.
