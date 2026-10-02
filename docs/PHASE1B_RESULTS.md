# Phase 1b Gate Results: SMK2 Motion Rig

Date: 2026-10-02 · Branch: `phase1b-results` · Built from `main` at `97551e6`. **No source changes were needed in this phase.**

Anything not observed is marked **NOT VERIFIED** with the reason.

## Environment and method

- Same machine as Phases 0 and 1: Resolve **Studio** 21.1.0.14, Windows 11 (build 26100), RTX 4070 SUPER, CUDA.
- Steps run: `git pull`, `python scripts/install.py` (Fuses in `Fuses/SMK2/`), Resolve restart.
- Unit tests: `test_smk_core` 49/0, `test_fuse_harness` 11/0, `test_animator` 10/0, `test_motion_rig` 9/0.
- Same method as Phase 1: scripting API plus Deliver-page PNG renders, analysed with PIL. I could not see the viewer or the Fusion Console, so nothing was judged by eye.
- Wiring was done by script: `AddModifier("Blend", "Fuse.SMK2_MotionRig")` for Opacity, and `input.ConnectTo(rig.<Output>)` for Size, Angle and Center. I did not use the GUI right-click menu.
- Benchmark timings are Deliver render times of 300 frames at 60 fps, 1080p, PNG output. They are **not** viewer playback fps (NOT VERIFIED, no viewer access).
- Test projects: `SMK Phase1b Gate` (24 fps) and `SMK P1b fps60`. Your `SMK Test` project was not touched.
- Resolve hung once during a render started right after a `ScriptReload` of 20 Fuses, so I force-killed it and rebuilt the graph. Later I temporarily installed two probe Fuses (R6 analysis). One had an escaping mistake of mine and opened an error dialog at startup, which I dismissed by simulated mouse click. The probe Fuses are removed again.

## Results

| Gate | Result | Evidence |
|---|---|---|
| **R1** Opacity, Scale, Angle | **PASS** | `AddModifier("Blend", "Fuse.SMK2_MotionRig")` on a Merge worked and the modifier exposes six outputs: Opacity, Scale, Angle, Offset X, Offset Y, Center. Then `Merge.Size.ConnectTo(rig.Scale)` and `Merge.Angle.ConnectTo(rig.Angle)` both connected (checked with `GetConnectedOutput()`). At 24 fps, text bbox centre x is 889.5 (frame 3), 967.5 (frame 6), 964.5 (frame 12): the same slide, overshoot and settle as the Animator. No Fuse errors in the Resolve log. Note: in Python, `merge.Angle` returns the value, so I fetched inputs by `INPS_ID` before connecting. |
| **R2** Point output to Merge.Center | **PASS, direct connection works** | **`Merge.Center.ConnectTo(rig.Center)` connects** (the Point output goes straight into the Point input). The expression fallback `Point(<rig>.Center.X, …)` was **not needed and not tried**. 1920×1080: slide angle 180/0.1 moves the card −192 px (628 vs 820 left edge), 90 moves it up 192 px, 270 moves it down 192 px, so the vertical slide is 0.1×**width**, not 0.1×height. 1080×1920: left −108 px, up −108 px (0.1×1080), again aspect-correct. Same distances as the Animator. |
| **R3** four connections, save/reopen | **PASS** (≤1/255 pixel difference) | One rig drives Blend, Size, Angle, Center. After save, close and reopen, all four connections are intact and there is no BezierSpline in the comp. A re-render of frame 6 has identical position (bbox 824–1111 × 489–590) and a maximum difference of **1 level of 255** against the pre-save render (diff bbox covers only the text). Re-rendering twice after reopen is bit-identical, so the 1-level change is from save/reopen or a resampling difference, not noise. Not strictly bit-identical. Done within one Resolve session, not an app restart. |
| **R4** 20 cards, Index 0..19, Stagger 0.05 | **PASS** | 20 Merges, each with its own Rig (all four outputs wired), 60 fps. First visible frame per card: 3, 6, 9, …, 60 (a constant step of 3 frames = 0.05 s). Setting card 19's Stagger to 0.025 moved its first visible frame from 60 to 32. The change was made by script on a live comp with no reload. |
| **R5** pixel parity vs Animator | **PASS** (pivot caveat) | Same text and background at 24 fps, Rig on Merge vs `SMK2 Animator` into a Merge. Frame 0: difference 0. Frames 3, 6, 12: maximum difference **1/255**, positions equal. With Scale 0.5 and Rotation 30 at frame 0 (default pivot): centre (771.5, 538) for the Animator vs (771.5, 538.5) for the Rig; widths 143 vs 145 px (resampling). **Difference:** the Animator has a Pivot X/Y control. With the Animator pivot at (1,1) the card landed at (1450.5, 472), while the Merge exposes **no `Pivot` input to the scripting API** (the list was empty), so the Rig cannot move the pivot and always scales/rotates about the Merge's default pivot (frame centre). Merge pivot behaviour in the GUI is NOT VERIFIED. |
| **R6** benchmark | **FAIL** (target ≤16.6 ms/frame for the Rig variant) | See the table below. |
| **R7** modifier cost, Blend only vs all four | **No measurable difference** | Blend only 77.5 and 84.2 ms/frame (two runs), Blend + Center 79.2, all four wired 80.8 and 82.4. The run-to-run noise (about ±4 ms) is larger than any effect of wiring more outputs. So animating Merge Size, Angle and Center does **not** raise the Merge cost noticeably. |

### R6 benchmark (60 fps timeline, 1080p, 300 frames to PNG, 20 Text+ cards merged over a Background)

| Variant | Total ms | ms/frame | fps equivalent |
|---|---|---|---|
| (a) No animation (plain Merges) | 2 251 | **7.5** | 133 |
| **(b) 20 Rigs on the Merges**, all four outputs wired | 24 247 / 24 734 (two runs) | **80.8 / 82.4** | about 12 |
| (b) 20 Rigs, Blend only | 23 244 / 25 246 (two runs) | **77.5 / 84.2** | about 12 |
| (b) 20 Rigs, Blend + Center | 23 761 | **79.2** | 12.6 |
| **(c) 20 Animators** | 21 751 | **72.5** | 13.8 |
| **(d) 20 native Transforms by expression** | 10 752 | **35.8** | 27.9 |

Extra variants I added to find where the cost comes from:

| Variant | Total ms | ms/frame |
|---|---|---|
| (e) 20 Merges animated by **native expressions** on Blend and Center (no Fuse, no extra node) | 6 743 | **22.5** (44 fps) |
| (f) 20 plain `SMK2 Motion` modifiers on Merge Blend | 24 766 | **82.6** |
| (g) 20 trivial **null Fuse modifiers** (just `Out:Set(clamp(req.Time/30))`, no Comp access) on Merge Blend | 20 261 | **67.5** |
| (h) 20 null modifiers that read `Comp:GetPrefs` and `Comp.RenderStart` | 20 756 | **69.2** |

What this says:
- **The Rig misses the ≤16.6 ms target by about 5×** (about 80 ms/frame), and it is no faster than the Animator (72.5 ms).
- **The cost is the Fuse modifier mechanism itself, not our code.** A null modifier that does almost nothing already costs about 3 ms per modifier per frame (67.5 ms for 20). Reading the Comp adds about 0.1 ms each. The Rig's own work (engine maths plus six outputs) adds about 0.7 ms each (82 vs 67.5 ms). A profile inside the Rig shows `Process` at about 0.5 ms per call, one call per frame per rig (`phase1b_evidence/rig_profile.log`).
- **Native expressions on the same Merges are about 3.5× cheaper** (22.5 ms), and plain Transforms 35.8 ms.
- So the "zero extra nodes" design did not help: for a Fuse, one modifier per card costs about as much as one extra node per card. Only non-Fuse (native expression) animation gets under 25 ms here.
- I did not find a Merge cost increase from Size ≠ 1 or Angle ≠ 0 (see R7).

## Recommendations

| Gate | One line |
|---|---|
| R1–R5, R7 | Go. The Rig is functionally correct, wires to Blend/Size/Angle/Center directly, and matches the Animator to ≤1/255 and ≤2 px. |
| R2 | Wiring method that works: **direct `ConnectTo` of the Point output to `Merge.Center`**. No expression workaround needed. |
| R6 | Not met. A Fuse modifier costs about 3 ms per card per frame. To reach 60 fps with 20 cards, generate native expressions (or a baked animation) on the Merges from the SMK maths instead of attaching one Fuse per card, or drive all 20 cards from one Fuse. Measure real viewer playback before deciding, because render time is only a proxy. |
| R5 | Add a pivot option only if needed: the Merge has no scriptable Pivot input, so the Rig cannot match the Animator's Pivot X/Y. |

## Needs the user

1. R6: watch real **viewer playback fps** at 60 fps 1080p with the 20-card Rig graph and with the native-expression graph (render time is only a proxy).
2. R1: do the same wiring through the GUI (right-click Blend → Modify With → `SMK2 Motion Rig`, then drag the other outputs). I only did it by script.
3. R5: check Merge pivot behaviour in the GUI (the Merge's Pivot control was not visible to scripting).
4. R3: do the save, close and reopen with a full Resolve restart in between.
5. Decide whether to go to a native-expression generator (R6 recommendation).
