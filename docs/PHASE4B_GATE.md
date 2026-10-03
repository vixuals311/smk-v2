# Phase 4b Gate — SMK Text, chain version (re-verify in Resolve)

Changes from S10 (all generated; `python scripts/install.py`, restart Resolve, **paste fresh macros**, old instances keep the old graph):
- **One long amount expression** (`UIT_Amt`); every property is a tiny linked Calculation (Multiply; "Second − First" for opacity; Add for scale).
  S10 measured 28 ms/frame for 12 letters (was 75).
- **Auto count:** the Text control is now a multi-line text box on the holder (`UIT_Ctrl.Text`); the follower's Text is the expression
  `UIT_Ctrl.Text`; Out timing uses `#UIT_Ctrl.Text.Value` (characters). The manual "Letter Count" control is gone. Word and Line macros use the
  same character count, so their last word/line leaves slightly early (documented, safe).
- Scale control has a minimum of 0.01. Spring/Elastic/Overshoot can push opacity slightly above 1 for a few frames (no clamp in the chain).

Hygiene: deselect before paste, comp rate = timeline rate, cold renders, readable graphs, distinct positions, clear names, notes, one comp per check,
`SaveProject()`, project `SMK Phase4b Gate`. Scripting only (no UI automation).

| # | Check | Pass criteria / report |
|---|---|---|
| Z1 | Paste `SMK2_TextLetter`, `SMK2_TextWord`, `SMK2_TextLine` fresh. **Does an unconnected Calculation chain evaluate when it comes from a pasted .setting?** (S10 left this unverified) | No red node/dialog; letters animate. If the amount does not evaluate (letters static / all at offset) say exactly what you see |
| Z2 | Defaults + the Text control: type "HELLO", then a 3-line text; Inspector page "Text" | Text box is multi-line; changing it updates the letters and the Out timing; report what the Inspector shows (text box height, label) |
| Z3 | Regression of W2, W5, W6, W7, W8 (defaults, Order, six engines, slide angles, scale/rotation/blur) | Same as Phase 4 |
| Z4 | Out with auto count: "SMK TEXT DEMO", "ONE TWO THREE", "HELLO", "A", and a 3-line text; letter, word, line macros | Last-frame alpha of every letter/word/line (expect 0.0); first frame of Out; for Word/Line macros how early the last unit finishes |
| Z5 | Scale At Start 0 (clamped to 0.01?), Fade 0.5, Spring/Elastic overshoot | Any flicker/brightening (alpha > 1) or errors? Report max alpha |
| Z6 | 24/30/60 fps comps (rate = timeline), pixel-identical at equal seconds | Same as W11 |
| Z7 | Two instances (copy-paste + renamed) | Independent; the copy's expressions point at its own `UIT_Ctrl_1` |
| Z8 | Save, full restart, reopen | Unchanged, no BezierSpline, pixel-identical |
| Z9 | Cost, 12 and 40 letters, cold 60 fps ms/frame; user: viewer fps first/cached | Report; S10 target ≈ 28 ms (12 letters), ≈ 112–124 ms (40 letters) |
| Z10 | Merge over SMK2_UIBlock: edges, no dark fringe (W16) | Same as W16 |
