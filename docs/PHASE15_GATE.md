# Phase 15 Gate — Release candidate 1 (M7), verified from the release zip only (run by Agent A, the only session driving Resolve)

Everything below is done from **`dist/release/SMK2_v2.0.0-rc1.zip`** (built by `python build/package.py`), not from the repo: this is what a customer gets.
Standard hygiene (scripting only, deselect before paste, cold renders, readable graphs, one comp per check, `SaveProject()`, project `SMK RC1`, keep "SMK Test" untouched, NOT VERIFIED where not observed, **one session only**).
Write `docs/PHASE15_RESULTS.md`, push `phase15-results`, paste the table.

**Clean-machine simulation:** before starting, move the live `Fuses/SMK2`, `Macros/SMK2` folders, the seven old `SMK2_Spike_*.fuse` files and any installed `SMK2_Titles*.drfx` OUT of the Fusion folder (to a backup folder; Resolve loads every sub-folder of `Fuses/`). Restart Resolve. Restore nothing until the end.

| # | Check | Pass criteria / report |
|---|---|---|
| RC1 | Build the zip (`python build/package.py`); unzip to a temp folder; verify `SHA256SUMS`; open `README.txt` | Hashes OK; README says how to install, uninstall, and the Fuses-first rule |
| RC2 | Install **only** from the unzipped release: `python install.py` (its own, no repo), restart Resolve | 12 Fuses + 22 macros land in `Fuses/SMK2` and `Macros/SMK2`; the Effects ▸ Fuses ▸ SMK v2 and Macros ▸ SMK2 lists are as in the manual (report names) |
| RC3 | Copy `SMK2_Titles_v2.0.0-rc1.drfx` to `Support/Fusion/Templates/`, restart; insert 3 titles | Titles insert and render |
| RC4 | **Whole-product smoke from the release**: all 12 Fuses and 22 macros, 4 frames each | 136/136 Complete and no pass-through (compare with bypass for the GPU Fuses) |
| RC5 | **Demo project**: build ONE realistic comp/timeline that uses the kit as a customer would (CardStack, StatCard with count-up, a TextLetter title, a Connector between two cards with a Cursor click, Look/Bloom/LongShadow on a card, a ProgressRing); render it to PNG sequence and H.264, decode 3 frames | Renders with no errors; frames show everything; total ms/frame; **save the project as `docs/phase15_evidence/SMK_RC1_demo.drp`** (export) so the owner can open it |
| RC6 | Install over an existing install (run `install.py` twice) and `--uninstall` then reinstall | Idempotent; nothing duplicated; foreign files untouched |
| RC7 | Full restart round-trip of the demo project | Pixel-identical |
| RC8 | Manual accuracy: pick 5 random controls per Fuse from `MANUAL.md` (name, default, range) and compare with the Inspector values read by script | Report mismatches |
| RC9 | Restore the backed-up folders exactly as they were (and remove the spike Fuses if the owner wants: leave them in the backup) | Resolve loads normally |

**Owner's hand-check list (RC1 sign-off), do it in one sitting, in this order — tick or write what is wrong:**
1. Double-click `SMK2_Titles_*.drfx`; confirm the dialog; drag three titles onto the Edit page; trim one by mouse; play it.
2. Viewer playback: StatCard x5, CardStack, TextLetter 12 letters, Bloom, Look at 1080p (first play, then cached). Note fps.
3. Drag the Connector's points/handles/magnet, the Cursor start crosshair (ClickDemo), the Shape line handles and the Page Curl in the viewer.
4. Look and feel: Relief (bevel), Reflection, Page Curl, Long Shadow, Bloom vs Look glow, StatCard counts, presets Glass/Neon/Soft. What would you change?
5. Inspector: pages and labels of CardStack, StatCard, Connector, Look: anything confusing, missing, too long?
6. Anything you expected from the Master Plan that is not there.
