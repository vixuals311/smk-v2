# Phase 4 spike S10 — make SMK Text cheap again; auto letter count

**Findings so far (Phase 4 gate):** `SMK2_TextLetter` works (W1–W16), but costs **75 ms/frame for 12 letters** and 240 ms for 40 letters
(cold, 60 fps), vs 19–21 ms for the S9 X6 proof (7 Calculation modifiers, ~120-character expressions). Hypothesis: Fusion re-parses each
Calculation's expression for every letter on every frame, and ours are ~1250 characters each (full easing engine). A generator change already
done (this commit): 7 → **5** Calculation nodes (one feeds both Size X/Y, one feeds both Softness X/Y). Test the rest here.
Script-only; follow the readable-graph / hygiene rules (comp rate = timeline rate, cold renders, distinct node positions, one comp per check
`S10_Yx`, `SaveProject()`, project `SMK Phase4 S10`). Use the 12-letter text "SMK TEXT DEMO", 60 fps, 300 frames, Blur At Start 4 as in W14.

| # | Question | How / report |
|---|---|---|
| Y0 | Baseline with the new 5-node macro: W14 again | `SMK2_TextLetter` 12 letters cold ms/frame (was 76.1 / 74.7) |
| Y1 | **Is it expression length?** Same macro, replace each of the 5 expressions with (a) the trivial `time/24`-style ~120-char expression, (b) a ~500-char Spring-only version, (c) the full ~1250-char one | Cold ms/frame for each. If cost scales with length → parse cost confirmed |
| Y2 | **Share one amount.** One Calculation `UIT_Amt` holds the long expression (computes the amount a); the other four use tiny expressions that read it, e.g. `UIT_Amt.FirstOperand`: (i) does a tiny expression reading another tool's *input value* see the **letter's shifted time** (compare letter opacities at a frame with Delay 2: differ per letter?), (ii) cost | Report (i) YES/NO with the per-letter numbers, and ms/frame |
| Y3 | If Y2(i) = NO: **linked chain**: `UIT_Amt` (long expr) → a second Calculation whose FirstOperand is a *link* to `UIT_Amt.Result` (SourceOp/Source, not an expression) with Operator Multiply and SecondOperand a short expression (e.g. `UIT_Ctrl.SlideDist`) → bound to the follower input | Shifted per letter? Cost? (Opacity/Scale need `+1`: report whether a second chained Calculation with Operator Add is needed, or Calculation offers a better operator) |
| Y4 | **Engine split.** Cost of a Spring-only expression (~500 chars) vs the combined 6-engine expression (~1250) at equal node counts | Tells us whether shipping one macro per engine/family is worth it |
| Y5 | **Auto count.** Put a text holder on `UIT_Ctrl` (user control `INPID_InputControl = "TextEditControl"`, `LINKID_DataType = "Text"`), bind follower `Text` as an expression `UIT_Ctrl.Text`, and compute Letter Count in the Out expression as `string.len(UIT_Ctrl.Text)` (letters, with spaces — verify how the follower indexes spaces) / `select(2, string.gsub(t, "%S+", ""))` (words) / lines | Does the follower Text accept the expression? Does the Out finish exactly at the last frame with no manual Count for "ONE TWO THREE" and "SMK TEXT DEMO"? Does the Inspector text box show in the published Text control? How are spaces / line breaks indexed by Order and Delay? |
| Y6 | Save → full restart → reopen the best variant | Intact, no BezierSpline, pixel-identical |
| Y7 | Best variant, 12 and 40 letters, cold 60 fps ms/frame | Target ≤ 30 ms for 12 letters |

Write `docs/PHASE4_S10_RESULTS.md` with the tables, commit the best working comp's `.setting` under `docs/phase4_evidence/`, push to branch
`phase4-s10-results`, paste the tables in chat. NOT VERIFIED where not observed. If a variant needs a generator change in
`build/make_macros.py`, describe the change (don't land it as the only record).
