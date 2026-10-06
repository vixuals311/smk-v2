# Phase 4d Gate — SMK Text last-frame alpha + open tests

**Fix (generated):** Out compensation in the Word and Line macros now uses the **last character** of the text (opacity is per character), so every
character is gone on the last frame. The last unit's slide may finish a few frames early (≤ 7 frames by the sandbox test; 13-character line ≈ 5).
`python scripts/install.py`, restart Resolve, **paste fresh**.

Hygiene: scripting only, deselect before paste, comp rate = timeline rate, cold renders (Background +0.001), readable graphs with distinct node
positions, clear names, one comp per check, note per group, `SaveProject()`, project `SMK Phase4d Gate`.

| # | Check | Pass criteria / report |
|---|---|---|
| R1 | **Last-frame alpha.** Word macro: "ONE TWO THREE", "HELLO", "A", "ONE TWO"; Line macro: 3-line text, "HELLO", "A", 2-line text; Letter macro: same texts | Per word/line/letter: motion start/finish frames and last-frame alpha. **Expect 0.00 for every one** (was 0.03–0.35). Report the max |
| R2 | Slide lag: frames between the last unit's slide finishing and the clip's last frame | ≤ 7 frames; report per case |
| R3 | **Other fonts and sizes** (open from Phase 4c): Open Sans Bold / Regular / Light, Arial, a condensed and a wide/serif font if installed; Size 0.04 / 0.08 / 0.15; Letter, Word, Line macros | Last-frame alpha per case (expect 0.00); any case with residue → report font, size, text |
| R4 | **Text edge cases** (open): double spaces, trailing space, trailing newline, empty text, a 60-character text, accents (é, ü), emoji | No red node / error; last-frame alpha 0.00; how the follower indexes each (report any mismatch with `#text`) |
| R5 | **Per-word alpha on a multi-line text in the Word macro** (open from Phase 4c) | Per-word last-frame alpha, 0.00 expected |
| R6 | **Motion smoothness proxy for the "does it look right" checks** (open): render every frame of In and Out for each of the six engines on the Letter macro, track one letter's centre (x, y) and opacity over time | Report per engine: peak overshoot, frame of settling, max frame-to-frame jump at the **end** of In and at the **start** of Out (should be small / no snap). Attach a contact sheet (every 2nd frame) per engine |
| R7 | **Slide directions** (open): for Slide Angle -90 / 90 / 0 / 180 on Letter, Word and Line macros, report the first-frame offset vector of one letter (px) and its direction in degrees | Direction = angle of the start offset; table |
| R8 | **Smoke test of all 7 macros** pasted fresh (UIBlock, ProgressRing, ProgressBar, TextLetter, TextWord, TextLine + Shape and Animator Fuses): no red node, render frame 0 / 12 / last | Pass/fail per macro; any error text |
| R9 | **Cost** 12 and 40 letters, cold, 60 fps, 300 frames | ≈ 25 ms / ≈ 75 ms expected; report |
| R10 | Save, full restart, reopen; frames pixel-identical | Same as Phase 4b |

**Still needs you (cannot be scripted):** (1) viewer playback fps with 12 and 40 letters (first play / cached); (2) does the default reveal and each
engine look right; (3) the Inspector layout of the Text control (multi-line box) and the colour swatches; (4) dragging a clip's trim handle on the
Edit page with a text macro; (5) the expanded group in the Nodes pane (readable?).
