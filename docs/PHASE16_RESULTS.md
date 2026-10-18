# Phase 16 Results: rc2 re-check (S1–S3, C1–C10, H1–H2)

Resolve Studio 21.1.0.14, Windows 11. Project `SMK Phase16` (+ `SMK Phase16 Demo`, the imported rc1 demo); `SMK TEST` not touched. Scripting only, **one session**. Built from `main` at `baa2c75` (version 2.0.0-rc2): `python build/build.py`, all 21 `tests/test_*.py` pass (kernel parity skipped, no gcc), `python scripts/install.py` into the live Fusion folder. **`Fuses\SMK2` held exactly the 12 `SMK2_*.fuse` files (no `SMK2_Spike_*`), `Macros\SMK2` 22 macros**; no `SMK2_Titles*.drfx` installed (not needed here). Resolve was started fresh for this phase. One comp (own timeline) per check, 1080p, 24 fps, PNG renders, no source file changed.
Analysis with PIL/numpy on the rendered PNGs; "non-bg px" = Phase 12 method (every 4th pixel, threshold 6 over bg 51/51/64).

## Results table

| Check | Comp | Result | Evidence |
|---|---|---|---|
| **S1** smoke, 34 tools × frames 3/12/60/116 | `S1_<name>` ×34 | **PASS: 136 / 136 `Complete`**, none empty except by design (Cursor f3, PageCurl f60/f116 as in Phase 12). Fuses via `AddTool`; Motion on a Text+ `Size`, MotionRig on a Merge `Blend`; macros pasted from the installed `.setting` files. | `s1_table.txt`, `renders/smoke_*.json` |
| **S2** not pass-through (7 image Fuses) | `S1_<name>` bypassed (`TOOLB_PassThrough`) | **PASS.** Pixels differing from the bypassed render (frame 60; Animator f3 / f12): Animator 63 539 / 6 840, Look 79 976, Relief 20 655, Reflection 50 133, PageCurl 41 049, Bloom 156 968, LongShadow 196 846 (max channel diff 32–204). | `renders/S2_*` |
| **S3** compare with the earlier counts | `S1_*` vs `docs/phase12_evidence/h1_table.txt` | **PARTLY COMPARABLE; no regression found, one thing unexplained.** The stored rc1 renders are not in the repo, so I compared my sampled counts with the Phase 12 table. Shape, Cursor, Callout, ClickDemo (+ Glass, Neon) are **identical**. Image Fuses (Animator, Look, Bloom, Relief, Reflection, PageCurl, LongShadow, MotionRig) are **not comparable**: my Text+ source ("SMK", size 0.2) is bigger than the Phase 12 source. Connector differs (50/162/164/21 vs 76/254/263/26): expected, the magnet default is now Auto and the line is shorter (Phase 12 had the centre-to-centre line). The other macros (UIBlock, CardStack, StatCard, ProgressBar/Ring, TextLetter/Line/Word and variants) differ by **0.1 – 8 % at single frames, typically 1–25 px of 10–30 k** (e.g. UIBlock f116 90 vs 95, TextLine f60 756 vs 766, CardStack f116 248 vs 273). **No macro embeds Connector, Look or Bloom (grep of the installed `.setting` files), so none of the three changed defaults can cause these**; the likely cause is text anti-aliasing at the sampled pixels on this machine, but the cause is **NOT VERIFIED**. | `s1_table.txt` |
| **C1** Connector defaults | fresh `SMK2_Connector` | **PASS.** `AMag = BMag = 1.0` (Auto); label "Start Magnet" with the choice "Auto (edge toward target)" in the source. | this table |
| **C2** Connector magnets in use | `C2_connector_behaviour` | **PASS.** Blocks A / B (0.14 × 0.07 of frame width) at x 0.3 / 0.7, frame 60. **Auto:** line pixels x 708–1202 at y ≈ 537: starts at A's right edge (710) and ends at B's left edge (1210 − gap), **nothing crosses either label**. **Off (rc1 look):** x 567–1343, line runs from block centre to block centre across both labels. **B placed above A (A bottom-left, B top-right):** Auto switches to the facing edges (line leaves A's top edge, enters B's bottom). | `c2_sheet.png` |
| **C3** hand-set magnets | same comp | **PASS.** Right/Left: identical to Auto (x 708–1202). Bottom/Top on side-by-side blocks: line leaves A's bottom and enters B's top (y 378–701, curved). | `renders/C3_*` |
| **C4** Look default | fresh `SMK2_Look` | **PASS.** `GlowBehind = 1`. | this table |
| **C5** Look on a bright card | `C5_look_bright_card` | **PASS.** Card fill (0.75, 0.8, 0.9) = RGB 191/204/230. Behind **on (default):** card interior max RGB **191/204/230, max diff vs bypassed Look = 0**, glow only outside (52 682 px outside the card rect vs 11 444 for the card's own shadow). Behind **off:** interior **255/255/255** (diff 64), the rc1 blow-out. | `renders/C5_*` |
| **C6** Bloom default | fresh `SMK2_Bloom` | **PASS.** `GlowBehind = 1`. | this table |
| **C7** Bloom on a bright card | `C7_bloom_bright_card` | **PASS.** On: interior 191/204/230, diff 0, 125 876 glow px outside. Off: 255/255/255. | `renders/C7_*` |
| **C8** Look → Bloom → LongShadow stack | `C8_stacked_card` | **PASS.** On: interior 191/204/230 (diff 0 vs the bare card), 287 618 px outside. Both Behind off: 255/255/255. | `renders/C8_*` |
| **C9** Glow Only with Behind on | `C5_…` / `C7_…` | **PASS.** Look and Bloom: the card colour is gone (interior 115/166/255 = glow colour only), glow present (218 570 / 291 764 non-bg px). | `renders/C9_*` |
| **C10** demo re-render | `RC5_demo` (rc1 demo imported as project `SMK Phase16 Demo`) | **PASS.** 120 frames cold, no errors, 1080p PNG: **218 ms/frame first run, 102 ms/frame second** (rc1: 230 / 111). The Connector in the demo reads `AMag = BMag = 1`, Look and Bloom `GlowBehind = 1`. Frame 60: the line starts at block A's right edge and ends at block B's left edge, **no longer crossing block A's label**; block B keeps its navy card with a blue glow ring (not white). Visual check by eye: Connector pulse dot, cursor ripple, Long Shadow all present. | `c10_sheet.png`, `c10_frame060.png` |
| **H1** restart round trip | `C2_connector_behaviour`, `C5_look_bright_card`, `RC5_demo` | **PASS: pixel-identical.** Projects saved, Resolve quit (`resolve.Quit()`) and relaunched (the first relaunch attempt did not start; the second did), projects reopened (39 timelines): C2 and C5 frame 60 **max diff 0**; the demo's 120 frames **max diff 0**. Inputs survived (`AMag/BMag` 1, `GlowBehind` 1). | `renders/H1_*` |
| **H2** log scan | `davinci_resolve.log`, `ResolveDebug.txt` | **PASS.** 0 hits for `SMK2`, `GPU failed`, `RunSession failed`, `Lua error`, `CRASH DUMP`, `Unknown tool`. | — |

## Notes
- An error in my own first macro runs: `comp.Paste(<string>)` pastes the clipboard, not the string; the first macro comps held a wrong macro and were deleted and rebuilt with `comp:Paste(bmd.readfile(...))` through `comp.Execute`. Only the rebuilt comps are reported.
- Image Fuse inputs are called `Image` (not `Input`); the macros' output is `Output`.
- The two cold demo runs differ in the Background value by +0.001 but their frames were identical here (max diff 0); the Phase 15 note about a 1-level red shift did not show up.
- Rendering only the cases that matter: this gate does not repeat the 34-tool Phase 12 hardening checks (resolution, frame-rate, stress).

## NOT VERIFIED
- Effects-library panes, Inspector appearance (combo label "Auto (edge toward target)" read from the source and the Inspector list names via script, not seen on screen), dragging Connector handles, viewer fps.
- Cause of the small macro count differences in S3 (not related to the three defaults).
- Whether the rc1 demo stores its own magnet values was not inspected; after import the Connector reads Auto.

## Evidence
`docs/phase16_evidence/`: `q16.py` (build/render helpers), `an16.py` (analysis), `s1_table.txt`/`.json`, `c2_sheet.png`, `c10_sheet.png`, `c10_frame060.png`. The PNG renders (56 MB, `renders/`) are not committed, so the `renders/...` references above are local only.
