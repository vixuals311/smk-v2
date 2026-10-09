# Phase 8 Results: Relief, Reflection, Page Curl, Look upgrades, Connector 4K, spike S12

Resolve Studio 21.1.0.14, Windows. Project `SMK Phase8` (your `SMK Test` was not touched). Scripting only, no UI automation. One comp per check (named after it, or after the group of cases it needed), each with a Note, explicit node positions (Note y −3; Background x 0; source x 4; effect x 8; Merge x 12; MediaOut x 16; one row per instance), `FlowView.Select()` before every paste, comp rate = timeline rate, Background +0.001 before every timed render, `SaveProject()` after each section. Comps are 24 fps, 120 frames, 1080p unless the name says otherwise. Measurements are PNG renders analysed with PIL (frame 40 unless stated). Setup: `git pull`, `python scripts/install.py --include-spikes`, Resolve restarted, `python build/build.py`, every `tests/test_*.py` run once: all pass (kernel-parity tests are **SKIPPED: no C compiler on this machine**, so the "≤ 6e-6" parity in the gate text was not re-run; I measured the GPU output in Resolve instead).

## Changes made in this phase

1. **`src/fuses/SMK2_Reflection.lua` (F7): the reflection was cut at the input image bounds.** Text+ with a small DoD is **not** clipped (the Fuse output window is the full canvas), but an input image smaller than the canvas (a 400×200 Text+) lost the reflection below its bottom edge (16 of 89 rows). Fix, same pattern as `SMK2_Look.lua`: `IMG_DataWindow = ImgRectI(dw.left − side, dw.bottom − bottom, dw.right + side, dw.top)` where `bottom` is the reflection reach below the data window and `side` = ripple + blur reach; kernel params `off[2]` / `osize[2]`, samples outside the source are transparent. No padding when the reflection fits (the canvas-size cases render pixel-identical). `tests/test_reflection.py`: 3 new checks (27 pass).
2. **`src/fuses/SMK2_PageCurl.lua`, `src/core/smk_curl.lua` (C2): the roll crest was not anti-aliased.** The roll branch was entered only for `t <= R`, which cut the half pixel of coverage beyond the crest, so the far edge of the curl was a hard 1-px step in about half the frames. Now `t <= R + 0.5` in oracle and kernel. After the fix every frame has a partial-coverage pixel at the crest. `tests/test_pagecurl.py`: new check (31 pass).
3. Spike S12 (`spikes/…`) unchanged. `python build/build.py` clean; all tests pass after both changes.

## A. SMK2 Relief

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| R1 | Defaults on Shape, Text+, TextLetter | `R1_defaults` | **PASS** | Shape card (115,128,153): left edge (177,184,198), top (173,180,195) lighter; right and bottom (67,74,89) darker; centre identical to the source (115,128,153); background outside identical (difference 0, so alpha unchanged). Within 20 px of the edge the interior still differs by up to 13–15 /255 (the bevel tail, centre exact). Text+ and TextLetter show the same bevel. `r1_relief.png` |
| R2 | Direction 0 / 90 / 135 / 225 | `R2_directions` | **PASS** | Edge brightness change on a grey card (left / right / top / bottom): 0° −77 / +76 / +3 / −4 (right edge lit); 90° +1 / −1 / +77 / −79 (top lit); 135° +55 / −55 / +52 / −53 (upper left lit); 225° +54 / −53 / −57 / +58 (lower left lit). 0 = light from the right, 90 = from above. `r2_dirs.png` |
| R3 | Size 2 / 8 / 30, Depth 0 / 1 / 2 / 6 | `R3_size_depth` | **PASS** | Lit-edge width (> 2/255): 5 / 19 / 69 px for size 2 / 8 / 30 (depth 2). Depth 0 / 1 / 2 / 6 at size 8: lit edge 0 / +35 / +60 / +89, shadow edge 0 / −34 / −58 / −87: monotone, depth 0 = no effect. `r3_size_depth.png` |
| R4 | Height from Brightness | `R4_brightness` | **PASS** | Dark card with a 14 px white inner border: Alpha mode profile across the border 255,255,255,255,255,31 (inner edge untouched); Brightness mode 255,255,200,153,19,24,29,31 (relief at the inner edge). `r4_brightness.png` |
| R5 | Mode Relief Map | `R5_relief_map` | **PASS** | Flat interior (127,127,127); lit edge 182, shadow edge 72, top 180; outside the object the background is untouched (the map is only inside the alpha). |
| R6 | Premultiplied over bright / dark | `R6_premult` | **PASS** | Soft-edged cards with shadow, default and Size 30 Depth 4, over 0.9 and 0.1: recovered alpha inconsistent 0 px, foreground below 0 on 0 px (min −0.6), above alpha 0 px. No fringe. |
| R7 | Resolutions, fps, cost | `R7_1080p`, `R7_1080x1920`, `R7_4K`, `R7_Fps24/30/60`, `R7_Bench_*` | **PASS** | 4K downscaled vs 1080p: mean difference 0.012 /255, max 12. 1080×1920 bevel is narrower in proportion to the width (px@1920 scales with the width: lit edge profile 1080p 61 / 49 / 35 / 7 / 0 vs 56 / 38 / 9 / 0 / 0). 24 / 30 / 60 fps: pixel-identical (max difference 0). Cost, 60 fps comp, 300 frames, cold, 1080p PNG (first run / second run) ms/frame: 1080p no effect 11.2 / 8.3, **Size 8 Normal 17.4 / 12.1, Size 30 High 17.6 / 12.2**; 4K no effect 19.1 / 18.4, **Size 8 Normal 24.5 / 19.0, Size 30 High 25.2 / 19.9**. The quality/size setting is invisible in these numbers (PNG encode dominates); viewer fps NOT VERIFIED (yours). |
| R8 | Two instances, restart | `R8_TwoInstances` | **PASS** | Two Relief tools (bevel size 8 / relief map size 20 direction 0 from brightness) independent; after a full quit and relaunch all 51 inputs of both identical, comp rate 24, frames 12 and 30 re-rendered **pixel-identical**; tool IDs only `Fuse.SMK2_Relief`, Shape, Background, Merge, MediaOut, Note (**no BezierSpline**). |

## B. SMK2 Reflection

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| F1 | Defaults on Shape, Text+, Look output | `F1_defaults` | **PASS** | Mirrored vertically below the baseline (gradient card: red end next to the baseline), fades to nothing. Faint horizontal banding is visible on the gradient reflection. `f1_defaults.png` |
| F2 | Baseline 0.2 / 0.4 / 0.7, Gap −10 / 0 / 20, Length 100 / 400 / 1000 | `F2_baseline_gap_length` | **PASS** | Baselines at image rows 864 / 648 / 324: the reflection starts on the baseline row; Gap +20 starts 20 rows below, Gap −10 overlaps 10 rows above (hidden behind the object); the extent is limited by the object height (228 px at Length 400 and 1000) and Length 100 → 92 px visible; baseline 0.2 is cut by the frame bottom (row 1079). |
| F3 | Blur growth 0 / 4 / 15, blur at baseline 0 / 10, Quality 0 / 1 / 2 | `F3_blur_growth` | **PASS with notes** | Right-edge 10–90 % width at 5 / 40 / 100 / 200 / 350 rows below the baseline: growth 0 → 0 / 0 / 0 / 0 / –; growth 4 → 0 / 1 / 2 / 8 / 14; growth 15 → 1 / 3 / 8 / 31 / 57; growth 4 + blur 10 → 5 / 6 / 7 / 18 / 22; growth 15 Quality 0 → 1 / 3 / 8 / 31 / 54, Quality 2 → 1 / 3 / 7 / 31 / 46. Crisp at 0, softer with distance. **Faint stepped streaks (ghost copies) are visible in the blurred edge wedge at every quality, smoother at Quality 2** (`f3_quality_q1_q0_q2.png`). |
| F4 | Ripple amount 0 / 6 / 20, frequency, speed ±1 | `F4_ripple`, `F4_ripple_fps60` | **PASS** | Edge peak-to-peak displacement 0 / 12 / 40 / 40 / 40 px for amount 0 / 6 / 20 (= 2 × amount); within 8 px of the baseline no displacement; speed −1 runs the other way; t = 0.25 s and 0.75 s differ; the 24 fps frame 6 and the 60 fps frame 15 are **pixel-identical**. (The 5 px shift of all rows at t = 0.25 s is the Shape source's own In animation.) |
| F5 | Tint, Keep Original off | `F5_tint_keep` | **PASS** | Object unchanged; red tint (alpha 1) reflection (212,8,10); blue tint alpha 0.5 reflection (23,23,133): the tint colour multiplies and **its alpha scales the reflection like an opacity**; Keep Original off: object area = background (38,38,51), reflection kept. |
| F6 | Premultiplied | `F6_premult` | **PASS** | Soft card + Text+ with reflection over 0.9 / 0.1: alpha-inconsistent 0, foreground below 0 on 0, above alpha 0. |
| F7 | Clipped at the DoD? | `F7_DoD` | **Text+ DoD: not clipped. Smaller input image: clipped → FIXED** | Text+ DataWindow (819, 705)–(1108, 808) (small), Reflection output window (0, 0)–(1920, 1080): the reflection extends far below the DoD. A 400×200 Text+ image: before the fix the reflection stopped at the image bottom (ink rows 536–639); after: output window (0, −170)–(400, 200), ink rows 536–711 (`f7_before_fix.png`, `f7_after_fix.png`). Change 1 above. |
| F8 | Resolutions, fps, cost, two instances, restart | `F8_1080p`, `F8_1080x1920`, `F8_4K`, `F8_Fps24/30/60`, `F8_Bench_*`, `F8_TwoInstances` | **PASS** | 4K downscaled vs 1080p: mean difference 0.010 /255 (max 85 on edges); reflection depth / frame width 0.1422 / 0.1417 / 0.1422; 24 / 30 / 60 fps at 0.5 s and 1.0 s pixel-identical; cost cold 60 fps (first / second): 1080p **17.6 / 12.0** (no effect 11.2 / 8.3), 4K **24.5 / 18.5** (no effect 19.1 / 18.4). Two instances (ripple 10 + blur 4 / tint blue, keep off): after restart all 53 inputs of both identical, frames 12 and 30 **pixel-identical**, no BezierSpline. |

## C. SMK2 Page Curl

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| C1 | Defaults, no Reveal | `C1_defaults` | **PASS** | Solid red full-frame page, Auto Out, delay 0.2 s, duration 1.2 s, direction 180. Frames 0–8 are the untouched page (1 colour); the roll travels right → left (remaining page 0…1912 → 0 px); page behind the roll is transparent; fully gone at frame 34 (1.42 s); last frame empty. Structure at frame 18: flat page 0–610 | paper back 610–1225 with the drop shadow at its far edge on the page (a hard line there is the paper edge) | roll crest 1225 | transparent. No seam inside the roll. `c1_frame18.png` |
| C2 | Reveal connected | `C2_reveal` | **PASS after fix** | Frame 2 page, frame 18 green reveal beyond the crest (51,204,77), frame 36 full reveal; no black fringe. **The crest was a hard 1-px step (before the fix, about half the frames had no partial pixel); fixed (change 2), every frame now has a partial pixel at the crest** (`p8_c1_fix` frames 10–32). The reveal receives no drop shadow from the roll (the shadow falls on the page only). `c2_frame18.png` |
| C3 | Manual progress 0 … 1 | `C3_manual` | **PASS** | Gradient Shape page at frame 40: progress 0 is **pixel-identical** to the source (max difference 0); covered fraction 1.000 / 0.779 / 0.521 / 0.263 / 0.000 for 0 / 0.25 / 0.5 / 0.75 / 1 (monotone), 1 = gone. |
| C4 | Direction 0 / 90 / 180 / 270 / 45 | `C4_directions` | **PASS** | Progress 0.5: the curl travels in the given direction in every case (the remaining page lies ahead of it: centroid offset along travel +462 / +255 / +465 / +252 px); the far edge is perfectly straight per scan line (x = 925 / 574 / 994 / 505); at 45° the boundary slope is dx/dy = 1.000 (perpendicular to the travel), residual 1.9 px. No wrong orientation. |
| C5 | Radius, shadow, ambient, light, back controls | `C5_params` | **PASS (looks judged from a contact sheet)** | 15 renders at progress 0.5 (`c5_contact_sheet.png`): Radius 20 / 70 / 200, Shadow strength 0 / 1, length 30 / 400, Ambient 0 / 1, Light angle −60 / 70, Back tint 0 / 1, Back brightness 0.4 / 1.2. Every one has exactly one hard step on a row: the end of the paper back (the paper edge); no seam between flat page, roll and back. Whether the look is good: yours. |
| C6 | Auto In | `C6_auto_in` | **PASS** | Coverage 0 on frames 0–4, 0.40 at frame 18, 1.0 from frame 30; the last frame is the page only (one colour). |
| C7 | Text+, Shape, UI Block, Look output | `C7_sources` | **PASS** | Progress 0 is pixel-identical to the sources for all four; at 0.5 the holes between letters stay transparent (background shows), the flap shadows the page under the back region. `c7_progress50.png` |
| C8 | Seconds at 24 / 30 / 60 fps, trimmed clip | `C8_Fps24/30/60`, `C8_Trim46` | **PASS** | 0.5 s and 1.0 s frames pixel-identical across rates. 46-frame range (comp render range 0–45 set with `SetAttrs`, **not a real trimmed timeline clip**: dragging a trim handle is yours): covered 1.0 / 0.438 / 0 / 0 / 0 at frames 0 / 20 / 33 / 34 / 45. The curl timing is Delay + Duration in seconds and does not depend on the clip length. |
| C9 | Two textures in `DVIPComputeNode` | `C1_defaults`, `C2_reveal` | **ACCEPTED: `AddInput("src")` + `AddInput("bg")` work** | The kernel with two input textures renders the curl and the reveal image (no pass-through fallback, which would show the page unchanged). **No error was seen.** I cannot read the Fusion console, and the Resolve logs contain no "GPU failed" lines, so the console text itself is NOT VERIFIED; the evidence is the correct output. |
| C10 | Resolutions, cost, two instances, restart | `C10_1080p`, `C10_1080x1920`, `C10_4K`, `C10_Bench_*`, `C10_TwoInstances` | **PASS** | 4K downscaled vs 1080p mean 0.024 /255 (max 5); far edge / width 0.5177 / 0.5180 / 0.5176. Cost cold 60 fps, Manual 0.5 (first / second): 1080p no effect 5.3 / 4.6, **curl 10.2 / 8.3**; 4K no effect 18.2 / 18.2, **curl 19.7 / 18.8**. Two instances (red direction 180 progress 0.3 / green direction 90 progress 0.6): after restart all 56 inputs of both identical, no BezierSpline, frame 40 **identical except a 1-px column at x = 1393 (the crest anti-aliasing added by change 2)**. |

## D. SMK2 Look upgrades

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| L1 | Glow R120 Draft / Max, Spread 0.5 / 1 / 2 | `L1_glow_quality` | **PASS** | Draft shows no ghost rings any more (`l1_R120_draft_normal_high_max.png`). Mean absolute difference from Max (/255): Draft 2.62, Normal 1.52, High 1.52 (Normal and High are identical at R120: the adaptive tap count is the same). Ring roughness 1.23 / 1.23 / 1.23 vs Max 1.04. Spread 0.5 / 1 / 2, blue excess at 10 / 60 / 100 px: 136 / 65 / 21, 82 / 19 / 2, 29 / 1 / 0: spread < 1 gives longer, brighter tails. |
| L2 | Glow Only | `L2_glow_only` | **PASS** | Object removed, glow kept (centre shows the glow colour (115,166,255), no white object); with a copy of the object merged on top it looks like glow + object. `l2_full.png` |
| L3 | Outline 20 px | `L3_outline20` | **PASS on smooth shapes, partly on text** | Ellipse: outer radius beyond the edge 19.37 px mean, std 0.48 (min 19, max 20): no stair-steps. Text+: a fine serration is still visible on outer corners and diagonals. `l3_full.png` |
| L4 | Inspector | (input list) | **PASS from the input list; the panel itself NOT VERIFIED** | Every custom Look control appears once (no duplicate IDs or labels; only Fusion's standard Comments / Frame Render Script repeat). |

## E. Connector 4K facets

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| E-K11 | Re-test of K11 | `E_K11_1080p`, `E_K11_1080x1920`, `E_K11_4K` | **PASS: facets gone** | Max distance of the true curve from the drawn polyline (1080p / 1080×1920 / 4K): Curve 0.00 (a straight line without a magnet, as before), Bezier arch 0.017 / 0.015 / 0.033 px, Spline N=6 zig-zag **0.174 / 0.304 / 0.347 px** (Phase 7: 0.71 / 1.18 / 1.41). The 4K spline crop is smooth (`e_k11_4k_spline_crop.png`). Rendered ink is within 1.72–4.23 px of the centreline against half thickness 1.5 / 0.8 / 3 (includes anti-aliasing). |
| E-K13 | Cost | `E_K13_Bench1/5/10` | **Unchanged** | 60 fps, 300 frames, cold, Bezier + dash + pulses + dot + arrow (first / second run): 1 connector 12.0 / 8.9 ms, 5: 35.1 / 18.1, 10: 64.4 / 30.3 (Phase 7: 12.8 / 9.7, 38.3 / 19.6, 70.0 / 32.0). Viewer fps NOT VERIFIED. |

## F. Spike S12 (multi-pass GPU)

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| S12-1 | Method 0 | `S12_Methods_1080p/4K` | **PASS** | Centre 255, right-edge 10–90 % width 1 px (the input's own edge). |
| S12-2 | Method 1 (Down/Up) | same | **PASS** | Soft blocky copy: edge 5 px at 1080p, 6 px at 4K, halo 5 / 4 px. Both passes ran (output differs from the input; a failed pass would fall back to the unchanged input). The intermediate (W/4 × H/4) was accepted. **The `[S12]` console lines were not read (console not readable): `RunSession=true` is inferred from the output.** `s12_1080p.png`, `s12_4K.png` |
| S12-3 | Methods 2 and 3 | same | **PASS** | Edge width 1080p: m1 5, **m2 22**, **m3 10** px; 4K: 6 / 25 / 11. Method 2 and 3 are both softer than 1; no errors seen. |
| S12-4 | Deferred on vs off | same | **BOTH work, identical results** | Edge widths identical for every method at both resolutions (full-crop pixel comparison is not meaningful: the two rows are at different sub-pixel positions). |
| S12-5 | Cost | `S12_Bench_*` | **Multi-pass costs about the same as one pass** | 60 fps, 300 frames, cold (first / second run) ms/frame. 1080p: no effect 11.3 / 8.4; method 0 17.0 / 12.0; method 1 17.4 / 12.4; method 3 18.0 / 12.5. 4K: no effect 24.5 / 21.6; method 0 33.0 / 27.1; method 1 33.3 / 26.9; method 3 34.0 / 24.1. PNG encoding dominates, so extra passes at W/4 add almost nothing here. |
| S12-6 | PreCalc guard, intermediate sizes | | **Intermediate sizes different from the output work (W/4 × H/4); PreCalc guard: NOT VERIFIED** | I did not remove the guard (the spike has `REG_NoPreCalcProcess` and returns early on PreCalc requests, as the other Fuses do; the earlier finding that `DVIPComputeNode` is nil on PreCalc was not re-tested). |

## Notes for you

**Confusing in the Inspector (from the input lists and behaviour; the panels themselves NOT VERIFIED):**
- Page Curl: the Direction label is very long ("Curl Travel Direction (deg, + = counter-clockwise; 180 = right to left)"); "Reveal (optional)" and "Page" are the two image inputs; the Progress slider only matters in Manual mode.
- Reflection: Gap > 0 moves the reflection **down**; the tint alpha acts like an opacity (colour multiplies, alpha scales); Baseline is a fraction of the height measured from the bottom, so objects must be positioned in Fusion's normalised y-up coordinates.
- Relief: Direction 0 = light from the right, 135 = from the upper left; Mode "Relief Map" outputs grey only inside the object's alpha.
- Test gotcha: the SMK2 Shape source animates (empty on frame 0 and on the last frames even with In Duration 0 because of its Out), so single-frame measurements of Shape-fed effects must avoid the first and last frames.

## Not verified
- Fusion console text (C9, S12 `[S12]` lines): not readable; judged from the output.
- Kernel parity (no C compiler); viewer fps; Inspector panel look.
- A real trimmed timeline clip (C8, K-like): comp render range used instead.
- S12-6 PreCalc guard.

## For you to check by hand
1. Whether the bevel, reflection and page curl look good (colours, light direction, curl feel, paper back tint, drop shadow).
2. Dragging Connector handles and points in the viewer.
3. Viewer fps for Relief, Reflection, Page Curl and the connectors.
4. Dragging a trim handle on a Page Curl clip.

## Evidence
`docs/phase8_evidence/`: scripts `h11.py`, `premult.py`, `c1an.py`, `r23an.py`, `e11an.py`; raw numbers per check in `p8_notes.md`; images named after the checks.
