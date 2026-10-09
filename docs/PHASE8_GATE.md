# Phase 8 Gate — SMK2 Relief, Reflection, Page Curl, Look upgrades, Connector 4K, spike S12 (run by Agent A, the only agent that drives Resolve)

`python scripts/install.py`, restart Resolve. **Scripting only (no UI automation).** Hygiene: deselect (`FlowView.Select()`) before each paste, comp rate = timeline rate,
cold renders (Background +0.001), readable graphs (distinct node positions via `flow:SetPos`, left→right, 2–3 units apart, clear names, one comp per check named after the check, a Note above each group),
`ProjectManager.SaveProject()`, project `SMK Phase8`. Keep "SMK Test" untouched. Write `docs/PHASE8_RESULTS.md` (table: check, comp, result, evidence), push `phase8-results`, paste the table in chat.
NOT VERIFIED where not observed. You may fix `build/make_macros.py`, `src/fuses/*.lua` and `src/core/*.lua`; re-run `python build/build.py` and `tests/test_*.py`, and describe each change.

These three Fuses were inspired by NeoEdit-style effects (bevel, emboss, reflection, paper curl) but are clean-room implementations; reference pixel functions + GPU kernels are verified against each other on
30,720 / 46,080 / 73,728 px (≤ 6e-6 difference, nearest-texel sampling). On the GPU the sampler is bilinear, so edges are a touch smoother than the test oracle.

## A. SMK2 Relief (bevel / emboss) — Effects ▸ Fuses ▸ SMK v2 ▸ SMK2 Relief
Image in → image out. Height from **Alpha** or **Brightness**; slope from a single Gaussian-derivative gather (no repeated blurs). Light direction (deg, + = counter-clockwise; 135 = from the upper left),
elevation, Size (px@1920), Depth, Highlight/Shadow amount and colours, Blend, Mode (**Bevel** = coloured highlight/shadow, **Relief Map** = grey), Quality 24/48/96 taps.

| # | Check | Pass criteria / report |
|---|---|---|
| R1 | On an `SMK2 Shape` card, a Text+ title, an `SMK2_TextLetter` macro; all defaults | Loads; edges facing the light (upper left) are lighter, opposite edges darker; flat interior unchanged; alpha unchanged |
| R2 | Direction 0 / 90 / 135 / 225 | Highlight moves around the object correctly (0 = highlight on the right-facing edge … report what you see) |
| R3 | Size 2 / 8 / 30 px, Depth 0 / 1 / 2 / 6 | Larger size = softer, wider bevel; Depth 0 = no effect; stronger depth never makes the lit edge darker (monotone) |
| R4 | Height From Brightness on a text with a bright inner stroke / photo | Brightness edges produce relief; Alpha mode ignores them |
| R5 | Mode Relief Map | Grey map, flat = mid-grey; usable as a displacement/lighting source |
| R6 | Premultiplied correctness over a bright and a dark background with soft edges | No dark or light fringe |
| R7 | 1080p, 1080×1920, 4K; 24/30/60 fps | Same look (px@1920); report cold ms/frame for Size 8 Normal and Size 30 High at 1080p and 4K |
| R8 | Two instances; save, full restart, reopen; no BezierSpline | Independent; pixel-identical |

## B. SMK2 Reflection — Effects ▸ Fuses ▸ SMK v2 ▸ SMK2 Reflection
Mirror about a horizontal baseline (fraction of height from the bottom) with Gap, Length, fade curve, opacity, **blur that grows with distance**, ripple (amount, frequency, speed in cycles/second, clip-relative), tint, Keep Original.

| # | Check | Pass criteria / report |
|---|---|---|
| F1 | Object (Shape / Text+ / Look) standing on the baseline; defaults | Reflection directly below the baseline, mirrored vertically, fades to nothing at Length |
| F2 | Baseline 0.2 / 0.4 / 0.7; Gap −10 / 0 / 20; Length 100 / 400 / 1000 | The mirror starts exactly at baseline − gap; length respected; nothing drawn outside the frame |
| F3 | Blur growth 0 / 4 / 15, blur at baseline 0 / 10 | Reflection gets softer with distance; at 0 it stays crisp; no banding/noise (report at Quality 0/1/2) |
| F4 | Ripple amount 0 / 6 / 20, frequency, speed ±1 | Wobbles sideways, none at the baseline, animates with time (same frame at 24 and 60 fps at equal seconds) |
| F5 | Tint colour/alpha; Keep Original off | Tint affects only the reflection; off = reflection only |
| F6 | Premultiplied/semi-transparent objects over a bright background | No fringe |
| F7 | **Does the reflection extend beyond the input's DoD?** (Text+ small DoD, baseline at the text bottom) | If the reflection is cut at the Text+ DoD/bounds, fix in `src/fuses/SMK2_Reflection.lua` by growing the output `IMG_DataWindow` (see `SMK2_Look.lua` for the working pattern) and describe |
| F8 | Resolutions, fps, cost (cold 60 fps), two instances, save/restart/reopen | As R7/R8 |

## C. SMK2 Page Curl — Effects ▸ Fuses ▸ SMK v2 ▸ SMK2 Page Curl
Page (Image) + optional **Reveal** input. Cylinder roll with shaded front, paper back (tint/dim) lying over the page, drop shadow. **Auto Out / Auto In** (Delay + Duration, seconds, clip-relative, symmetric ease) or Manual progress.
Direction = the direction the curl travels (deg, + = counter-clockwise; 180 = right to left).

| # | Check | Pass criteria / report |
|---|---|---|
| C1 | Page = a coloured card/photo; no Reveal; Mode Auto Out; defaults | Page intact before Delay; a roll travels right→left; the page behind the roll is gone (transparent); fully gone by Delay + Duration; last frame empty |
| C2 | Reveal connected (a second image) | The Reveal shows where the page has gone; page edge/roll anti-aliased; no black fringe |
| C3 | Manual progress 0 / 0.25 / 0.5 / 0.75 / 1 | Progress 0 = page untouched pixel-for-pixel; progress 1 = fully gone; monotone |
| C4 | Direction 0 / 90 / 180 / 270 / 45 | Curl travels in that direction (0 = left→right …); the roll stays straight (perpendicular to travel); report any wrong orientation |
| C5 | Radius 20 / 70 / 200; shadow strength/length; ambient; light angle; back tint/amount/brightness | Visible, sensible, no seams between flat page / roll / back (report any hard line) |
| C6 | Auto In (reverse) | Page rolls back on; first frame empty, last frame intact |
| C7 | Text+, Shape, a UI Block macro, a Look output as the page | Works for any RGBA; alpha holes stay holes |
| C8 | Timing in seconds at 24/30/60 fps; trimmed 46-frame clip | Same progress at equal seconds; ends with the clip (RenderEnd) |
| C9 | **Two source textures:** confirm `DVIPComputeNode` accepts `AddInput("src")` + `AddInput("bg")` | If it fails, report the exact console error |
| C10 | 1080p / 1080×1920 / 4K, cost cold 60 fps, two instances, save/restart/reopen | As R7/R8 |

## D. SMK2 Look upgrades (re-test)
New: **Glow Only**, **Glow Spread** (gamma), adaptive sample count (wide glows get ≥ 0.8 × radius taps, up to 160), adaptive outline rings, Glow Quality `Max (160)`. Also a duplicated-input bug in the Create() was removed.

| # | Check | Pass criteria / report |
|---|---|---|
| L1 | Glow R=120 px at Draft / Max; Spread 0.5 / 1 / 2 | Draft no longer shows ghost rings; Spread < 1 gives longer, brighter tails; difference image mean Draft vs Max |
| L2 | Glow Only on | Object removed, glow kept; usable under another copy of the object |
| L3 | Outline 20 px | No stair-steps; even width |
| L4 | Inspector | Each control appears once (no duplicates); labels readable |

## E. Connector 4K facets (re-test of K11)
The polyline cap was raised from 96 to 192 points (curves use 128 points beyond 800 px chords, splines up to 180). Re-run K11 at 4K and K13 cost with 1/5/10 connectors; report the max deviation from the true curve and any visible facets.

## F. Spike S12 — multi-pass GPU (`SMK2_Spike_S12_MultiPass`, Effects ▸ Fuses ▸ SMK v2 ▸ Spikes)
Question: can one Fuse run several `DVIPComputeNode` sessions in a row, with the intermediate `Image` of one pass feeding the next (downsample → blur → upsample)? That would unlock pyramid glow, bloom and long shadows at fixed cost.
Run the 4 methods on a high-contrast image (Shape on black) at 1080p and 4K; the Deferred Intermediates checkbox both on and off.

| # | Check | Pass criteria / report |
|---|---|---|
| S12-1 | Method 0 | Output equals the input |
| S12-2 | Method 1 (Down/Up) | Soft blocky copy; console shows both passes `RunSession=true`; intermediate is W/4 × H/4 |
| S12-3 | Method 2 and 3 | Method 2 softer than 1; method 3 softer than 1; no errors |
| S12-4 | Deferred on vs off | Which of the two works (or both) |
| S12-5 | Cost cold 60 fps, 300 frames | ms/frame for methods 0 / 1 / 3 at 1080p and 4K |
| S12-6 | Does a PreCalc guard matter? Intermediate sizes different from the output? | Report |

**For the user by hand:** whether bevel / reflection / curl look good (colour, light direction, curl feel), dragging Connector handles, viewer fps.
