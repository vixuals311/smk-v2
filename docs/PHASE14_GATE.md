# Phase 14 Gate — Edit-page titles bundle (.drfx, M6) and Relief fix (run by Agent A, the only session driving Resolve)

Standard hygiene (scripting only, deselect before paste, cold renders, readable graphs, one comp per check, `SaveProject()`, project `SMK Phase14`, keep "SMK Test" untouched, NOT VERIFIED where not observed, **one session only**).
Write `docs/PHASE14_RESULTS.md`, push `phase14-results`, paste the table.

**What is new**
1. `build/make_drfx.py` → `dist/SMK2_Titles_v<ver>.drfx` (also inside the release zip): 21 titles (every macro except the parked Callout) as complete Edit-page titles under `Edit/Titles/SMK2/` — each is the macro group plus a `MediaOut`.
   Phase 0 S5 showed a title-only `.drfx` installs (double-click shows a confirm dialog, the file lands in `Support/Fusion/Templates/`) and that **Fuses are not carried by a .drfx**, so install the Fuses first with `install.py`.
2. Relief: a per-pixel rotation of the spiral gather (same fix as Reflection) so large Size no longer shows a crosshatch (Phase 13 Q7). Quality still has no effect from Size ≈ 32 up (the tap count is capped at 160).

| # | Check | Pass criteria / report |
|---|---|---|
| E1 | `python build/package.py`, unzip the release to a temp folder; confirm the `.drfx` is inside and lists 21 files under `Edit/Titles/SMK2/` | Yes; names readable ("SMK2 StatCard Neon") |
| E2 | **Install the .drfx by script**: copy it to `<Support>/Fusion/Templates/`, restart Resolve (Phase 0 S5: this is where the double-click dialog puts it). If a confirm dialog is the only way, say so (the user does it by hand) | Titles listed in the Effects Library: use `timeline:InsertFusionTitleIntoTimeline("<name>")` (report the exact name strings that work) |
| E3 | Insert **every one of the 21 titles** on a timeline (one timeline, readable order), render frames 0 / 12 / mid / last−3 of each | No error; each shows its product (non-bg px > 0); report any title that is blank or fails and the reason |
| E4 | Open one inserted title's comp (StatCard) in the Fusion page | The macro group is connected to MediaOut1; the output is the group's `MainOutput1`; node names intact; Inspector controls present (list the pages) |
| E5 | **Clip-relative timing on titles**: put a StatCard title on the timeline, trim head and tail (valid trim: set the clip's in/out inside its own frame range), render | Count starts at the trimmed head; the card's Out ends on the trimmed last frame; report RenderStart/RenderEnd read in the title comp |
| E6 | Title **without the Fuses installed** (temporarily use `install.py --target <temp>` as the only Fuse location, i.e. do NOT have SMK2 Fuses in the live folder — or rename the live `Fuses/SMK2` folder, restart, test, restore) | What the user sees: red/missing tool message? Report how it fails, so the manual can warn |
| E7 | Uninstall: remove the `.drfx` from `Templates/`, restart | Titles gone; Fuses unaffected |
| E8 | Two copies of the same title on the timeline and a title duplicated in the Fusion page | Independent; inputs separate |
| E9 | Relief again: Size 80 / Depth 12 on a Shape ring at Quality 0 / 1 / 2, and a normal-size Relief (Size 8, Depth 2) before/after | Crosshatch gone (fine grain remains?); the normal-size look unchanged (mean abs diff vs Phase 13 frame) |
| E10 | Smoke: H1 (34 tools, 4 frames each) after this rebuild | 136/136 Complete |

**For the user by hand:** double-click the `.drfx` and confirm the Effects Library dialog; drag a title onto the Edit page and trim it with the mouse; viewer fps; look and feel.
