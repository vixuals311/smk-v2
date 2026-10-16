# Phase 14 Results: Edit-page titles bundle (.drfx) and Relief fix (E1–E10)

Resolve Studio 21.1.0.14, Windows 11. Project `SMK Phase14` (`SMK Test` not touched). Scripting only; the only UI interaction was a read-only screenshot of the screen (E6). **I was the only session driving this Resolve.** One comp / timeline per check, named after it. Everything unzipped went to a temp folder.

Setup: `git pull` (main at the Phase 13 merge), `python scripts/install.py`, Resolve restarted, `python build/build.py`, every `tests/test_*.py` once: **all pass, 0 failures** (`docs/phase14_evidence/p14_tests.log`; kernel-parity SKIPPED, no C compiler). **No source file was changed in this phase.**

## Results table

| Check | Comp / timeline | Result | Evidence |
|---|---|---|---|
| **E1** package + unzip | (temp folder) | **PASS.** `python build/package.py` → `dist/release/SMK2_v2.0.0-dev.zip` (43 entries). Unzipped to a temp folder: `SMK2_Titles_v2.0.0-dev.drfx` (65 954 bytes) is inside and listed in `SHA256SUMS`; the `.drfx` has **21 files under `Edit/Titles/SMK2/`**, readable names: `SMK2 TextLetter`, `SMK2 TextWord`, `SMK2 TextLine`, `SMK2 ProgressRing`, `SMK2 ProgressBar`, and `SMK2 UIBlock / CardStack / StatCard / ClickDemo` each as base, ` Glass`, ` Neon`, ` Soft` (`.setting` files). | this table |
| **E2** install by script | `E2_probe` | **PASS: copying the `.drfx` into `Support/Fusion/Templates/` and restarting Resolve is enough; no confirm dialog was needed.** The file was copied to `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Templates\` (the folder already holds many other `.drfx`), Resolve restarted, then `timeline:InsertFusionTitleIntoTimeline(name)`. **Name strings that work:** `"SMK2 StatCard"` (the file stem), `"SMK2 StatCard Neon"`, `"StatCard"` (short; inserted `SMK2_StatCard`), `"SMK2/SMK2 StatCard"`, `"Edit/Titles/SMK2/SMK2 StatCard"`. **Does not work:** `"SMK2_StatCard"` (underscore; returns None). Inserted titles are 120 frames long; each comp contains the macro group + `MediaOut1`. Whether Resolve also needs the restart (vs. picking the file up while running) was **not tested (NOT VERIFIED)**. The double-click confirm dialog was not exercised (yours). | `p14_*`, `e3.json`, E2 outputs in the log below |
| **E3** all 21 titles | `E3_titles` (21 titles on one track in the order above, 120 frames each) | **PASS: no failure, no blank title.** 84 renders (21 × frames 0 / 12 / 60 / 116), all `Complete`. Frame 0 is empty for every title by design (In has not started; Shape is empty on frame 0). Table below (non-background pixels, step 4, threshold 6, background black). | `e3.json`, `e3an.py`, `frames/p14_e3_*` |
| **E4** open a title comp | `E3_titles` item `SMK2 StatCard` | **PASS.** Edit page → playhead on the title → Fusion page: tools `SMK2_StatCard` (GroupOperator, the only top-level tool besides `MediaOut1`) with inner `UIS_Ctrl`, `UIS_Card`, `UIS_Num`, `UIS_Label`, `UIS_M1`, `UIS_M2`, `UIS_Animator`, all names intact. `MediaOut1.Input` is connected to the group's `MainOutput1` (the connection reports the inner tool `UIS_Animator`, which feeds `MainOutput1`). Group has **94 inputs on 8 Inspector pages: Common (3), Number (11), Count (6), Caption (5), Card (27), Motion (8), In Motion (17), Out Motion (17)** (read from `INPS_ICS_ControlPage`). Visual Inspector appearance NOT VERIFIED (yours). | `e5.json` (tools), E4 output |
| **E5** clip-relative timing on titles | `E5_title_trim` | **PASS.** Titles cannot be trimmed by a script API (`SetProperty("Duration")` returns False; titles report left / right offset 0 / 0). A **valid** trim was made by inserting a second title with the playhead at 01:00:03:08: Resolve split the StatCard into a head item (frames 86400–86480, 80 frames, right offset 40) and a tail item (86600–86640, 40 frames, left offset 80). **Values read in the title comps: head item `RenderStart 0, RenderEnd 79, GlobalStart 0, GlobalEnd 79`; tail item (head-trimmed) `RenderStart 80, RenderEnd 119, GlobalStart 80, GlobalEnd 119`** (read from the comp attributes; the Fuse-side values were not probed separately: NOT VERIFIED, the render behaviour below is consistent with them). **Count starts at the trimmed head:** the tail item's frames 0 / 3 / 12 / 27 / 28 are **pixel-identical to the same local frames of the untrimmed title** (max difference 0), i.e. its first frame is clip time 0 (card empty on frame 0, In from there). **The Out ends on the trimmed last frame:** head item non-bg px 10 116 until frame 68, 10 175 at 72, 10 004 at 76, **0 at 79 (last)**; tail item 10 109 at 34, 476 at 37, **0 at 39 (last)**; untrimmed reference stays at 10 116 until its own end (0 at 119). | `e5.json`, `frames/p14_e5_*` |
| **E6** title without the Fuses | `E6_no_fuses` (3 titles inserted before the test) | **FAILS LOUDLY WITH A MODAL WARNING DIALOG; scripting then blocks.** With the live `Fuses/SMK2` folder removed from the Fuses tree and Resolve restarted: opening a title comp (script `GetFusionCompByIndex`, or the Fusion page) raises a **modal dialog "Warning: Unknown tool found. Name: UIS_Card  ID: Fuse.SMK2_Shape"** with an **OK** button and a "Do not show this again" checkbox, one per missing tool (`UIS_Card` = Shape, `UIS_Animator`, `UIB_Shape`, `UIB_Animator`, …; screenshot in `frames/e6_dialog_*.png`); the Resolve log has `Fusion ERROR Unknown tool found: "UIS_Card" (Fuse.SMK2_Shape)`. The missing Fuse nodes are loaded as **`Dummy`** tools (script tool list: `UIS_Card Dummy`, `UIS_Animator Dummy`; everything else, Text+, Merge, Background, is normal). **While the dialog is open the Resolve scripting API stops answering** (`OpenPage`, `SaveProject`, `CreateEmptyTimeline` return None); I had to kill Resolve (project had been saved). Effect on pixels / render with missing Fuses was therefore **NOT VERIFIED** (a first attempt kept the Fuses loaded: renaming the folder to `SMK2_OFF` inside `Fuses/` does NOT remove them, Resolve scans every sub-folder: the folder must be moved out of `Fuses/`). **Restored:** the folder was moved back, Resolve restarted, the stored comps show `Fuse.SMK2_Shape` / `Fuse.SMK2_Animator` again (not Dummy) and `AddTool("Fuse.SMK2_Shape")` works. **Manual text:** "Install the Fuses first (`install.py`), then the titles. Without the Fuses every title opens with 'Warning: Unknown tool found … Fuse.SMK2_Shape' and shows nothing for those nodes." | `frames/e6_dialog_crop.png`, `frames/e6_dialog_screen.png`, `e6.json`, `e6r.json` |
| **E7** uninstall | `E7_after_uninstall` | **PASS.** `.drfx` deleted from `Templates/`, Resolve restarted: `InsertFusionTitleIntoTimeline` returns None for `"SMK2 StatCard"`, `"SMK2 UIBlock Neon"`, `"StatCard"`, `"SMK2/SMK2 StatCard"`, `"Edit/Titles/SMK2/SMK2 StatCard"` (a stock title `"Text+"` still inserts); `AddTool("Fuse.SMK2_Shape")` and `("Fuse.SMK2_Relief")` still work (Fuses unaffected). Titles already placed in a project keep their stored comps (NOT VERIFIED beyond the project reload). **State left:** the `.drfx` is NOT installed now; reinstall by copying `dist/SMK2_Titles_v2.0.0-dev.drfx` to `Templates/`. | `e7.json` |
| **E8** copies independent | `E8_two_copies` | **PASS.** Two `SMK2 StatCard` titles on the timeline: Target Value 12 480 / 12 480; set A = 777 → (777, 12 480); set B = 55 555 → (777, 55 555), re-read from fresh comp objects (777, 55 555); the two renders of frame 60 differ (8 224 px). Duplicate inside a title comp (Fusion page, Copy / Paste the group): `SMK2_StatCard_1` + inner `UIS_*_1`, same ID; changing the duplicate (42) leaves the original (777). The duplicate's output was not wired / rendered (NOT VERIFIED). | `e8.json`, `e8b.json`, `frames/p14_e8_*` |
| **E9** Relief again | `E9_relief_quality` | **Crosshatch gone; normal-size look is NOT unchanged: a fine grain was added.** Size 80 / Depth 12 at Quality 0 / 1 / 2: the irregular crosshatch of Phase 13 is replaced by a smooth bevel with **fine grain** on the lit/shadow edge (`frames/e9_cmp_size80.png`, top = Phase 13, bottom = now). Q0 vs Q2 mean absolute difference at Size 80 is now 2.52 /255 (it was exactly 0.00: the jitter makes the qualities differ again); my second-difference roughness measure rises from 3.9 to 11.7 because of the grain (it measures noise, not the crosshatch). **Normal size (Size 8, Depth 2) vs the Phase 13 frame:** full-frame mean absolute difference **0.18 /255** (max 71); ring crops Q0 / Q1 / Q2: **1.19 / 0.58 / 0.28**. At 4× zoom the Quality 0 bevel edge visibly changes from a smooth banded edge to a grainy one (`frames/e9_cmp_default_zoom.png`); I did not look at Quality 1/2 at that zoom. Whether the grain is acceptable at 100 % is a look decision (yours). Sizes 16 / 24 / 32 / 48 / 64 were rendered too (roughness 9–15, Q0 vs Q2 2.4–3.5). | `e9.json`, `frames/e9_*.png`, `q14.py` |
| **E10** H1 smoke after the rebuild | `H1_<name>` ×34 | **PASS: 136 / 136 Complete.** 132 / 136 frames are pixel-identical to the Phase 12 renders; **the only differences are `Relief` at all 4 frames (max difference 28, 1 959 px above 6) = the intended Relief change.** | `e10a.json`–`e10c.json` |

### E3: non-background pixels per title (frames 0 / 12 / 60 / 116)

| Title | f0 | f12 | f60 (mid) | f116 (last−3) |
|---|---|---|---|---|
| SMK2 TextLetter | 0 | 775 | 768 | 161 |
| SMK2 TextWord | 0 | 776 | 768 | 326 |
| SMK2 TextLine | 0 | 762 | 768 | 321 |
| SMK2 ProgressRing | 0 | 1 749 | 1 718 | 1 299 |
| SMK2 ProgressBar | 0 | 1 098 | 1 085 | 828 |
| SMK2 UIBlock | 0 | 10 278 | 10 272 | 10 267 |
| SMK2 UIBlock Glass | 0 | 10 278 | 10 272 | 304 |
| SMK2 UIBlock Neon | 0 | 13 539 | 13 540 | 392 |
| SMK2 UIBlock Soft | 0 | 11 672 | 11 671 | 10 197 |
| SMK2 CardStack | 0 | 22 013 | 21 933 | 21 765 |
| SMK2 CardStack Glass | 0 | 22 011 | 21 933 | 919 |
| SMK2 CardStack Neon | 0 | 30 071 | 30 191 | 1 686 |
| SMK2 CardStack Soft | 0 | 26 939 | 27 355 | 21 586 |
| SMK2 StatCard | 0 | 10 117 | 10 116 | 10 004 |
| SMK2 StatCard Glass | 0 | 10 117 | 10 116 | 617 |
| SMK2 StatCard Neon | 0 | 13 152 | 13 151 | 917 |
| SMK2 StatCard Soft | 0 | 11 426 | 11 426 | 9 587 |
| SMK2 ClickDemo | 0 | 1 986 | 1 999 | 1 977 |
| SMK2 ClickDemo Glass | 0 | 1 984 | 1 998 | 307 |
| SMK2 ClickDemo Neon | 0 | 3 459 | 3 399 | 345 |
| SMK2 ClickDemo Soft | 0 | 2 562 | 2 539 | 1 902 |

Frame 116 is in the middle of the Out fade (the Out lasts the last 0.5 s). The base and `Soft` cards still count > 10 000 px there because they are still mostly opaque (a translucent Glass / Neon card drops below my threshold earlier); I confirmed on UIBlock that the base title's card is gone on frame 119 (0 px) and that its frames 100 / 108 / 112 are 10 272 / 10 272 / 10 278 px: the Out works (E5 gives the exact timing on a trimmed StatCard), it is the pixel-count threshold, not a missing Out. A suspicious "base holds, Glass ends" pattern at frame 116 was investigated (rendering order and a repeat in a different insert order gave the same numbers: deterministic) and is explained by the Glass fill alpha 0.12 vs 1.0 in the card input values.

## Things that went wrong / worth knowing
1. **E6 modal dialog blocks scripting** (see table): any script that opens a title comp without the Fuses hangs the API until a human clicks OK. Resolve had to be killed once (project saved before).
2. **Renaming `Fuses/SMK2` to another name inside `Fuses/` does not unload the Fuses**; Resolve scans all sub-folders. I first concluded "Fuses missing" wrongly; corrected by moving the folder out.
3. Titles cannot be trimmed through the API (`Duration` is not settable; offsets are 0 / 0). The split trick (second insertion at the playhead) gives a real head-trim and tail-trim.
4. Same Resolve start-up quirks as in Phase 13 (`launch_resolve` tool unreliable; I started `Resolve.exe` directly).
5. Log scan: no `CRASH DUMP`, `GPU failed`, `RunSession failed` or `Lua error` this session; the only new log errors are the four E6 `Unknown tool found` lines. The Fusion console is not readable from scripting.
6. **Live Fuse folder still contains the seven `SMK2_Spike_*.fuse` files from earlier phases** (installed with `--include-spikes`); untouched.

## NOT VERIFIED
- Whether the restart is required for Templates pickup; the double-click dialog; Inspector appearance; render / pixels of a title without the Fuses (blocked by the dialog); Fuse-side `RenderStart/End` in the title comp (only the comp attributes were read); the duplicated title's own output; kernel parity (no C compiler); viewer fps.

## For you to check by hand
1. Double-click `SMK2_Titles_v2.0.0-dev.drfx` and confirm the Effects Library dialog; check the titles appear under Titles ▸ SMK2.
2. Drag a title onto the Edit page and trim it with the mouse; watch the count and the Out.
3. Viewer fps; look and feel, including whether the new Relief grain is acceptable at Quality 0.

## Evidence
`docs/phase14_evidence/`: `q14.py` (E9 / E10 runners), `e3an.py`, raw JSON `e3*.json … e10*.json`, `p14_build.log`, `p14_tests.log`, images in `frames/` (E3 / E5 / E8 frames, the E6 dialog screenshot, E9 comparisons).
