# Phase 9 Gate — SMK2 Bloom (multi-pass pyramid glow) (run by Agent A, the only agent that drives Resolve)

`python scripts/install.py`, restart Resolve. **Scripting only.** Hygiene: deselect (`FlowView.Select()`) before each paste, comp rate = timeline rate, cold renders (Background +0.001),
readable graphs (distinct `flow:SetPos` positions, left→right, 2–3 units apart, clear names, one comp per check named after the check, a Note per group), `ProjectManager.SaveProject()`, project `SMK Phase9`.
Keep "SMK Test" untouched. Write `docs/PHASE9_RESULTS.md` (table: check, comp, result, evidence), push `phase9-results`, paste the table. NOT VERIFIED where not observed.
Remember the Shape source is empty on frame 0 and the last frames: single-frame checks must avoid them. You may fix `src/fuses/SMK2_Bloom.lua` / `src/core/smk_bloom.lua`; re-run build + tests and describe changes.

**SMK2 Bloom** (Effects ▸ Fuses ▸ SMK v2 ▸ SMK2 Bloom): image in → image out; 8 GPU passes (extract + 5 downsamples + one composite) through 6 intermediate images; glow from Alpha or Brightness,
radius px@1920 (4–400), intensity, spread (gamma), colour, behind / additive / glow-only, opacity; output window padded by 1.3 × radius + 2 (`IMG_DataWindow`). The pipeline is verified against its Lua reference on 33,408 px (max diff 6e-7).

| # | Check | Pass criteria / report |
|---|---|---|
| B1 | Bloom on a `SMK2 Shape` card, a Text+ title, an `SMK2_TextLetter` macro; defaults | Loads, no error, **no pass-through** (the glow is visible; if the console shows `GPU failed`, report the text); soft symmetric halo |
| B2 | Radius 10 / 40 / 120 / 300 px | Halo grows with radius; no blocky/diamond artifacts, no banding or steps (zoom 400 % on the halo and report); resolution independent (px@1920) |
| B3 | Compare with `SMK2 Look` glow at 120 px (Max quality) on the same object | Visual difference (mean abs difference image); which looks smoother; report both ms/frame |
| B4 | Intensity 0.5 / 1.2 / 3, Spread 0.5 / 1 / 2, colours, Alpha vs Brightness (threshold) | As expected; Brightness glows only bright parts; Spread < 1 = longer tails |
| B5 | Behind / additive / Glow Only | Behind leaves the object untouched; Glow Only removes it; no dark or light fringe over bright and dark backgrounds with soft edges |
| B6 | **DoD:** small Text+ with a 300 px glow near the box edge; Bloom on a Shape that fills the frame | Glow not clipped at the input's DoD; output window padded; report any clipping |
| B7 | 1080p, 1080×1920, 4K; 24/30/60 fps | Same look at equal seconds; no tile seams / edge darkening at the frame borders |
| B8 | **Cost (cold 60 fps, 300 frames):** Bloom R=40 and R=300 at 1080p and 4K; 1 / 5 / 10 Blooms; vs Look glow Max R=120 | ms/frame each. Expectation: nearly independent of the radius; report whether it beats Look at R ≥ 120 |
| B9 | Animated input (Shape In/Out, Look shine) and a trimmed 46-frame clip | Glow follows the input every frame; no stale frames; last frame consistent |
| B10 | Two instances; save, full restart, reopen; no BezierSpline | Independent; pixel-identical |
| B11 | Inspector input list | Report labels, any confusing control |

**For the user by hand:** whether the glow looks good compared to the Look glow / NeoEdit Glow; viewer fps.
