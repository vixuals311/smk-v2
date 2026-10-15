# Phase 11 Gate — Products: Card Stack, Stat Card, Click Demo, style presets (run by Agent A)

`python scripts/install.py`, restart Resolve, **paste fresh** (new macros). **Scripting only.** Standard hygiene: deselect (`FlowView.Select()`) before each paste, comp rate = timeline rate, cold renders (Background +0.001),
readable graphs (distinct `flow:SetPos`, left→right, 2–3 units apart, clear names, one comp per check named after the check, a Note per group), `ProjectManager.SaveProject()`, project `SMK Phase11`.
Keep "SMK Test" untouched. Write `docs/PHASE11_RESULTS.md` (table: check, comp, result, evidence), push `phase11-results`, paste the table. NOT VERIFIED where not observed.
Shape sources are empty on frame 0 and the last frames: avoid those for single-frame checks. You may fix `build/make_macros.py` / `src/fuses/*.lua`; re-run `python build/build.py`, all `tests/test_*.py`, and describe each change.
All new macros are generated and unit-tested (wiring, published controls, **their expressions are executed in tests**); nothing below has run in Resolve yet.

## A. `SMK2_CardStack` — four cards, one set of controls, automatic stagger
Cards 2–4 follow card 1 (size, colours, border, shadow by link) and sit one pitch lower (`height + gap`); each card's Animator has Index 0–3 and mirrors the first animator's timing; Stagger Between Cards default 0.12 s.

| # | Check | Pass criteria / report |
|---|---|---|
| P1 | Paste fresh; defaults | No red node; 4 cards, text "Card 1…4", evenly spaced; cards appear one after another (stagger), in order, and leave in order |
| P2 | Change card 1 width/height/radius/colours/border/shadow; Gap 0 / 0.015 / 0.05; Stack Center X; First Card Y | All four follow; spacing = card height + gap (measure pitch in px); 1080p, 1080×1920, 4K identical in frame fractions |
| P3 | Edit Text 1–4, Font, Weight (all 8), Text Size, Text Color | Texts independent; font/size/colour/weight shared; weights render (no red node) |
| P4 | Stagger 0 / 0.12 / 0.3; In/Out engines (Spring, Elastic…); Enable Out; trimmed 46-frame clip | Starts differ by Stagger seconds; with Out on, the last frame is empty for **all four**; engines apply to all four |
| P5 | Cost cold 60 fps 300 frames; 1 and 3 stacks; node count | ms/frame; vs 4 separate `SMK2_UIBlock` |
| P6 | Save, full restart, reopen; two instances; no BezierSpline on published inputs | Pixel-identical; independent |

## B. `SMK2_StatCard` — card + counting number + caption
Number is computed by an expression (closed-form engine, the same as Text): `Prefix + format(Target × (1 − a)) + Suffix`, with Decimals 0/1/2 and a thousands separator. Count Delay/Duration/Engine are separate from the card's In/Out.

| # | Check | Pass criteria / report |
|---|---|---|
| T1 | Defaults | No red node; "12,480" counts up from 0 after 0.3 s over 1.4 s and **stops exactly on 12,480**; caption "Total users"; card appears |
| T2 | Target Value 0 / 7 / 999 / 1000 / 1,234,567 / 1,000,000; Decimals 0/1/2; Thousands on/off; Prefix `$`, Suffix `%`/`K` | Text exactly as formatted (report the string at the last frame) |
| T3 | Count Engine Ease / Spring / Bounce / Elastic / Overshoot / Inertia | Settles on the target for every engine; report max value reached (overshoot) and any negative value |
| T4 | Count Delay/Duration; card In/Out timing; Enable Out; 24/30/60 fps; trimmed clip | Counting times in seconds; number never changes after the count ends; card leaves on Out |
| T5 | Fonts and weights; number/caption size and colour; a very long value (e.g. 1,234,567,890) | No red node; text centred; report clipping |
| T6 | Cost cold 60 fps; 5 stat cards | ms/frame (text expressions are re-parsed per frame) |
| T7 | Save, full restart, reopen; two instances | Pixel-identical; independent |

## C. `SMK2_ClickDemo` — button + cursor that travels to it and clicks
Waypoint 2 of the `SMK2 Cursor` is an expression `Point(Card.CX, Card.CY)`, so the cursor always lands on the button; ripple on the click. The button does not react to the click (ripple only).

| # | Check | Pass criteria / report |
|---|---|---|
| D1 | Paste fresh; defaults | No red node; button appears; cursor fades in at "Cursor Start", moves to the button centre, clicks (ripple), fades out |
| D2 | Move Button Center X/Y and Width; render the arrival frame | Cursor tip lands within the button, at its centre (±2 px); the ripple is centred on the tip |
| D3 | **Does a Point expression on the Cursor's waypoint (OffsetControl) work?** and the macro-level `Cursor Start (drag in viewer)` crosshair | Yes/No; the crosshair appears in the viewer (UNVERIFIED by script: record what you can) |
| D4 | Cursor timing: Start Delay, Time To Reach The Button, Hold, Click Delay, Move Style Smooth/Snappy/Spring, Arc | Times in seconds; click at arrival + Click Delay |
| D5 | Does `UseFrameFormatSettings`/Width/Height on the Cursor produce a full-frame output at 1080p, vertical, 4K? | Output size correct, cursor positions identical in fractions |
| D6 | Cost, save/restart/reopen | As P5/P6 |

## D. Style presets
`SMK2_UIBlock`, `SMK2_CardStack`, `SMK2_StatCard`, `SMK2_ClickDemo` each have `_Glass`, `_Neon`, `_Soft` variants (same macro, different default fill/border/shadow/text colours).

| # | Check | Pass criteria / report |
|---|---|---|
| V1 | Paste every variant (12) | No red node; each appears in the Macros menu under SMK2 (report the list); looks distinct from the base (colour sample of fill/border/text) |
| V2 | Glass: fill 12 % white over a coloured background; Neon: cyan border + glow-coloured shadow; Soft: light card, dark text | As described; text readable (contrast ratio) on each |
| V3 | Node/graph and published-control counts equal to the base macro | Same |

## E. Open from Phase 10
| # | Check | Pass criteria / report |
|---|---|---|
| O2 | Look outline at 20 px, 1080p and 4K (rings now capped at 6, directions at 56) | ms/frame vs the Phase 10 figures (10.9 ms / 70.5 ms); serration still gone at 20 and 40 px? |

**For the user by hand:** whether the products look good, the Inspector layout of the long control lists, dragging the Click Demo cursor crosshair, viewer fps.
