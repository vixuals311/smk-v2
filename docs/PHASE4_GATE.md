# Phase 4 Gate — SMK Text (letter / word / line reveal)

New generated macros: `SMK2_TextLetter`, `SMK2_TextWord`, `SMK2_TextLine` (`python scripts/install.py`, restart Resolve).
Built from S8/S9 findings: **Text+ → StyledTextFollower**, each animated follower input bound to a built-in **Calculation** (or **Vector**
for position) modifier whose expression reads `time` (so each letter sees its own delayed time). No Fuse modifiers, no scripts. Easing is
closed-form Lua inside the expression (Ease, Spring, Bounce, Elastic, Overshoot, Inertia), seconds-based and clip-relative
(`comp.RenderStart/RenderEnd`). All controls live on an unconnected holder node (`UIT_Ctrl`) so the graph is acyclic.
Out phase starts earlier for the whole word so the last letter finishes at the clip's last frame (set **Letter Count** = number of
letters/words/lines for correct Out timing; auto-count is deferred).

Pages: Text (text, font, size, colour, position), Motion (delay, duration, stagger, engine, spring/overshoot, Order), Look (opacity, slide distance+angle, scale, rotation, blur at start), Out.

**Test hygiene:** deselect (`FlowView.Select()`) before each paste; comp frame rate must equal the timeline rate (set `Comp.FrameFormat.Rate`);
cold timings (change Background by 0.001); readable graphs, distinct positions, clear names, notes, one comp per check, `SaveProject()`.

| # | Check | Pass criteria / report |
|---|---|---|
| W1 | Paste `SMK2_TextLetter` fresh; no red node / dialog | Loads; exact error otherwise (generator bug → fix `build/make_macros.py`, describe change) |
| W2 | Defaults | White bold "SMK Text", letters rise (slide up 3 % of width) with fade-out→in? **Note:** default Fade 0 → letters fade in, spring ease, 0.04 s stagger left→right; Out at the end; no console errors |
| W3 | Edit the **Text** control (type "HELLO WORLD") | Text updates; Font, Size, Text Color (swatch group) work; Position moves it |
| W4 | Letter / Word / Line macros with "ONE TWO THREE FOUR" (two lines) | Each animates by its unit; report word/line start frames; Stagger per character is documented |
| W5 | Order: Left→Right, Right→Left, Inside Out, Outside In, Random One by One, Completely Random | Behave as in S8 E4 |
| W6 | Engines: all six (Ease, Spring, Bounce, Elastic, Overshoot, Inertia) | Distinct, settle, no jump; Spring may overshoot |
| W7 | Slide Angle -90 (up), 90 (down), 0, 180; Slide Distance 0 / 0.03 / 0.2 | Direction = direction of the **start offset** (-90 means letters start below and rise); same on 9:16 |
| W8 | Scale At Start 0 / 0.5 / 2, Rotation At Start ±30, Blur At Start 0 / 4 / 10, Fade 0 / 0.5 | Each alone and combined staggered per letter; blur visible and clean at 0 when settled |
| W9 | Out: Enable Out on/off, Out Duration, Out Offset, Letter Count = actual count | Letters exit in order; **every letter fully gone on the last frame**; report the last-frame alpha per letter |
| W10 | Trim the clip on the Edit page (drag a handle) | Out follows the new end; In unaffected |
| W11 | 24 / 30 / 60 fps comps (comp rate = timeline rate) | Same look at equal seconds (± 1/255) |
| W12 | Two instances (one copy-paste, one renamed) | Independent; no cross-talk |
| W13 | Save, close, full restart, reopen | Unchanged; no BezierSpline; pixel-identical |
| W14 | Cost: 12 letters, 40 letters, cold render ms/frame at 60 fps; viewer first-pass / cached fps (user) | Report; target ≈ S9 X6 (≈ 19–21 ms for 12 letters); does it grow with letter count? |
| W15 | Expand the group: graph readable (Text, Follower, Vector, 7 Calculation nodes, Ctrl holder) | Yes/no + screenshot; Inspector shows published controls on the group |
| W16 | Merge `SMK2_TextLetter` over `SMK2_UIBlock` or a Background, check alpha/edges | No dark fringe on blurred letters; premultiplied sane |
