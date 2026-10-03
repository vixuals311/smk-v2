# Phase 4 spike S9 results: cheap per-letter animation with native expressions

Resolve Studio 21.1.0.14, Windows. Project `SMK Phase4 S9` (your `SMK Test` was not touched). Scripting only: no Fuse was changed. One comp per check, named `S9_X*`. Each has a Note above the graph and explicit node positions (Note y −3; Background x 0; Text+ x 4; Merge x 8; MediaOut x 12; one row per Text+). `FlowView.Select()` before every add, project saved with `SaveProject()`, and the background changed by 0.001 before each timed render. 60 fps comps (`S9_X6_AllTogether`, `S9_X11_SplineFallback`, `S9_X2_Calc3`) are 60 fps timelines with `Comp.FrameFormat.Rate` set to 60 explicitly. Everything else is 24 fps.
Helper scripts: `docs/phase4_evidence/h4.py` (builder), `s9meas.py` (measurement). Best working comp, saved as Text+ settings: `docs/phase4_evidence/S9_X6_TextPlus_follower_expressions.setting`.

## The answer

**Yes, it works, and it is cheap, but only if the expression lives inside a modifier.** An expression typed straight onto a follower input is ignored by the render. The same expression inside a built-in `Calculation` modifier connected to that input is evaluated with each letter's own shifted time. Seven `Calculation` modifiers (size X/Y, rotation, opacity, offset distance, blur X/Y) cost 19–21 ms/frame at 60 fps for 12 letters, against 107 ms for three `SMK2_Motion` modifiers in S8 E9. Splines are cheaper still (6.1 ms for three).

## Summary

| # | Comp | Result |
|---|---|---|
| X1 | `S9_X1_TimeShift` | Expression directly on the input: all letters equal (no effect). Expression inside a `Calculation` modifier: different per letter (shifted). Numbers below. |
| X2 | `S9_X1_TimeShift`, `S9_X2_Calc3`, `S9_X11_SplineFallback` | `Calculation` shifted: yes. 2-key `BezierSpline` shifted: yes. Expression on the input itself: no. |
| X3 | `S9_X1_TimeShift` | A multi-statement IIFE expression is accepted and evaluates. Length limit about 2,300 characters. |
| X4 | `S9_X4_VectorSlide` | `Vector` modifier on `CharacterOffset` works. Letters slide up (Angle 90) or sideways (Angle 0), staggered. Units measured. |
| X5 | `S9_X5_Blur` | Blur works and is staggered, but needs values of about 1 or more (S8 used 0.05). No extra enable beyond `Softness1` = 1 (the default). |
| X6 | `S9_X6_AllTogether` | Five effects (size, rotation, opacity, offset, blur) together and staggered. **19–21 ms/frame**. |
| X7 | `S9_X7_Rate24`, `S9_X6_AllTogether` | Pixel-identical at equal seconds (0.25 s, 24 fps frame 6 vs 60 fps frame 15). |
| X8 | `S9_X8_OutPhase` | Out works with `comp.RenderEnd`. Without compensation the last letters do not leave. With `(N−1)×Delay` compensation they leave in stagger order. |
| X9 | `S9_X9_WordLine` | Word and line units work with the same expressions. |
| X10 | `S9_X6_AllTogether` | Connections and expressions intact after a full quit and relaunch, frame pixel-identical. |
| X11 | `S9_X11_SplineFallback` | 6.1 ms/frame (single run). |

## X1: letter opacities at frame 12

Text "ONE TWO THREE FOUR", follower Delay 2 frames, Order 0. Expression `math.min(1, time/24)`. If the expression sees each letter's shifted time, the opacity of letter *i* at frame 12 is (12 − 2i)/24. Opacity is measured as the peak brightness of each letter in the render, relative to full white.

| Method | O | N | E | (space) | T | W | O | later letters | Differ letter to letter? |
|---|---|---|---|---|---|---|---|---|---|
| Expected if shifted | 0.50 | 0.42 | 0.33 | n/a | 0.17 | 0.08 | 0 | 0 | |
| Expression set directly on `Opacity1` | 1.00 | 1.00 | 1.00 | n/a | 1.00 | 1.00 | 1.00 | 1.00 | **No** (not applied; if the expression were seen unshifted, all would be 0.50) |
| Expression in a `Calculation` modifier on `Opacity1` | 0.50 | 0.41 | 0.33 | n/a | 0.17 | 0.08 | 0 | 0 | **Yes** |
| 2-key `BezierSpline` (frame 0→24) on `Opacity1` | 0.50 | 0.41 | 0.33 | n/a | 0.17 | 0.08 | 0 | 0 | **Yes** |

Related finding: a **static** value typed into a follower input (for example `Opacity1 = 0.2`, `CharacterSizeX = 0.5`, `CharacterSpacing = 2`) has no effect on the render either. The follower only applies inputs that are connected to a modifier (spline, Calculation, Vector, Fuse). This explains why S8 saw no effect from static `CharacterOffset` values.

## X2: which methods are shifted per letter

| Method | Shifted per letter? | Cost (12 letters, 60 fps, 300 frames, cold) |
|---|---|---|
| (a) `Calculation` modifier with the expression on `FirstOperand` (`SecondOperand` 0, `Operator` 0) | **Yes** | 3 modifiers (Opacity1, Size X/Y): 12.6 ms/frame (`S9_X2_Calc3`, single run). 7 modifiers: 19–21 ms (X6). |
| (b) 2-key `BezierSpline` | **Yes** | 3 splines: 6.1 ms/frame (`S9_X11_SplineFallback`, single run) |
| (c) expression set on the follower input itself | **No** (input ignored) | not applicable |
| Not tried | `Offset`, `Probe`, `Perturb`, `Publish` and others. A loop trying several modifier names hung Resolve and I had to kill it, so I did not test them one by one. | |
| For comparison (S8 E9) | `SMK2_Motion` Fuse modifier | 1 bound: 31.5–33.2 ms, 3 bound: 107 ms |

## X3: easing in one expression

- A multi-statement IIFE expression is accepted: `(function() local r = comp:GetPrefs("Comp.FrameFormat.Rate"); ... return v end)()`. The 646-character test (spring closed form, overshoot and bounce terms, `math.exp`, `math.cos`, `math.sin`) evaluated without error (values 0, 1.0, 0.97, 1.0 …).
- `comp:GetPrefs("Comp.FrameFormat.Rate")` works inside an expression.
- **Maximum length: about 2,300 characters.** An IIFE of 2,246 characters evaluated; 2,345 and longer did not (the value reads back as nil; `SetExpression` itself does not raise an error).
- Other failure behaviour: `SetExpression` never raised for a bad expression (`(function() return time/24 ` with no `end`, a call to an undefined function, a bare `return time/24`); the modifier simply returned nil. There is no verbatim error text to report; I did not find where Fusion logs it.
- Not usable inside expressions: `comp:GetAttrs()` returns nil. Use the fields `comp.RenderStart` and `comp.RenderEnd` (verified 0 and 119).

## X4: vertical slide with a `Vector` modifier (`S9_X4_VectorSlide`)

`AddModifier("CharacterOffset","Vector")` works (the Vector's `Position` output feeds the point). `Distance` is driven by a `Calculation` whose `FirstOperand` has the expression. Set `Origin` to (0,0), otherwise the letters leave the screen.

| Test | Result |
|---|---|
| Angle 90, `Distance = 0.2*(1 − min(1, time/24))` | Letters slide up and settle on their rest line (cap top at y = 515 px). Letter *i* sits 57 px higher than letter *i−1* at the same frame (frame 24: A at 515, B 458, C 401, D 345). Staggered: yes. |
| Angle 0, `Distance = 0.05*(1 − …)` at frame 12 | Letters shift right: A +48, B +56, C +64 … H +104 px relative to rest, in steps of 8 px (= 0.00417 × 1920). |
| Units | **Horizontal: 1.0 of Distance = 1920 px (one frame width at 1080p).** Vertical (Angle 90): 3,420 px per unit (= 1920 × 1.78) because `Vector.ImageAspect` defaults to 1.778. Set `ImageAspect` = 1 to get equal units on both axes. Dependence on text size NOT VERIFIED. |

## X5: blur (`S9_X5_Blur`)

`SoftnessX1` and `SoftnessY1` each driven by a `Calculation` expression `k*(1 − min(1, time/24))`. Softness edge width = pixels between the 5% and 50% intensity points.

| Value of k | Result |
|---|---|
| 0.03 (like S8's 0.05) | No visible blur at all |
| 3 | Visible blur, staggered per letter at frame 12 (letters 1–5 edge width ≈ 4, 4.5, 5, 7, 8.5 px, rising for later letters; peak intensity falls from 229 to 222). Image: `S9_X5_blur_f12.png` |

Enables: `Softness1 = 1` (the default) was enough. Setting `SoftnessOnFillColorToo1` to 1 or 0 gave identical results. I also set `Softness1..8` to 1 for the test. So the S8 "no blur" came from values that were too small, not from a missing enable.

## X6: everything together (`S9_X6_AllTogether`)

12 letters "ABCDEFGHIJKL", 60 fps, comp rate 60, Delay = expression `0.05 * rate` (3 frames). Each of `CharacterSizeX`, `CharacterSizeY`, `CharacterAngleZ`, `Opacity1`, `SoftnessX1`, `SoftnessY1` has a `Calculation` modifier; `CharacterOffset` has a `Vector` (Angle 90, `ImageAspect` 1) whose `Distance` has one more `Calculation`. Total 7 `Calculation` + 1 `Vector`. Expression: `P = min(1, max(0, time / rate / 0.5))` (0.5 s ease), rotation −45°·(1−P), distance 0.03·(1−P), blur 3·(1−P). Image at frame 20: `S9_X6_all_together_f20_60fps.png` (letters rotating, scaling, fading, blurring and rising one after another).

| Variant | ms/frame (cold, 300 frames, 60 fps) |
|---|---|
| X6: 7 `Calculation` + 1 `Vector` | **18.9 and 20.6** |
| X2 comparison: 3 `Calculation` | 12.6 (single run) |
| X11: 3 `BezierSpline` | 6.1 (single run) |
| S8 E9: 1 `SMK2_Motion` | 31.5–33.2 |
| S8 E9: 3 `SMK2_Motion` | 107.2–107.5 |
| S8 E9: static / follower with nothing bound | 5.6 / 5.4 |

## X7: fps independence

Same graph at comp rate 24 (`S9_X7_Rate24`) and 60 (`S9_X6_AllTogether`), Delay and expressions in seconds via `comp:GetPrefs("Comp.FrameFormat.Rate")`. Compared at 0.25 s (24 fps frame 6, 60 fps frame 15), full 1080p frames: **maximum difference 0 on every channel** (pixel-identical). Only that one time point was compared.

## X8: Out phase (`S9_X8_OutPhase`)

8 letters, 24 fps, 120 frames, Delay 2.4 frames. `Opacity1` = In (0.5 s) × (1 − Out), where Out starts at `n − d − compensation` (`n = comp.RenderEnd − comp.RenderStart + 1`, `d` = 0.5 s in frames). Frames at which each letter's Out starts and when it reaches 0:

| Row | Out start per letter (1 to 8) | Gone at | Opacity at frame 119 |
|---|---|---|---|
| Uncompensated | 109, 111, 114, 116, 119, none, none, none | none by 119 | 0.08, 0.28, 0.48, 0.68, 0.88, 1.0, 1.0, 1.0 |
| Compensated by `(N−1)*Delay` = 7 × 2.4 | 92, 95, 97, 99, 102, 104, 107, 109 | 103, 106, 108, 111, 113, 115, 118, none | 0 for letters 1–7, 0.08 for letter 8 |

Yes: Out must be compensated by (N−1)×Delay, and then the letters leave in stagger order. The last letter is almost, but not quite, gone on the very last frame (0.08), so use a slightly larger compensation (about one frame more) to be fully clear. The first letter then leaves (N−1)×Delay earlier than a plain clip-end Out would.

## X9: word and line units (`S9_X9_WordLine`)

Word-level `WordSizeX/Y` and `WordOffset` (via `Vector`), and line-level `LineSizeX/Y` and `LineOffset`, with the same `Calculation` expressions. Delay 2 frames, Order 0.

| Unit | Result |
|---|---|
| Word, "ONE TWO THREE FOUR" | Words start at frames 1, 9, 17, 29 (expected 0, 8, 16, 28 = 2 × first-character index 0, 4, 8, 14). Staggered: yes. |
| Line, "ONE TWO / THREE FOUR" | Line 1 starts at frame 1, line 2 at frame 20 (first character of line 2 is index 8: 16 frames + threshold). Staggered: yes. |
| Word and line offset | Both `Vector` bindings accepted and evaluate (0.015 at frame 12). Rendered offset for word and line: NOT VERIFIED. |

There is no word- or line-level opacity or blur input (opacity and softness exist only per shading element).

## X10: save, quit, relaunch

`S9_X6_AllTogether` (8 modifiers). After saving and a full quit and relaunch, the connection map of the follower was identical (`CharacterAngleZ`, `CharacterSizeX/Y`, `Opacity1`, `SoftnessX1/Y1` → `Calculation`, `CharacterOffset` → `Vector`, `Vector.Distance` → `Calculation`), the Delay expression was intact, the comp rate was still 60, no `BezierSpline` was created, and frame 15 re-rendered **pixel-identical** to the render before the restart. Settings file: `S9_X6_TextPlus_follower_expressions.setting`.

## X11: fallback speed

12 letters, 60 fps, 2-key `BezierSpline` (frame 0 → 30) on `Opacity1`, `CharacterSizeX`, `CharacterSizeY`: **6.1 ms/frame** (single run), against 5.4 for the bare follower. This is the speed to match; the 3-Calculation version is about twice that (12.6) and the full 7-Calculation version about 3×.

## Other things to know

- Resolve hung (not responding for more than 5 minutes) when I added several different modifier types to one input in a loop; I force-quit and relaunched it. Unsaved comps were lost, so I rebuilt them.
- Each timed result is one or two runs.
- Not checked: whether the Inspector shows these bindings as linked, and the effect of text size on the vertical Distance units.
