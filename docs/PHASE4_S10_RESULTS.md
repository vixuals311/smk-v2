# Phase 4 spike S10 results: make SMK Text cheap again, auto letter count

Resolve Studio 21.1.0.14, Windows. Project `SMK Phase4 S10` (your `SMK Test` was not touched). Scripting only, no UI automation. No Fuse was changed and `build/make_macros.py` was **not** changed in this spike; the generator change the results point to is described in "Generator change" below, not landed. One comp per check, named `S10_Y*`, each with a Note above the graph and explicit node positions (Note y −3; Background x 0; macro group x 4; Merge x 8; MediaOut x 12). `FlowView.Select()` before every paste, `Comp.FrameFormat.Rate` set to the timeline rate (60), background changed by 0.001 before every timed render, `SaveProject()`.
Every timing: text "SMK TEXT DEMO" (13 characters, 11 letters, 2 spaces), 60 fps, 300 frames, 1080p PNG, Blur At Start 4, Letter Count 13, cold, first-to-last PNG time ÷ 299. Helper scripts in `docs/phase4_evidence/` (`h6.py`, `s10meas.py`, `y5meas.py`).
The best working comp is `S10_Y5_AutoCount`; its group settings are `docs/phase4_evidence/S10_Y5_TextLetter_chain_autocount.setting`, and the modified macro text I pasted for it is `S10_SMK2_TextLetter_auto_macro_variant.setting`.

## The answer

The cost was expression length, multiplied by how many times each long expression is evaluated per letter. Fusion does not cache a Calculation's result across the five nodes that each contain the full easing code. **Computing the amount once in one long Calculation and feeding the other outputs through linked Calculations (Y3) cuts 12 letters from 54–58 ms to 27.7 ms, with the same per-letter shifted look.** Adding the auto letter count (Y5) costs nothing: 28.0 and 28.4 ms. 40 letters drop from 237–245 ms to 112–124 ms.
Reading another tool's input value from a tiny expression (Y2) does see each letter's shifted time, but it is slower (79 ms), because every read re-evaluates the long expression.

## Summary

| # | Comp | Result |
|---|---|---|
| Y0 | `S10_Y0_Baseline` | New 5-Calculation macro: **57.9 and 53.5 ms/frame** (was 76.1 / 74.7 with 7 nodes). |
| Y1 | `S10_Y1_Trivial`, `S10_Y1_SpringOnly`, `S10_Y0_Baseline` | Cost scales with expression length: 120 chars 22.7 ms, 412 chars 32.8 ms, ~1,200 chars 53.5–57.9 ms. Parse or evaluation cost is confirmed. |
| Y2 | `S10_Y2_SharedAmt` | (i) YES, the tiny read sees the shifted time. (ii) **79.1 ms**: slower than five long expressions. |
| Y3 | `S10_Y3_Chain` | Linked chain is shifted per letter and costs **27.7 and 27.6 ms**. Operators needed: Multiply, and Subtract (Second − First) or Add for the "1 ±" terms (a second chained Calculation per output). |
| Y4 | `S10_Y4_SpringChain` | Spring-only amount in the chain: **22.7 ms**, against 27.7 for the six-engine amount. |
| Y5 | `S10_Y5_AutoCount` | Auto count works with `#UIT_Ctrl.Text.Value` (not `string.len(UIT_Ctrl.Text)`). Out finishes at the last frame with no manual Count. Follower Text accepts the expression. |
| Y6 | `S10_Y5_AutoCount` | Intact after a full quit and relaunch, no BezierSpline, two frames pixel-identical. |
| Y7 | `S10_Y5_AutoCount`, `S10_Y7_Best40` | 12 letters **28.0 and 28.4 ms** (target ≤ 30 met). 40 letters **124.2 and 111.7 ms**. |

## Y0 and Y1: baseline and expression length

All three use the same 5-Calculation macro (`UIT_Dist`, `UIT_Opacity`, `UIT_Scale` for size X/Y, `UIT_AngleZ`, `UIT_Blur` for softness X/Y). In Y1 every Calculation's expression is replaced by the same amount code `a` in a different length.

| Variant | Expression length (Opacity) | Cold ms/frame |
|---|---|---|
| (a) `S10_Y1_Trivial`: linear `a = max(0, 1 − (time − RenderStart)/12)` | 120 chars | 22.7 (single run) |
| (b) `S10_Y1_SpringOnly`: closed-form Spring only | 412 chars | 32.8 (single run) |
| (c) full six-engine + Out (`S10_Y0_Baseline`) | 1,211 chars | 57.9 and 53.5 |
| For comparison, the old 7-node macro (W14) | about 1,250 chars | 76.1 and 74.7 |

Roughly 0.035 ms per character per frame for 12 letters: 22.7 → 32.8 over 292 characters, 32.8 → 55 over about 800. Node count also matters (7 → 5 nodes: 75 → 56 ms).

## Y2: one shared amount read by tiny expressions

One long Calculation (a Calculation modifier on the unused follower input `MiterLimit1`) returns `a`. The five macro expressions are replaced by tiny ones that read its input value, for example `UIT_Ctrl.SlideDist*(Calculation1.FirstOperand)`.

| Question | Result |
|---|---|
| (i) Does the tiny expression see each letter's shifted time? | **YES.** Rendered letter opacities at frame 6 (Fade 0, Blur 0, no Out): 0.47 and 0.22 for the first two letters, the rest 0 (not started). The expected shifted Spring values are 0.47 for letter 1 and 0.22 for letter 2 (0.06 s into its motion). A letter-0-only evaluation would have shown the same value on every letter. |
| (ii) Cost | **79.1 ms/frame** (single run), worse than Y0 (53.5–57.9). Every read of `Calculation1.FirstOperand` re-evaluates the long expression, so five reads cost five evaluations plus the read overhead. |

## Y3: linked chain

`UIT_Amt` (one Calculation, long expression returning `a`) is linked into the others: `FirstOperand` is a **link** to `UIT_Amt`'s `Result` (not an expression), `SecondOperand` is a short expression, and `Operator` combines them.

| Output | Nodes | Operator(s) |
|---|---|---|
| Slide distance | 1: `UIT_Dist` = Amt × `SlideDist` | Multiply (value 2) |
| Rotation | 1: `UIT_AngleZ` = Amt × `Rot` | Multiply |
| Blur (both softness X and Y) | 1: `UIT_Blur` = Amt × `Blur` | Multiply |
| Opacity | 2: helper = Amt × (1 − Fade); `UIT_Opacity` = 1 − helper | Multiply, then Subtract (Second − First) (value 5) with SecondOperand 1 |
| Scale (both size X and Y) | 2: helper = Amt × (Scale − 1); `UIT_Scale` = helper + 1 | Multiply, then Add (value 0) with SecondOperand 1 |

Operator values are the menu positions starting at 0: 0 Add, 1 Subtract (First − Second), 2 Multiply, 5 Subtract (Second − First). The extra "+1 / 1 −" step needs a second chained Calculation for Opacity and Scale (no single operator does multiply-then-add). Total: 1 long + 3 single + 2 × 2 chained = 8 Calculation nodes, only one with a long expression.
Shifted per letter: **YES** (frame 6: letters 0.47 and 0.22, same as Y2 and the baseline). Values at letter 0 match the baseline (Opacity 0, 0.164, 0.47, 0.931 at frames 0, 3, 6, 12; blur 4 × a).
Cost: **27.7 and 27.6 ms/frame**.

## Y4: engine split

| Variant | Long expression length | Cold ms/frame |
|---|---|---|
| Linked chain, six-engine amount (`S10_Y3_Chain`) | 1,173 chars | 27.7 and 27.6 |
| Linked chain, Spring-only amount (`S10_Y4_SpringChain`) | 368 chars | 22.7 (single run) |
| Five own expressions, Spring-only (Y1b) vs full (Y0) | 412 vs 1,211 chars | 32.8 vs 53.5–57.9 |

With the chain the engine split saves about 5 ms (18%). With the five-own-expressions layout it saved about 21–25 ms. So a per-engine macro is worth little once the chain is in place: one macro with all engines is fine.

## Y5: auto letter count

Test macro: the shipped `SMK2_TextLetter.setting` text-edited (see `S10_SMK2_TextLetter_auto_macro_variant.setting`; generator not touched): (1) `UIT_Ctrl` gets a `Text` user control (`TextEditControl`, `LINKID_DataType = "Text"`); (2) follower `Text` is the expression `UIT_Ctrl.Text`; (3) the published Text control points to `UIT_Ctrl.Text`; (4) every `UIT_Ctrl.Count` in the amount expression is replaced by the count.

| Question | Result |
|---|---|
| Does follower `Text` accept the expression? | **YES.** The follower and Text+ show the text typed in the published control. |
| Count expression | **`#UIT_Ctrl.Text.Value`** works (13 for "SMK TEXT DEMO"). `string.len(UIT_Ctrl.Text)` and `tostring(...)` do not: inside a number expression `UIT_Ctrl.Text` is an input object, not a string; `.Value` is the string. |
| Words / lines | Word count `select(2, string.gsub(UIT_Ctrl.Text.Value, "%S+", ""))` gives 3 for "ONE TWO THREE" and 4 for "ONE TWO / THREE FOUR". Line count `select(2, string.gsub(UIT_Ctrl.Text.Value .. "\n", "\n", ""))` gives 1 and 2. Only the numbers were checked; the Out of the Word and Line macros was not rendered: NOT VERIFIED. |
| Does Out finish exactly at the last frame with no manual Count? | **YES.** "SMK TEXT DEMO" (11 letters): every letter alpha 0.0 on the last frame, last letter gone at frame 296. "ONE TWO THREE": same (last letter gone at 296). "HELLO" (5 letters, no change to any Count): last letter again gone at 296, all 0.0. So the Count adapts to the text with nothing to set. |
| How are spaces / line breaks indexed? | As characters. `#Text.Value` counts spaces and a line break as one character each ("ONE TWO\nTHREE FOUR" = 18), which is also how the follower indexes them for Order and Delay (S8: the first character of line 2 has index 8). So the character count equals the follower's index count, which is what the Out compensation needs. |
| Does the Inspector text box show in the published Text control? | The published `Follower_Text` is a `TextEditControl` in the group's input list (page Text). Whether the multi-line text box displays correctly in the Inspector: NOT VERIFIED (no UI automation, as requested). |

## Y6: save, quit, relaunch

`S10_Y5_AutoCount` (chain + auto count). After saving and a full quit and relaunch: follower connections identical (Vector, Calculation on CharacterAngleZ, CharacterSizeX/Y, Opacity1, SoftnessX1/Y1 and the three helper inputs), the follower `Text` expression and the amount expression (1,173 characters) intact, text "SMK TEXT DEMO", comp rate 60, no BezierSpline, and frames 6 and 285 re-rendered **pixel-identical**.

## Y7: best variant

| Text | Comp | Cold ms/frame |
|---|---|---|
| 12 letters, "SMK TEXT DEMO" | `S10_Y5_AutoCount` | **28.0 and 28.4** |
| 40 letters | `S10_Y7_Best40` (size 0.04, Stagger 0.02) | **124.2 and 111.7** |

For comparison: W14 was 75 and 237–245 ms; S9 X6 was 19–21 ms for 12 letters. 40 letters cost roughly 3.5–4 times the 12-letter figure for 3.1 times the letters. At 40 letters it is still above real time even at 24 fps (41.7 ms).

## Generator change (described, not landed)

To ship the Y3 + Y5 variant in `build/make_macros.py`:
1. Add a `UIT_Amt` Calculation node with `FirstOperand` expression = `text_expr("a")` (the long body, `return a`). I created it by script as a Calculation modifier on the unused follower input `MiterLimit1`; in the generator it would be a plain node, so whether an unconnected Calculation tool in a pasted `.setting` evaluates through links is NOT VERIFIED. (In the shipped macro the Calculations are only referenced through the follower inputs.)
2. Replace the five long expressions with linked Calculations: `UIT_Dist`, `UIT_AngleZ`, `UIT_Blur` = Operator 2 (Multiply), `FirstOperand` linked to `UIT_Amt.Result`, `SecondOperand` expression `UIT_Ctrl.SlideDist` / `UIT_Ctrl.Rot` / `UIT_Ctrl.Blur`. For Opacity and Scale add two helper Calculations (Multiply with `(1-UIT_Ctrl.Fade)` and `(UIT_Ctrl.Scale-1)`); `UIT_Opacity` = Operator 5 (Second − First) with SecondOperand 1 and FirstOperand linked to the helper; `UIT_Scale` = Operator 0 (Add) with SecondOperand 1.
3. For auto count: add a `Text` user control (`TextEditControl`) to `UIT_Ctrl`, set follower `Text` to the expression `UIT_Ctrl.Text`, publish `UIT_Ctrl.Text` instead of the follower `Text`, and replace `UIT_Ctrl.Count` with `#UIT_Ctrl.Text.Value` (Letter), `select(2, string.gsub(UIT_Ctrl.Text.Value, "%S+", ""))` (Word) or the line version (Line). Drop the manual "Letter Count" control.
The Word and Line macros were not rebuilt or timed with these changes.

## Other things to know

- Resolve hung (not responding) once more when I added a Calculation to an input that already had a macro Calculation connected and re-pointed connections in one script. I force-quit and relaunched it, deleted the half-built comp and rebuilt it, editing the existing Calculation tools in place and adding new Calculations only on unused follower inputs. Unsaved changes were lost.
- Y1 (trivial and Spring-only), Y2, Y4 are single timing runs; Y0, Y3, Y5 and Y7 are two runs.
- Setting a `UserControls` table on a macro-internal tool from a script did nothing (no error, no new input), so the Text control was added by editing the macro text instead.
