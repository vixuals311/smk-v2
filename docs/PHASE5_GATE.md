# Phase 5 Gate — SMK2 Cursor, font weight fix, UTF-8 re-check

`python scripts/install.py`, restart Resolve, paste macros fresh. **Scripting only (no UI automation).** Hygiene: deselect before paste, comp rate = timeline
rate, cold renders (Background +0.001), readable graphs with distinct node positions, clear names, one comp per check, a note per group, `SaveProject()`,
project `SMK Phase5 Gate`.

## A. SMK2 Cursor (new Fuse: Effects ▸ Fuses ▸ SMK v2 ▸ SMK2 Cursor)
One Fuse: anti-aliased pointer (polygon, no image file), up to 8 waypoints (Point controls with on-screen crosshairs), per waypoint *Move to (s)*,
*Hold (s)*, *Click*; Move Style Smooth / Snappy / Spring; Path Arc; Start Delay; press dip; up to 3 simultaneous click ripples; Fade In / Out; clip length
from the clip. Reference pixel function and GPU kernel verified on 73,728 pixels (max diff 6.5e-6); path/click maths verified in 27 + 14 unit tests.

| # | Check | Pass criteria / report |
|---|---|---|
| C1 | Add `SMK2 Cursor` to a comp over a Background | Loads; no console error; transparent output; defaults: white pointer, dark outline, soft shadow |
| C2 | Defaults over time | Pointer fades in at ≈ 0.4 s at waypoint 1, holds, glides to waypoint 2 (≈ 1.2 s), click: press dip + blue ripple, moves to waypoint 3, click again, rests, fades out ending at the last frame. Report the pointer tip position (px) at each arrival frame and the press/ripple frames |
| C3 | **Hot spot accuracy:** at each arrival frame (after the move ends) measure where the pointer's tip pixel is | Within ±1 px of waypoint × frame size, on 1080p, 1080×1920 and 4K |
| C4 | Waypoints: N = 2…8 via script (`SetInput`), change positions, Move/Hold times | Timeline follows: arrival time = Start Delay + Σ(Move + Hold of earlier waypoints); report the measured arrival frames vs expected |
| C5 | Move Style Smooth / Snappy / Spring, Arc −0.2 / 0 / 0.2 | Smooth is symmetric (half time ≈ half way); Spring overshoots then settles; Arc bends the path perpendicular, endpoints unchanged; path is the same shape on 16:9 and 9:16 (isotropic) |
| C6 | Clicks: Click on/off per waypoint, rapid clicks (hold 0.1 s), press depth / duration, ripple radius / thickness / duration / colour | Press dip centred on the click time; ripples expand and fade; overlapping ripples both visible (max 3) |
| C7 | Fade In / Out, trimmed clip (46-frame clip) | Opacity 0 on frame 0 and on the last frame; follows the new clip length |
| C8 | 24 / 30 / 60 fps comps (rate = timeline rate) | Pixel-identical at equal seconds (± 1/255) |
| C9 | Over a `SMK2_UIBlock`: cursor moves onto the card, click, card still animates | Premultiplied edges, no dark fringe along the pointer outline |
| C10 | Two instances (copy-paste + renamed) | Independent |
| C11 | Save, full restart, reopen | Unchanged; no BezierSpline on any SMK2 input; pixel-identical |
| C12 | Cost: 1 cursor, 3 cursors, 60 fps, cold, 300 frames | Report ms/frame |
| C13 | Inspector input list for the waypoint Point inputs (`GetInputList`: control type) | Report whether they are `OffsetControl` with a Crosshair preview (viewer widgets) — NOT scriptable to drag; user checks the widgets by hand |

## B. Font weight does not change (user report)
In the Text macros the Inspector's Text page shows Font = *Open Sans* and a Style combo (*Regular*), but changing the style does not change the weight:
the macro's real `Style` input (`Bold`) is not what that combo edits. Phase 2d also saw the "Font Style" row show "--" when `Style` was published separately.

| # | Check | Pass criteria / report |
|---|---|---|
| F1 | Paste `SMK2_TextLetter`. `GetInputList()` on the group: which inputs exist for font / style? Which input does the visible Style combo write? Try `SetInput` on every style-related input name and render | Table: input ID → effect on weight |
| F2 | Variant A: publish the inner `Style` as its own control (edit `UIT_Text_Style` InstanceInput into the macro text). Variant B: also publish `Font` under a different name. Variant C: add a `Weight` combo on `UIT_Ctrl` (Regular, Bold, Light, SemiBold, ExtraBold, Italic…) driving `Style` by expression | For each: Inspector appearance (what the rows show), does changing it change the weight, and what happens with an invalid style for a font (does the render fail?) |
| F3 | Pick the most robust variant, implement it in `build/make_macros.py` (all three text macros + UI Block), re-run it and describe the change | Weights visibly change for Open Sans (Light, Regular, Bold, ExtraBold); for Arial the Style list is valid; switching Font keeps the render working (no "Could not find font") |

## C. UTF-8 re-check (fix landed in 4e)
| # | Check | Pass criteria / report |
|---|---|---|
| U1 | Text macros with "éüÈ ÀBC" and "A😀B" and a 2-line text with accents (Letter / Word / Line) | The last frame's letters/words/lines are fully gone and the **slide finishes within 1–2 frames of the last frame** (was 3–4 frames early); last-frame alpha 0.00 |
| U2 | Regression: "SMK TEXT DEMO", "ONE TWO THREE", "HELLO", "A" on all three macros | As Phase 4d (alpha 0.00; slide ≤ 7 frames early) |
