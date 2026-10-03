# Phase 4 spike S9 — cheap per-letter animation (native expressions, Vector modifier, softness)

**Why:** S8 E9 showed each Fuse modifier bound to a follower input costs ≈ 2.5–3 ms **per letter per frame** (12 letters × 3 inputs ≈ 107 ms/frame
vs 5.4 for a bare follower). The Neo Text Engine's follower setup (read for ideas only) shows two things we missed:
1. **Position:** `CharacterOffset` (a Point) is bound to a Fusion **`Vector`** modifier's `Position` output (`Vector` tool: Origin, Distance, Angle);
   the animated value is `Vector.Distance` (a Number), angle sets the slide direction.
2. **Enables:** the follower sets `TransformRotation = 1`, `TransformSize = 1`, and `Softness1..8 = 1` (the Softness nest toggles) before
   `SoftnessX1/Y1` take effect — probably why blur showed nothing in S8.
Neo drives these with BezierSplines (cheap, but keyed in frames, so it ships 30 fps + 60 fps copies). We want the fps-independent, live-editable,
cheap version: **native expressions that read `time`** on the bound inputs.

Install: `python scripts/install.py`, restart Resolve. Rules as before (readable graph, distinct positions, names, notes, one comp per check
`S9_xx`, deselect before paste, `ProjectManager.SaveProject()`, project `SMK Phase4 S9`, comp rate = timeline rate, cold renders: change the
Background by 0.001). Script-only; no Fuse changes. "ONE TWO THREE FOUR" at 24 fps, follower Delay 2 frames, Order 0, TransformSize on.

| # | Question | How / report |
|---|---|---|
| X1 | **Does an expression on a follower input see the letter's shifted time?** Set `Opacity1` (bound as the Neo way, i.e. the input exposed as a Number modifier you can put an expression on, or the input itself) to the expression `time / 24` (or `math.min(1, time/24)`), per letter | Render letter opacities at frame 12: if each letter shows a different value → `time` is shifted per letter (YES). If all equal → expressions do not see the offset. Report both numbers |
| X2 | If X1 = no: try (a) a `Calculation`/`Expression` built-in modifier chain, (b) a hand-keyed BezierSpline with 2 keys (frame 0→24) bound to Opacity1, (c) `SetExpression` on the modifier's output. Which of them is shifted per letter? | Table: method → shifted? → cost |
| X3 | **Easing in one expression:** use an immediately-invoked function in an expression, e.g. `(function() local t = ... return ... end)()` with a spring/overshoot/bounce closed form, using `comp:GetPrefs("Comp.FrameFormat.Rate")` for seconds. Does Fusion accept multi-statement/IIFE expressions? Max length accepted? | Report errors verbatim; test expression ≈ 400 characters |
| X4 | **Vertical slide:** add a `Vector` modifier (`AddModifier("CharacterOffset", "Vector")` or via GUI), set Angle 90 (up) / 270, drive `Vector.Distance` with the X1/X3 expression, per letter | Letters slide up by a staggered amount? Report render positions (px) per letter at 3 frames; also the same via an X-direction (Angle 0). Units of Distance (fraction of frame width?) |
| X5 | **Blur:** set `Softness1 = 1` (enable) then drive `SoftnessX1`/`SoftnessY1` with an expression (not zero) | Do letters visibly blur? Per-letter staggered? Report blur radius in px (measure edge softness) and which enables were needed. Also try `Softness1..8` all 1 |
| X6 | **Scale/rotation/opacity together** on one follower (CharacterSizeX/Y, CharacterAngleZ, Opacity1, Vector.Distance, SoftnessX/Y1) each with its own expression | One render with all five staggered; report cost (ms/frame cold, 60 fps comp rate, 12 letters, 300 frames) vs S8 E9 (1 modifier 33 ms, 3 modifiers 107 ms) |
| X7 | **fps independence:** same comp at comp rate 24 and 60 with Delay in seconds converted by `0.05*comp:GetPrefs("Comp.FrameFormat.Rate")` and expressions using seconds | At equal seconds, letter states identical (± 1/255)? |
| X8 | **Out phase:** expression with Out starting at `(RenderEnd-RenderStart+1)/rate - outDur` (use `comp.RenderEnd`, `comp.RenderStart` in an expression) | Letters leave in stagger order and all are gone by the clip end? (Last letter's time is shifted: report whether Out must be compensated by `(N-1)*delay`) |
| X9 | **Word and line units:** repeat X1/X4 with the Word-level and Line-level follower inputs (CharacterX → WordX → LineX names from your E1 table) | Word/line stagger works with the same expressions? |
| X10 | Save → full restart → reopen | Expressions/links intact, no BezierSpline created, pixel-identical |
| X11 | Fallback measurement: the same 12-letter text with a 2-key BezierSpline on Opacity1 and on Size (Neo's way) | ms/frame cold; this is the speed we have to match |

Write `docs/PHASE4_S9_RESULTS.md`; commit the saved `.setting` of the best working comp under `docs/phase4_evidence/`; push to branch
`phase4-s9-results`; paste the tables in chat. NOT VERIFIED where not observed.
