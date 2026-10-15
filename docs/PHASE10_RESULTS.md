# Phase 10 Results: SMK2 Long Shadow, Reflection blur, Look outline, labels

Resolve Studio 21.1.0.14, Windows. Project `SMK Phase10` (your `SMK Test` was not touched). Scripting only, no UI automation. One comp per check (named after it), each with a Note, explicit node positions (Note y −3; Background x 0; source x 4; effect x 8; Merge x 12; MediaOut x 16; one row per instance), `FlowView.Select()` before every paste, comp rate = timeline rate, Background +0.001 before every timed render, `SaveProject()` after each section. Comps are 24 fps, 120 frames, 1080p unless the name says otherwise. Measurements are PNG renders analysed with PIL (frame 40 unless stated; the Shape source is empty on frame 0 and the last frames and was not used there).

## Setup and changes made in this phase

Setup: `git pull`, `python scripts/install.py`, Resolve restarted, `python build/build.py`, every `tests/test_*.py` run once: all pass (**kernel-parity tests SKIPPED: no C compiler on this machine**; the GPU output was measured in Resolve).

**Two Windows-only fixes were needed before the build and `test_release.py` would pass** (no Fuse behaviour changed):
1. `tools/gen_manual.py` opened the sources and `docs/MANUAL.md` with the system code page (cp1252) and crashed on `▸`. Now `encoding="utf-8"` for reads and the write.
2. `build/build.py` read and wrote the Fuse sources with the system code page: the built `.fuse` files contained a cp1252 byte (0x97, an em dash from the header) and were not valid UTF-8, which failed `test_release.py` ("no runtime require in shipped Fuses" decode). Now `encoding="utf-8"` on every `open`.

## A. SMK2 Long Shadow

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| S1 | Shape card, Text+ title, TextLetter; defaults | `S1_defaults` | **PASS: the shadow is really produced, not a pass-through** | Rendered with the shadow vs the three Long Shadow tools bypassed: **448,892 pixels differ** (max difference 102 / 102 / 104) inside the box 345…1889 × 262…1080; the shadow runs down-right and fades out; output window (−2, −285)–(2205, 1082). The Fusion console is not readable from scripting (no `GPU failed` text seen in the Resolve logs); the pixel comparison is the evidence. `s1_shadow.png` |
| S2 | Direction 0 / 45 / 90 / 135 / 180 / −45 / −90 | `S2_directions` | **PASS: right directions, no gaps or stripes on thin strokes** | Seven crosses made of a 4 px wide, 150 px long bar: the extrusion goes right / up-right / up / up-left / left / down-right / down (0 = right, 90 = up, `s2_dirs.png`). Along the centre line the darkening decays smoothly with **0 dips** in every direction (10 / 100 / 200 px: 99 / 69 / 34 on diagonals); the bar's shadow is a clean parallelogram. Reach on the centre line 294–300 px of 300 (240 for 180°, cut by the frame edge). At 400 % zoom on Text+ (`s2_zoom400_text.png`) the shadow bands of neighbouring strokes meet in clean diagonal steps (the max of the per-stroke ramps); **no holes or stripes inside a stroke's extrusion**. Thin light slivers between letters are the real gaps between the letters' shadows. |
| S3 | Length 50 / 200 / 400 / 1000, Fade Curve 0.5 / 1 / 2 | `S3_length` | **PASS** | Reach from the object edge where the darkening drops below 2/255: **49 / 198 / 396 / 993 px** for Length 50 / 200 / 400 / 1000 (≈ Length − 1…−7). Darkening at L/4 / L/2 / 3L/4 for Length 400: curve 1 153 / 102 / 51 (linear), curve 0.5 177 / 144 / 102 (longer, brighter), curve 2 114 / 50 / 13 (shorter; reach 370). `s3_len.png` |
| S4 | Colour, alpha, opacity, fringe | `S4_colour` | **PASS** | Soft-edged cards and Text+ over 0.9 and 0.1 backgrounds: red alpha 0.6, black alpha 1 × opacity 0.5, red text shadow: alpha-inconsistent 0 px, foreground below 0 on 0 px (min −0.6), above alpha 0 px: no fringe. Red alpha 0.6 on the dark background (143, 12, 12); the object (77,153,230) is untouched (the shadow is behind). |
| S5 | DoD | `S5_dod` | **PASS: not clipped; padding only on the shadow side** | Direction −45, Length 600. Text+ (DataWindow (170, 822)–(411, 907)): output window (−2, −427)–(2347, 1082): grown by 427 px to the right and to the bottom only (the shadow side), +2 elsewhere; the shadow reaches about 594 px diagonally from the text corner (`s5_dod.png`). A 400×200 Text+ image: window (−2, −91)–(491, 202) (length scales with the width: 125 px). A Shape near the right frame edge: the shadow runs off the frame (expected, not cut by a DoD). |
| S6 | 1080p, 1080×1920, 4K; 24/30/60 fps | `S6_1080p`, `S6_1080x1920`, `S6_4K`, `S6_Fps24/30/60` | **PASS** | 4K downscaled vs 1080p mean difference 0.037 /255 (max 46 on edges); shadow reach / frame width 0.1458 (1080p), 0.1461 (4K), 0.1444 (1080×1920): scales with the width (px@1920); 24 / 30 / 60 fps frames pixel-identical (max difference 0). |
| S7 | Animated input | `S7_animated` | **PASS** | Shape In/Out and an SMK2_TextLetter macro, frames 0–119, against a bypassed render: shadow present from the first object frame (Shape: object frame 1, shadow frame 1; TextLetter: object 2, shadow 1) to the last (object 116 / 115, shadow 117 / 118); no frame has an object but no shadow; the only "shadow without a counted object" frames are the 1–3 frames at each end where the object is below my threshold (the fading tails). Correlation of object and shadow area 0.74 (Shape) / 0.99 (TextLetter). |
| S8 | Cost | `S8_*` | **Grows only slightly with length (log passes)** | 60 fps, 300 frames, cold PNG (first / second run) ms/frame. **1080p:** no effect 12.0 / 8.5; **L100 19.7 / 13.7; L1000 20.1 / 14.2** (+0.4 / +0.5 ms for 10× the length). **4K:** no effect 18.5 / 17.9; **L100 26.5 / 20.5; L1000 30.1 / 21.3**. **Instances (1080p, L400):** 5 cards no effect 36.0 / 18.5, **5 shadows 64.9 / 32.5**; 10 cards no effect 66.4 / 30.8, **10 shadows 123.9 / 60.0** (≈ 3 ms warm per instance). Viewer fps NOT VERIFIED (yours). |
| S9 | Two instances, restart | `S9_TwoInstances` | **PASS** | Two tools (A: direction 0, length 600, red alpha 1; B: direction 135, length 150, black alpha 0.4, curve 0.5) are independent; after a full quit and relaunch all 45 inputs of both identical, comp rate 24, frames 20 and 60 re-rendered **pixel-identical** (max difference 0); tool IDs only `Fuse.SMK2_LongShadow`, Shape, Background, Merge, MediaOut, Note (**no BezierSpline**). |
| S10 | Inspector | (input list) | **Labels readable; panel itself NOT VERIFIED** | Custom controls, each once, no duplicate IDs: "Shadow Direction (deg: 0 = right, 90 = up, -45 = down-right)", "Length (px @1920)", "Fade Curve (1 = linear, <1 = longer, brighter)", "Shadow Colour", "Opacity". |

## B. Reflection blur (D8-006)

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| F1 | Re-run F3: growth 4 / 15 / 30, blur at baseline 0 / 10, Quality 0 / 1 / 2, text and hard-edged shape | `F1_blur` | **Stepped streaks gone; recommend Quality 1 (default) and Quality 0 is acceptable** | The blurred edge wedge is smooth at all three qualities (`f1_squares_q0_q1_q2.png`, `f1_text_q0_q1_q2.png`): no ghost copies. What remains is invisible grain: growth 15 mean absolute difference from Quality 2 is **0.20 /255 (Q0) and 0.32 /255 (Q1)** on the square and 0.22 / 0.34 on the text (the very small values are the whole remaining difference). My high-pass "grain" number (about 2.2 /255) is dominated by the content edges and is equal at Q0 / Q1 / Q2, so it does not separate the qualities. Quality 1 stays the default; Quality 0 is visually the same here. |
| F2 | Animated ripple: grain stable? | `F2_shimmer` | **PASS: no shimmer** | Ripple 0: consecutive frames differ by 0.0 /255 (one 0.003 once), high-frequency rms 2.23 on all frames. Ripple 6 px speed 0.5: frame-to-frame difference 0.37 /255 (the movement) with a constant high-frequency rms 2.27–2.28: the noise pattern does not change over time. |
| F3 | Cost, Quality 1, growth 15, ripple 6 | `F3_cost_1080p`, `F3_cost_4K` | **Same as Phase 8** | 60 fps cold (first / second run): 1080p **18.5 / 12.6** (Phase 8 `F8_Bench`, growth 4: 17.6 / 12.0), 4K **24.8 / 19.5** (24.5 / 18.5). |
| F4 | Inspector | (input list) | **Labels present** | "Gap (px @1920; + moves the reflection further down)" and "Tint (alpha = strength)" are there. |

## C. Look outline (D8-007)

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| O1 | Text+ with outline 6 / 20 / 40 px | `O1_outline` | **PASS: the serration is gone** | At 6 / 20 / 40 px the outer edge along a vertical stem of the H is perfectly straight (x standard deviation 0.00 px, min = max). The white ellipse with 20 px: outer radius beyond the edge 19.46 px mean, std 0.53 (min 18, max 21) (Phase 8: 19.37 / 0.48). Corners are smooth scallops following the letter shapes (`o1_outline.png`, 300 % zoom `o1_zoom_20.png`); no remaining stair-steps seen. |
| O2 | Cost, outline 20 px | `O2_1080p_*`, `O2_4K_*` | **1080p +5.5 ms; 4K is expensive: +52 ms** | Text+ title, 60 fps cold PNG (first / second run): 1080p no effect 5.3 / 4.8, **outline 20 px 10.9 / 10.7**; 4K no effect 17.9 / 18.3, **outline 20 px 70.5 / 70.8**. The outline direction count now scales with the width (24 up to 72 rings), so 4K is about 4× the baseline; not fixed here (an optimisation could cap the ring count by the outline width instead). Phase 7/8 had no outline-only cost number to compare. |

## D. Labels

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| I1 | Relief, Page Curl, Bloom labels and defaults | `I1_labels` | **PASS** | Relief: "Light Direction (deg: 0 = from the right, 90 = from the top, 135 = upper left)". Page Curl: "Curl Direction (deg, 180 = right to left)". Bloom: "Intensity (Bloom is softer than Look: ~4x Look)", **default 4.0**. Bloom at defaults vs Look glow R120 (Max) on the same square: blue excess at 1 / 10 / 30 / 60 / 100 px 191 / 111 / 35 / 10 / 0 vs 141 / 85 / 49 / 21 / 2; mean absolute difference 2.45 /255 (comparable; the Bloom tail is slightly shorter). No duplicate IDs in any of them. `i1.png` |

## Not verified
- Fusion console text (S1): not readable; judged from the pixels.
- Kernel parity (no C compiler); viewer fps; Inspector panel appearance.
- Whether the effects look good (yours).

## For you to check by hand
1. Whether the long shadow, the reflection blur and the outline look good (colour, fade, softness).
2. Viewer fps with several Long Shadows (≈ 3 ms each) and with the 4K outline (about 50 ms extra).

## Evidence
`docs/phase10_evidence/`: `h11.py`, `premult.py`, `p10_notes.md` (raw numbers), images named after the checks.
