# Phase 2d Gate Results: UI Block v2 re-check

Date: 2026-10-03 · Branch: `phase2d-results` · Built from `main` at `3cda806`, plus one macro fix (`build/make_macros.py`, below).

Anything not observed is marked **NOT VERIFIED** with the reason.

## Environment and method

- Same machine as earlier phases: Resolve **Studio** 21.1.0.14, Windows 11 (build 26100), RTX 4070 SUPER, CUDA.
- Steps run: `git pull`, `python build/make_macros.py`, `python scripts/install.py`, Resolve restart (I had to force-restart it once: it was sitting on a "Create New Project" dialog). Every block in this phase was pasted **fresh** from the new macro file.
- Unit tests: `test_smk_core` 49/0, `test_fuse_harness` 12/0, `test_animator` 10/0, `test_motion_rig` 9/0, `test_shape` 34/0, `test_macros` 13/0 (also after my fix).
- Same method as earlier phases: scripting API plus Deliver-page PNG renders analysed with PIL, plus cropped screenshots of the Inspector.
- Macros are loaded by `comp:Paste(bmd.readfile(<path>))`. Adding from **Effects ▸ Tools ▸ Macros** (V1) is NOT VERIFIED (no way to drive the Effects panel).
- Viewer fps is NOT VERIFIED anywhere (no viewer access). Timings are Deliver render times.

## Project and comps (open these by hand)

Project **`SMK Phase2d Gate`**. Same layout rules as Phase 2c (Note on top, sources left, SMK nodes, Merges, MediaOut right, every tool renamed, positions set with `FlowView.SetPos`, saved with `SaveProject()`). Your `SMK Test` project was not touched.

| Check | Comp to open |
|---|---|
| V1 | `V1_Colours` |
| V2 | `V2_Angle` |
| V3 | `V3_FontStyle` |
| V4 (U3 look and motion) | `V4_U3_Defaults` |
| V4 (U5 parity) | `V4_U5_Parity` |
| V4 (U8 instances) | `V4_U8_TwoInstances` |
| V4 (U9 restart) | all comps |
| V4 (extra: benchmark re-measure) | `V4_U10_Bench12` (60 fps; taps `Card05_Merge`, `Card08_Merge`, `Card12_Merge`) |
| V5 | `V5_PasteMinimal` (the minimal repro) and `V5_ShadowChain` (the original symptom) |

## One macro bug found and fixed (`build/make_macros.py`)

**The label did not rotate with the card.** The macro set `UIB_Label.Angle = UIB_Shape.Angle`, but the Text+ input called "Angle" is only a **nest header** (it has no value; reading it returns `None`), so the expression did nothing. The real rotation input is **Layout Angle Z** (`AngleZ`). Fix: the expression is now `UIB_Label.AngleZ = UIB_Shape.Angle` (one line; unit tests pass). Verified in V2.

## Results

| Check | Comp | Result | Evidence |
|---|---|---|---|
| **V1** colour pickers | `V1_Colours` | **PASS** (one picker per colour; the stock Fusion layout still lists the channel sliders below it; Effects ▸ Macros path NOT VERIFIED) | Exact description below. Screenshots: `images/v1_card_page_top.png`, `images/v1_fill_colour_picker_expanded.png`. |
| **V2** angle | `V2_Angle` | **PASS** (after the fix) | Angle 30 / −45 / 90: the text axis measures 29.4°, −45.6°, 89.4° (the measurement is biased by about −0.6°), counter-clockwise positive like the card, and the text centre is within 2 to 6 px of the card centre (the card estimate includes its shadow). Before the fix the text axis was −0.6° for all three (not rotated). `images/v2_angles_fixed.png`. |
| **V3** Font Style | `V3_FontStyle` | **PASS for setting it by value; the Inspector widget is misleading (see below)** | All eight valid styles change the text; three invalid names make the render fail. |
| **V4** U3 default look/motion | `V4_U3_Defaults` | **PASS** | Identical numbers to Phase 2c: card centre x 925, 965, 971, 961, 960 at frames 4, 6, 8, 12, 24; card and text centres equal at every visible frame (offset 0); out slide: centre 1038 at frame 111, gone by 114. |
| **V4** U5 parity | `V4_U5_Parity` | **PASS** | A UI Block chain and a standalone Shape chain (three looks each) are **identical over the whole frame** (max diff 0), with shadows on every card in both. |
| **V4** U8 instances | `V4_U8_TwoInstances` | **PASS** | Left, Right and a Ctrl+C / Ctrl+V copy: at frame 5 the cards are at x 423.5, 1464, 926.5 (as in Phase 2c); at rest each card has its own text (card/text centres 480/481.5, 1440/1441, 960/961.5); the copy's expressions point to its own Shape (`UIB_Shape_2`). |
| **V4** U9 full restart | all comps | **PASS** | Resolve restarted, project reopened: all 9 timelines and comp names intact, no placeholder tools, no BezierSpline. Re-renders of `V4_U3_Defaults` (frame 24), `V4_U8_TwoInstances` (60) and both chains of `V4_U5_Parity` (60) are **pixel-identical** (max diff 0) to the pre-restart renders. `V2_Angle` after restart still rotates the text 29.4 / −45.6 / 89.4° and keeps it centred (it is not byte-compared, because I rebuilt that comp after taking the earlier image, see V5). |
| **V5** the chain finding | `V5_PasteMinimal` | **CAUSE FOUND: not a Shape or macro bug. Fusion's paste inserts a stray Merge node when the previous node is still selected.** | See below. |

### V1: exactly what each colour control shows (Inspector, Card page)

Every colour is now **one control row with a swatch** (and an eyedropper at its right), instead of four separate rows with their own swatches as in Phase 2c. A small **">" arrow** to the left of each swatch expands a full colour picker (hue strip, saturation/value square and an alpha strip, with Hue/Sat/Value boxes; I opened it for Fill Color to check). Below the swatch, the standard **Red / Green / Blue (/ Alpha) slider rows are still listed**, as in Fusion's stock colour control; they are not hidden.

| Control | Swatch shows | Rows below the swatch |
|---|---|---|
| Text Color | white | Red 1.0, Green 1.0, Blue 1.0 (**no alpha**) |
| Fill Color | dark blue (0.16 / 0.2 / 0.36) | Red, Green, Blue, Alpha 1.0 |
| Fill Color B | light blue (0.4 / 0.6 / 1.0) | Red, Green, Blue, Alpha 1.0 |
| Border Color | white over a checker pattern (alpha 0.35 visible) | Red 1.0, Green 1.0, Blue 1.0, Alpha 0.35 |
| Shadow Color | black over a checker pattern (alpha 0.35 visible) | Red, Green, Blue 0.0, Alpha 0.35 |

So the picker is there for all five; whether you count the always-visible slider rows as "loose channels" is a judgement call, as they are the same as Fusion's own colour controls.

### V3: Font Style

- **Setting it by value works.** Text+ accepts the exact style names of the installed font. For Open Sans these all work and give distinct looks (ink pixel counts, a weight measure: Light 689 < Regular 1321 < Medium 1643 < Semibold 1921 < Bold 2534 < ExtraBold 3176; Italic 1249 and Bold Italic 2388 are slanted). `images/v3_styles.png`.
- **Names the font does not have make the render fail**: `Black`, `Condensed` and an invented name each logged `Could not find font: Open Sans: <style>` and the Deliver job ended "Failed" (the whole comp, not only the text).
- **What the Inspector shows:** the **Font** control is a font-family combo with a second combo showing the style ("Regular"), and the separate **Font Style** row (the macro's published `Style`) shows **"--"** in both of its combos. Its first combo is a **list of font families** (Ahmed, Arial, Bahnschrift, …, `images/v3_font_style_dropdown.png`), not a list of styles. I did not choose anything from it. Note that the Font control's style combo showed "Regular" while the node's value was "Bold" (rendered bold), so the Inspector display does not follow the value.
- Recommendation: do not publish `Style` as its own row (the Font control already carries a style combo); expose a plain "Bold" checkbox or a combo with the valid style names if you need a style choice.

### V5: why Phase 2c's chain looked wrong

Phase 2c U5 compared a block chain with a standalone Shape chain and found the shadows of B and C different (I read it as "B and C lost their shadow"). The cause is neither Merge ordering, overlapping shapes, shadow offset nor premultiplication:

1. **Fusion inserts an extra `Merge` when you paste a node while the previously pasted node is still selected.** The paste joins the new node and the selected one through an auto-created `MergeN`, and re-points the downstream links of the first node to that Merge.
2. Minimal repro in `V5_PasteMinimal`: paste #1 with nothing selected → 1 group, 0 stray Merges. Paste #2 (previous paste still selected) → **`Merge1` appears**. Paste #3 after clearing the selection (`FlowView.Select()`) → **no new Merge**.
3. In the original chain, block A's output (as seen by my Merge) was really the stray `Merge2`/`Merge1` that already contained B and C, so B's and C's shadows were composited **twice**: the single-merge B shadow at 28 % alpha became about 48 % (1 − 0.72²), the darker/longer shadow I saw. The standalone-Shape chain was the correct one. Evidence: in `V5_ShadowChain`, three standalone Shapes in a chain are **identical to each of them merged alone** (max diff 0), while the three pasted blocks in the same layout differ from their single merges (max diff about 23 to 36) and block A *alone* shows B and C in its output (non-background pixels from x 178 to 1783, instead of 178 to 590).
4. Clearing the selection before each paste (done for every comp in this phase) removes the stray nodes: `V4_U5_Parity` now gives a block chain and a Shape chain that are identical, with no extra Merge.

**What this affects (earlier results, not re-run):**
- Phase 2c `U4_TextAlign`, `U5_LookParity`, `U8_TwoInstances` and `U10_Bench12` contain stray Merges (about 2 to 11 each). U4 and U8 still looked right because their cards do not overlap; U5's chain comparison was misleading (the single-merge comparisons in U5 were valid).
- **Phase 2c U10 benchmark was measured on a graph with 11 extra Merges.** I rebuilt it clean (`V4_U10_Bench12`, 75 tools instead of 86) and re-measured cold (the Background colour is changed by 0.001 before each render so no cached frames are reused):

| Blocks | clean (this phase), ms/frame | contaminated graph (Phase 2c) | Shape + Text+ (Phase 2b T7, cold re-measure) |
|---|---|---|---|
| 5 | **65.9** (19 755 ms) | 64.2 | 45.8 |
| 8 | **67.5** (20 248 ms) | 62.5 | 47.5 |
| 12 | **84.2** (25 255 ms) | 60.9 | 62.5 |

  So the clean UI Block graph is **about 1.35 to 1.45× slower than Shape + Text+** at the same counts; the 12-block cost rises (84 ms) instead of staying flat, so the "flat" claim in Phase 2c does not hold. Use these clean numbers.
- **Phase 2 `H13b_v1_Bench20` (v1 UIBlock, 2.5 s/frame) was built by pasting 20 macros with the previous paste selected, so it also contains stray Merges.** The "v1 is about 18× slower" figure is therefore not clean; I did not re-run it.
- Any other comp made by pasting a macro with a selection (`U6`, `U11`) may have stray Merges; their conclusions (shapes, motion, look) did not depend on them.

## Recommendations

| Item | One line |
|---|---|
| Macro | Keep the fix (`AngleZ`). Colour controls are now single pickers; decide if the visible channel sliders are acceptable. |
| V3 | Remove the separate "Font Style" row (it shows "--" and lists families) and expose style a safer way; invalid style names break the whole render. |
| Pasting macros by script | Always clear the selection (`FlowView.Select()`) before each paste, or Fusion adds stray Merge nodes. |
| Benchmarks | Re-baseline anything measured on a pasted graph. The clean UIBlock numbers are 65.9 / 67.5 / 84.2 ms/frame for 5 / 8 / 12 blocks. |

## Needs the user

1. **V1:** add the block from **Effects ▸ Tools ▸ Macros** in the UI and look at the five colour controls on `V1_Colours` (open the Inspector, Card page); tell me whether the visible channel sliders are acceptable.
2. **V3:** try the "Font Style" row in the UI and tell me if it does anything you would want to keep.
3. **Benchmarks:** measure viewer fps on `V4_U10_Bench12` (taps 5 / 8 / 12) and `T7_Cards` in `SMK Phase2b Gate`.
4. Decide if the Phase 2c and Phase 2 benchmarks that used pasted macros (U10, H13b) should be re-run clean.
