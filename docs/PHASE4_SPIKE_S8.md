# Phase 4 spike S8 — Text+ StyledTextFollower inputs, per-letter binding, seconds-based delay

**Goal:** learn the real input IDs of the follower and prove the plan for `SMK Text` (letter / word / line stagger driven by `SMK2 Motion`)
before any macro is generated. Script-only work; no Fuse changes. (Phase 0 S2 already showed a Follower re-evaluates a modifier per character.)

Setup: `python scripts/install.py`, restart Resolve. 24 fps comp, 120 frames, 1920×1080, Text+ with "SMK TEXT DEMO".
Follow the readable-graph rules (distinct node positions, clear names, one comp per check named `S8_xx`, notes, `ProjectManager.SaveProject()`,
deselect before paste, project `SMK Phase4 S8`).

| # | Question | How / report |
|---|---|---|
| E1 | Add a follower: `text:AddModifier("StyledText", "StyledTextFollower")` (or the GUI path). List **every** follower input: `mod:GetInputList()` → ID, display name, data type, default, page/group, min/max if available | Paste the full table into the results doc. I especially need the IDs for: Order, Delay (and the delay-type / unit menu: letter, word, line), Position/Center X/Y, Size, Rotation, Opacity, Blur/Softness, Spacing, and the "enable" checkboxes (e.g. TransformSize, TransformRotation) |
| E2 | Export: `text:SaveSettings("<path>.setting")` after adding the follower and binding a modifier (E3). Commit the file's text to `docs/phase4_evidence/` | Shows how the follower, its bindings and the Text+ link are serialized |
| E3 | Bind `SMK2 Motion` (Fuse modifier) to each animatable follower input: Opacity, Size, vertical position, rotation (one at a time and together). `input:ConnectTo(motion.Output)` or `AddModifier("Opacity1","Fuse.SMK2_Motion")` | Does each accept it? Per letter, are the letters visibly staggered by the follower Delay? Report the `[req.Time]` offsets if you can log them, and the rendered letter-by-letter result at several frames |
| E4 | Units: Order values (what does each number mean: left→right, right→left, centre-out, edges-in, random…), and the unit menu (per letter / word / line) | Table: ID value → behaviour, verified by rendering "ONE TWO THREE" |
| E5 | Delay units: Delay = 2 at a 24 fps comp vs a 60 fps comp (Comp.FrameFormat.Rate) | Delay is in frames? Does an expression work: `Delay = Input { Expression = "0.05 * comp:GetPrefs(\"Comp.FrameFormat.Rate\")" }` set by script (`input:SetExpression`)? |
| E6 | Offset semantics: with Motion In Duration 0.5 s and follower Delay giving 0.1 s per letter, do letters start 0.1 s apart and each run a full 0.5 s? Does the last letter finish its Out phase before the clip end (Motion Out follows the clip end via `Comp.RenderEnd`)? | Report the first/last frame of motion for letter 1 and the last letter, In and Out |
| E7 | Save, close, full restart, reopen | Connections intact, no BezierSpline created on follower inputs, renders pixel-identical |
| E8 | Per-letter blur / colour / tracking if the follower exposes them | Report which ones exist and whether the modifier can drive them |
| E9 | Cost: 12-letter text with one follower + 2–3 bound Motion modifiers: render ms/frame cold vs the same Text+ static | Report (we expect ≈3 ms per bound modifier) |

Write `docs/PHASE4_S8_RESULTS.md` (tables above), push to branch `phase4-s8-results`, paste the tables in chat. NOT VERIFIED where not observed.
