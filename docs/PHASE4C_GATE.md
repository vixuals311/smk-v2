# Phase 4c Gate — SMK Text Word / Line Out timing + per-unit stagger

Phase 4b (Z1–Z10) passed; **Z4 found**: with per-character delay, the Line macro's last line finished its slide/scale **44 frames before the clip end**
(Word macro 1–8 frames early). Fix (generated, `python scripts/install.py`, restart Resolve, paste fresh):
- **Stagger is now per unit** for Word and Line: the follower's per-character Delay is scaled by *units ÷ characters*, so "Stagger" ≈ seconds between words
  (lines) on average (defaults: Letter 0.04 s, Word 0.1 s, Line 0.2 s).
- **Out timing uses the last unit's own start index**, so the last word / line finishes on the last frame.
- Sandbox tests (43) check this for letter, word and line macros, including "A", "HELLO", "ONE TWO THREE" and 3-line text.

| # | Check | Pass criteria / report |
|---|---|---|
| Q1 | Paste `SMK2_TextWord`, `SMK2_TextLine`, `SMK2_TextLetter` fresh; no red node; letters animate | Load result |
| Q2 | Word macro: "ONE TWO THREE", "HELLO", "A", "ONE TWO" at defaults | First frame each word's motion starts; last frame the last word's motion finishes (expect ≈ 118–119, was 1–8 frames early); last-frame alpha of every word (expect 0.0) |
| Q3 | Line macro: 3-line text, "HELLO", "A", 2-line text | Start frame per line (expect ≈ 0.2 s apart); last frame each line finishes (expect last line ≈ 118–119, was 44 frames early); last-frame alpha per line (0.0) |
| Q4 | Stagger 0, 0.05, 0.3 on Word and Line | Spacing between words/lines scales with Stagger (seconds per unit, uneven by word length); no negative or stuck states |
| Q5 | Does the per-character fade inside a unit look natural (a quick wipe inside each word/line)? | Describe; screenshot at 3 frames |
| Q6 | Regression: Z3/Z5/Z6/Z7/Z8 (order, engines, angles; overshoot; fps; two instances; restart) and cost (12 letters ≈ 25 ms) | Same as Phase 4b |
