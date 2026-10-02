# Phase 2c Gate Results: SMK2 UI Block v2 (generated macro)

Date: 2026-10-02 · Branch: `phase2c-results` · Built from `main` at `30cb0bc`, plus the two macro fixes below (`build/make_macros.py`).

Anything not observed is marked **NOT VERIFIED** with the reason.

## Environment and method

- Same machine as earlier phases: Resolve **Studio** 21.1.0.14, Windows 11 (build 26100), RTX 4070 SUPER, CUDA.
- Steps run: `git pull`, `python build/make_macros.py`, `python scripts/install.py` (macro to `Fusion/Macros/SMK2/`), Resolve restart.
- Unit tests: `test_smk_core` 49/0, `test_fuse_harness` 12/0, `test_animator` 10/0, `test_motion_rig` 9/0, `test_shape` 34/0, `test_macros` 11/0 (also after my fixes). `test_shape_kernel` is still SKIPPED (no C compiler).
- Same method as earlier phases: scripting API plus Deliver-page PNG renders analysed with PIL, plus cropped screenshots of the Inspector and Nodes panes for U2 and U7.
- **How the macro was loaded:** I loaded `SMK2_UIBlock.setting` with `comp:Paste(bmd.readfile(<path>))` (through `comp.Execute`). I did **not** try Effects ▸ Tools ▸ Macros in the UI (no UI control), so that path is NOT VERIFIED.
- All timings are Deliver render times (PNG, 300 frames), not viewer fps. Viewer fps is NOT VERIFIED everywhere.

## Project and comps (open these by hand)

Project **`SMK Phase2c Gate`**. Same layout rules as Phase 2: Note on top, sources left, then SMK nodes, Merges, MediaOut on the right, every tool renamed, positions set with `FlowView.SetPos`, saved with `ProjectManager.SaveProject()`. Your `SMK Test` project was not touched.

| Check | Comp to open |
|---|---|
| U1 and U2 | `U1_Load` (select `U1_UIBlock` and look at the Inspector pages) |
| U3 | `U3_Defaults` |
| U4 | `U4_TextAlign` |
| U5 | `U5_LookParity` |
| U6 and U7 | `U6_Motion` (one block; double-click `U6_Block` to expand the group) |
| U8 | `U8_TwoInstances` |
| U9 | all comps (reopened after a full restart) |
| U10 | `U10_Bench12` (60 fps; taps `Card05_Merge`, `Card08_Merge`, `Card12_Merge`) |
| U11 | `U11_vs_v1` |

## Two macro bugs found and fixed (`build/make_macros.py`)

The first render of the freshly generated macro showed a tiny card, so I debugged it. Both bugs are in the macro description, not in Resolve:

1. **The inner Shape had the wrong image size.** A Shape pasted from the macro came up with `UseFrameFormatSettings = 0`, `Width 320`, `Height 240` (the Fuse's own defaults only apply when created by `AddTool`), so the card was drawn in a 320×240 buffer (about 430 px wide instead of 576). **Fix:** the Shape node now sets `UseFrameFormatSettings=1, Width=1920, Height=1080` (the same as the Label already did).
2. **Expressions that point to an inner node named `Shape` do not evaluate.** The Label's `Point(Shape.CX, Shape.CY)` and the Animator's `PivotX = Shape.CX` stayed at their defaults (the first-pasted block's label stayed at the frame centre while its card moved). After renaming the node to `Shape_0` the expression evaluated at once. **Fix:** all four inner nodes are now `UIB_Shape`, `UIB_Label`, `UIB_Merge`, `UIB_Animator` (published control keys such as `Shape_W` and `Animator_InEngine` are unchanged). Fusion rewrites the names on later pastes and copy-pastes (`UIB_Shape_1`, …) and re-points the expressions correctly (checked in U4 and U8).

`python build/make_macros.py` regenerates the file; the unit tests pass.

## Results

| Check | Comp | Result | Evidence |
|---|---|---|---|
| **U1** load | `U1_Load` | **PASS** (loaded by script paste; the Effects ▸ Macros menu path NOT VERIFIED) | No error dialog and no "Unknown tool". The group `SMK2_UIBlock` loaded with 4 inner nodes of the right types (`Fuse.SMK2_Shape`, `TextPlus`, `Merge`, `Fuse.SMK2_Animator`), 82 published inputs, one `MainOutput1`, the Label and Animator expressions present, wiring Shape → Merge ← Label → Animator as designed. No new Fuse or macro errors in the Resolve log. |
| **U2** Inspector pages | `U1_Load` | **PARTIAL: pages OK, colour controls are NOT swatches** | Inspector tabs: **Card, Motion, In Motion, Out Motion** (plus Settings), labels readable (`images/u2_inspector_card_page.png`). The colour controls (Text colour, Fill A, Fill B, Border, Shadow) show as **one mini-swatch plus one slider per channel**: "Fill Red", "Fill Green", "Fill Blue", "Fill Alpha" each with its own swatch and a slider, so **four loose Red/Green/Blue/Alpha controls per colour** and not a single colour picker. Each channel's swatch shows only that channel, so for example "Text Red" is a red box. Also: the "Font Style" combo shows "--" instead of "Bold" (the value is still applied: Bold renders). |
| **U3** defaults | `U3_Defaults` | **PASS** (after both fixes) | Hold pose: a dark rounded card 572 px wide (576 expected) with white bold "Card" centred (text centre x 960, card centre 960), soft shadow, hairline border (`images/u3_defaults_f24.png`). Slide-in from the left with spring: card centre x 925, 965, 971, 961, 960 at frames 4, 6, 8, 12, 24. Out: card slides right (centre 1038 at frame 111) and is gone by frame 114. The text-to-card centre offset is 0 px at every visible frame, so the text moves with the card. |
| **U4** text and layout | `U4_TextAlign` | **PASS** | Four blocks: Center 0.3/0.7 with Width 0.22 / Height 0.1; Angle 30; text "Hello world" at size 0.06 in red; Center 0.75/0.3 with Width 0.3 / Height 0.2. In every one the label is centred on its card (`images/u4_text_align.png`). Text, size and colour work. Font and style: Style "Regular" gives a narrower text (346 px vs 374 px wide) and Font "Arial" a different shape. **Note:** the label does not rotate with the card's Angle (the 30° card has horizontal text). |
| **U5** look vs Shape | `U5_LookParity` | **PASS** | Three configurations (linear 45° + Outside border 8 px + radius 0.3; radial + Center border 6 px; solid + Inside border 4 px + shadow X 20 / Y 30 / blur 40). Block (text emptied) vs a standalone Shape with the same values, each merged alone over the Background: **max diff 0** in all three. (A combined chain of the three standalone Shapes rendered B and C without their shadow; I did not find out why. The single-merge comparison is the reliable one.) |
| **U6** motion controls | `U6_Motion` | **PASS** | Six In engines on the Motion pages give six distinct paths and all settle at 960 (Ease monotone; Spring overshoots to 971; Bounce dips to 914; Elastic swings to 1017 then 943; Overshoot peaks at 979; Inertia slow). Index 0..5 with Stagger 0.1 (set by script, live): first visible frames 4, 6, 9, 11, 13, 16 (about 2.4 frames = 0.1 s at 24 fps). In Rotation 90 + Scale 0.5 at frame 0 gives a 61×94 px card (rest 192×115, rotated and halved is about 58×96). The Fade, Slide and Out controls were not re-tested one by one beyond that; they are the same Animator inputs checked in Phase 1. |
| **U7** group collapsed / expanded | `U6_Motion` | **PASS** | Collapsed it is a single stacked-node tile; double-clicking opens it in place (`images/u7_group_expanded.png`): `UIB_Shape` top left, `UIB_Merge`, then `UIB_Animator` running left to right, `UIB_Label` below left feeding the Merge, all distinct and readable. Node positions inside the group: Shape (−1.5, −0.2), Label (−1.5, 1.8), Merge (−0.5, 0.8), Animator (0.5, 0.8). |
| **U8** two or more instances | `U8_TwoInstances` | **PASS** | `U8_Left_Block` (text "Left", slide from the left, Ease), `U8_Right_Block` (text "Right", slide from the right, Bounce, a second paste) and `U8_Copy_Block` (a Ctrl+C / Ctrl+V copy of the first, renamed, text "Copy", Inertia). At rest each label is at its own card; at frame 5 the three cards are at x 423, 1464 and 926 (different directions and engines). The copy's Label expression is `Point(UIB_Shape_2.CX, UIB_Shape_2.CY)` (its own Shape), so there is no cross-talk (`images/u8_two_instances.png`). |
| **U9** save / close / reopen (**full app restart**) | all comps | **PASS** | Project saved, Resolve quit and restarted, project reopened: all 8 timelines and comp names intact, tool counts unchanged, no `Dummy`/unknown tools, **no BezierSpline anywhere**. Re-renders of U3 (frame 24), U4 (frame 60) and U8 (frame 60) are **pixel-identical** to the pre-restart renders (max diff 0). |
| **U10** benchmark | `U10_Bench12` | **Render 64.2 / 62.5 / 60.9 ms/frame** for 5 / 8 / 12 blocks. Viewer fps NOT VERIFIED. | Table below. |
| **U11** vs v1 | `U11_vs_v1` | **Notes only** | See below. |

### U10: benchmark (60 fps, 1080p, 300 frames to PNG, each block has text; Index staggered, Stagger 0.05)

Cold means the Background colour was changed by 0.001 before the render so that nothing from the previous render's frame cache is reused (see the caching note below).

| Cards | UIBlock v2 (this phase), ms/frame | Shape + Text+ (Phase 2b T7, **re-measured cold now**) | T7 as reported in Phase 2b |
|---|---|---|---|
| 5 | **64.2** (19 246 ms) | 45.8 (13 753 ms) | 42.5 |
| 8 | **62.5** (18 752 ms) | 47.5 (14 251 ms) | 52.5 |
| 12 | **60.9** (18 260 ms) | 62.5 (18 737 ms) | 55.8 |

- The UIBlock v2 time is **flat (about 61 to 64 ms/frame) from 5 to 12 blocks**; Shape + Text+ grows from 46 to 62 ms. At 5 and 8 cards the macro is about 1.3 to 1.4× slower than separate Shape + Text+ nodes; at 12 cards they are equal. Neither reaches 24 fps (41.7 ms) or 60 fps (16.6 ms) in render time at these counts.
- The very first 5-block render took 47 246 ms (157.5 ms/frame); I take that as one-off warm-up (font and Fuse start-up) because the identical graph re-rendered cold took 64.2.
- **Caching note (affects every benchmark in this project's history):** rendering the same graph twice in one Resolve session reuses cached frames. Re-rendering the 5-block graph unchanged took 3 748 ms (12.5 ms/frame), and a larger tap reuses the cached merges of the smaller one. My earlier Phase 2b T7 numbers were taken as ascending taps (3, 5, 8, 12) without changing the graph, so part of those later numbers may have used cached frames. The cold re-measurements in the table above are the ones to use; they are within about 10 ms of what I reported before, so the conclusions do not change. Earlier phases mostly rendered different graphs each time, but I have not re-checked them.
- Viewer first-pass and cached fps: NOT VERIFIED (no viewer access).

### U11: side by side with v1 `SMK_UIBlock` (`images/u11_v1_left_v2_right.png`)

| | v1 (left) | v2 (right) |
|---|---|---|
| Size | same width 576 px; v1 `Height` is a fraction of frame height (needed 0.267 for 288 px), v2 `H` a fraction of frame width | 576 × 288 |
| Corners | small radius only (the useful range is narrow; 0.2 made the whole shape wrong in Phase 2) | up to a pill (0 to 0.5) |
| Border | opaque white 6 px band: my border alpha 0.35 had no visible effect | 2 px, translucent (alpha 0.35) |
| Shadow | none, no control for it | soft shadow (X, Y, blur, colour) |
| Text | none | label text with font, style, size, colour, centred and moving with the card |
| Fill | solid colour | solid, linear, radial gradients (and alpha) |
| Motion | frame-based In/Out, with slide, fade and scale | seconds-based In/Out, with six engines, slide, fade, scale and rotation, Index/Stagger |
| Node count | one group of 28 nodes | one group of 4 nodes (2 Fuses) |

What v1 has that v2's block does not publish: Anchor and Growth Origin controls, per-effect enable switches (slide, fade, scale) and link-out-to-in switches, Quick Animation / UI Motion Style / Animation Pair / Preset menus, and Motion Response / Damping / Oscillation fine-tuning. v2 exposes the engine and spring/elastic parameters instead.

## Recommendations

| Item | One line |
|---|---|
| Macro | Go. It loads and works after the two fixes; every published control and the shared wiring behave. |
| U2 | Decide whether to accept per-channel colour controls, or to publish the colours differently (a single colour control needs a different publishing approach). Also fix the "--" shown in the Font Style combo. |
| U4 | If the label should rotate with the card, add a Rotation to the Label or drive it from the Angle control. |
| U10 | Render time is flat at about 61 to 64 ms/frame for 5 to 12 blocks, so the per-block overhead is small once a few exist. No 24 or 60 fps in render. Check real viewer fps before drawing conclusions. |

## Needs the user

1. **U1:** add the block from **Effects ▸ Tools ▸ Macros** in the UI (I only loaded it by script paste) and confirm nothing red appears.
2. **U2:** open `U1_Load`, select `U1_UIBlock`, and judge the colour controls (per-channel sliders) and the Font Style "--" display.
3. **U10:** measure viewer first-pass and cached fps on `U10_Bench12` at taps 5 / 8 / 12, and compare with `T7_Cards` in `SMK Phase2b Gate`.
4. **U11:** scrub `U11_vs_v1` and compare the motion feel by eye.
5. **U4:** decide whether the label should rotate with the card's Angle.
6. **Kernel parity test:** still needs a machine with a C compiler.
