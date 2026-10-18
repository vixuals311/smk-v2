# Phase 16 Gate — rc2 re-check (smoke of all 34 tools + the three changed defaults)

rc2 changed defaults only: **Connector** Start/End Magnet = Auto (`AMag`/`BMag` = 1), **Look** and **Bloom** "Glow Behind Object" on (`GlowBehind` = 1). Unit-tested, never seen in Resolve. This gate checks them and re-runs the whole-product smoke.

**Install:** `python build/build.py`, `python scripts/install.py`, restart Resolve. Before the restart make sure `Fuses\SMK2` holds exactly the 12 `SMK2_*.fuse` files (no `SMK2_Spike_*.fuse`; Resolve loads every sub-folder of `Fuses/`) and `Macros\SMK2` holds 22 macros. Verify by script (`AddTool("Fuse.SMK2_<name>")`) that every tool loads.
**Rules (standard):** scripting only; **one session drives Resolve**; project `SMK Phase16` (keep "SMK Test" untouched); one comp per check, named after the check; deselect (`FlowView.Select()`) before each paste; comp rate = timeline rate; cold renders (Background +0.001); readable node graphs (distinct `flow:SetPos`, left→right, 2–3 units apart, clear names, a Note per group); `ProjectManager.SaveProject()`; write NOT VERIFIED where not observed. Shape sources are empty on frame 0 and the last frames.
Write `docs/PHASE16_RESULTS.md` (table: check, comp, result, evidence), push branch `phase16-results`, paste the table.

## Part A — Smoke, all 34 tools (22 macros + 12 Fuses), 4 frames each

| # | Check | Pass criteria / report |
|---|---|---|
| S1 | For every tool, a comp `S1_<name>` with defaults (image Fuses fed by a Shape or Text+; modifiers Motion / Motion Rig attached to a Shape or Text+ input). Render frames 3, 12, 60, 116 | 136/136 Complete; output non-empty (Shape/Cursor/Connector as generators; modifiers via their host); table: tool, comp, non-bg px at the 4 frames |
| S2 | Not pass-through: for the 7 image Fuses (Animator, Bloom, Look, LongShadow, PageCurl, Reflection, Relief) compare frame 60 (Animator: frames 3 and 12) with the tool bypassed (`TOOLB_PassThrough`) | Pixels differ for each |
| S3 | Compare all 136 frames with the Phase 15 renders (`docs/phase15_evidence`, same method). Expected identical for everything except Connector, Look, Bloom and macros containing them (UIBlock, Callout, CardStack, StatCard, ClickDemo and their variants, if they embed those) | List every tool whose frames differ and by how much; each difference must be explained by one of the three changed defaults, otherwise it is a regression |

## Part B — The three changed defaults

| # | Check | Pass criteria / report |
|---|---|---|
| C1 | **Connector, defaults.** Add `SMK2_Connector` fresh; read `AMag`, `BMag` | Both = 1 (Auto); the UI label reads "Auto (edge toward target)" |
| C2 | **Connector, behaviour.** Two UIBlocks A (left) and B (right), a Connector from A to B with Start/End Box sizes set to the blocks' sizes, defaults otherwise. Render frame 60. Then the same comp with `AMag`/`BMag` = 0 (Off) | Auto: line starts and ends on the block edges facing the other block (gap ≈ 6 px), does not cross either label. Off: line starts at the block centres (the rc1 look). Report the start/end pixel positions of the line for both; also repeat with B placed below A (edge should switch to bottom/top) |
| C3 | **Connector, hand-set magnets still work.** `AMag` = Right, `BMag` = Left; then Top/Bottom | Line leaves/enters at the chosen edge |
| C4 | **Look, defaults.** Add `SMK2_Look`; read `GlowBehind` | = 1 |
| C5 | **Look, bright card.** Plain bright card (Shape, near-white) with Look glow on, defaults. Render with `GlowBehind` 1 and 0 | rc2 default: card stays unblown (card interior pixels equal to the input within 2/255) and the glow is visible only outside the card; with 0 the card blows out as in rc1. Report max interior RGB and glow px count for both |
| C6 | **Bloom, defaults.** Add `SMK2_Bloom`; read `GlowBehind` | = 1 |
| C7 | **Bloom, bright card.** Same as C5 with Bloom | Same criteria as C5 |
| C8 | **Look + Bloom stacked on a bright card** (the rc1 demo case: Look glow → Bloom → Long Shadow on block B) | Card not blown to white; Report max interior RGB and a screenshot |
| C9 | **Glow Only** still works with Behind on (`GlowOnly` = 1 in Look/Bloom) | Object absent, glow present |
| C10 | **Demo re-render.** Re-run the Phase 15 demo (`docs/phase15_evidence/SMK_RC1_demo.drp`, import into `SMK Phase16`, timeline `RC5_demo`), render 120 frames cold | No errors; Connector no longer crosses block A's label; block B not white; ms/frame vs 111 ms (rc1); save a contact sheet of frames 20/60/100 |

## Part C — Housekeeping

| # | Check | Pass criteria / report |
|---|---|---|
| H1 | Restart round-trip: save, quit Resolve, relaunch, reopen, re-render C2, C5, C10 frame 60 | Pixel-identical to before the restart |
| H2 | Log scan for `SMK2`, `GPU failed`, `RunSession failed`, `Lua error`, `CRASH DUMP`, `Unknown tool` | None expected; list any hits |

**NOT VERIFIED by script (owner by hand):** Effects-library panes, Inspector appearance, dragging Connector handles, viewer fps.
