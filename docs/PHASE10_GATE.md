# Phase 10 Gate — SMK2 Long Shadow, Reflection blur, Look outline, Inspector labels (run by Agent A)

`python scripts/install.py`, restart Resolve. **Scripting only.** Standard hygiene: deselect (`FlowView.Select()`) before each paste, comp rate = timeline rate, cold renders (Background +0.001),
readable graphs (distinct `flow:SetPos` positions, left→right, 2–3 units apart, clear names, one comp per check named after the check, a Note per group), `ProjectManager.SaveProject()`, project `SMK Phase10`.
Keep "SMK Test" untouched. Write `docs/PHASE10_RESULTS.md` (table: check, comp, result, evidence), push `phase10-results`, paste the table. NOT VERIFIED where not observed.
Shape sources are empty on frame 0 and the last frames: avoid those for single-frame checks. You may fix `src/fuses/*.lua` / `src/core/*.lua`; re-run build + tests and describe each change.

## A. SMK2 Long Shadow (new; Effects ▸ Fuses ▸ SMK v2 ▸ SMK2 Long Shadow)
Flat long shadow behind any element, multi-pass (init + ceil(log2(length+1)) doubling passes + composite): shadow = max over distance of (alpha − distance/Length), so it fades linearly to nothing at Length.
Direction (deg: 0 = right, 90 = up, −45 = down-right), Length (px@1920, up to 1500), Fade Curve, colour/alpha, Opacity. The output window is padded only on the shadow's side. Pipeline verified against its Lua reference on ~47,000 px (max diff 7e-6).

| # | Check | Pass criteria / report |
|---|---|---|
| S1 | On a Shape card, a Text+ title, an `SMK2_TextLetter` macro; defaults | Loads, no error, **not a pass-through** (shadow visible; compare with bypass); shadow down-right, fading out |
| S2 | Direction 0 / 45 / 90 / 135 / 180 / −45 / −90 | Shadow goes the stated way (0 = right, 90 = up); the shadow is a straight extrusion, no gaps or stripes along thin strokes of text (zoom 400 %) |
| S3 | Length 50 / 200 / 400 / 1000 | Reach ≈ Length (measure where alpha drops below 2/255); Fade Curve 0.5 / 1 / 2 changes the fade |
| S4 | Shadow colour/alpha, opacity | Colour correct, no fringe over bright and dark backgrounds, shadow behind the object |
| S5 | **DoD:** small Text+ with a 600 px shadow; Shape near the frame edge | Not clipped at the input's DoD or the frame; padding only on the shadow side |
| S6 | 1080p, 1080×1920, 4K; 24/30/60 fps | Same look (px@1920), shadow length scales with width |
| S7 | Animated input (Shape In/Out, Motion on a Text+) | Shadow follows the input every frame |
| S8 | Cost (cold 60 fps): Length 100 / 1000 at 1080p and 4K; 1 / 5 / 10 instances | ms/frame each; expectation: grows only logarithmically with length |
| S9 | Two instances; save, full restart, reopen; no BezierSpline | Independent; pixel-identical |
| S10 | Inspector | Labels readable |

## B. Reflection blur (fix for the stepped streaks, D8-006)
The spiral gather now has a per-pixel rotation (interleaved-gradient noise) and its tap count rises with the blur (up to 128).

| # | Check | Pass criteria / report |
|---|---|---|
| F1 | Re-run F3: Blur growth 4 / 15 / 30, Blur at baseline 0 / 10, Quality 0 / 1 / 2 on a text and a hard-edged shape | Stepped streaks gone? Report what remains (fine grain/noise level, mean abs difference vs Quality 2); recommend the default Quality |
| F2 | Animated (ripple on): is the grain stable frame to frame? | Report any shimmer (the noise pattern is static per pixel, so there should be none) |
| F3 | Cost at Quality 1, blur growth 15, 1080p and 4K | ms/frame; compare with Phase 8 |
| F4 | Inspector | "Gap (+ moves the reflection further down)" and "Tint (alpha = strength)" labels |

## C. Look outline (D8-007)
Outline directions now scale with the width (24 up to 72) so the arc gap stays ≤ ~2 px.

| # | Check | Pass criteria / report |
|---|---|---|
| O1 | Text+ at 40 pt with Outline 6 / 20 / 40 px | Serration gone? Even width, smooth corners (zoom 400 %); report remaining artifacts |
| O2 | Cost: Outline 20 px, 1080p and 4K | ms/frame vs Phase 7/8 numbers |

## D. Labels
| # | Check | Pass criteria / report |
|---|---|---|
| I1 | `SMK2 Relief` "Light Direction (0 = from the right, 90 = from the top, 135 = upper left)", `SMK2 Page Curl` "Curl Direction (deg, 180 = right to left)", `SMK2 Bloom` "Intensity" default 4 | Labels present; Bloom at defaults looks comparable to Look at the same radius |

**For the user by hand:** whether the long shadow, reflection and outline look good; viewer fps.
