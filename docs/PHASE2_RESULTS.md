# Phase 2 Gate Results: SMK2 Shape

Date: 2026-10-02 · Branch: `phase2-results` · Built from `main` at `0317990`. **No source changes were needed in this phase.**

Anything not observed is marked **NOT VERIFIED** with the reason.

## Environment and method

- Same machine as earlier phases: Resolve **Studio** 21.1.0.14, Windows 11 (build 26100), RTX 4070 SUPER, CUDA.
- Steps run: `git pull`, `python scripts/install.py` (Fuses in `Fuses/SMK2/`), Resolve restart.
- Unit tests: `test_smk_core` 49/0, `test_fuse_harness` 11/0, `test_animator` 10/0, `test_motion_rig` 9/0, `test_shape` 34/0. **`test_shape_kernel`: SKIPPED (no C compiler on this machine)**, so the "kernel matches the Lua oracle" claim was not re-checked here. The Resolve renders below are the first GPU evidence for the kernel.
- Same method as Phase 1: scripting API plus Deliver-page PNG renders analysed with PIL. For H12 I also looked at a screenshot of the Inspector (cropped to the Inspector only).
- Resolve's Python API has no way to read the Fusion Console or viewer fps. **Viewer playback fps (H13) is NOT VERIFIED.**

## Test project and comps (open these by hand)

All checks are in one Resolve project, **`SMK Phase2 Gate`**: one timeline per check, each with one Fusion comp of the **same name**. Your `SMK Test` project was not touched.

Layout in every comp: a Note on top says what the check is and what to look for; sources/generators on the left (x = 0), SMK nodes next, Merges (x = 6 to 12), then MediaOut at the right. Multi-card comps have one row per card with 2-unit row spacing; the shared Background and the merge chain sit to the right. Every tool is renamed (for example `H5_Border_Inside_w12`, `Card07_Shape`). Node positions were set explicitly with `FlowView.SetPos`. The internal nodes of the v1 macro group are positioned by the v1 macro itself (in H14 and H13b).

| Check | Timeline / comp name |
|---|---|
| H1 | `H1_Defaults` |
| H2 | `H2_Shapes` |
| H3 | `H3_Resolutions` |
| H4 | `H4_Fills` |
| H5 | `H5_Borders` |
| H6 | `H6_Shadows` |
| H7 | `H7_RingTrim` |
| H8 | `H8_RotateScale` |
| H9 | `H9_Stagger20` |
| H10 | `H10_MultiInstance` |
| H11 | (all of the above, reopened after a full app restart) |
| H12 | `H12_ColourPickers` |
| H13 | `H13_Bench20` (60 fps timeline) and `H13b_v1_Bench20` (the v1 UIBlock version, 60 fps) |
| H14 | `H14_vs_v1_UIBlock` |

Notes on your layout rules:
- `comp:Save()` is **not available in Resolve**: calling it opens an error dialog ("The composition could not be saved: No such file or directory"). I saved with `ProjectManager.SaveProject()` after building each comp instead.
- Note nodes were created with `AddTool("Note")`, with the text in the node's `Comments`.
- H13 and H13b are 60 fps timelines inside the 24 fps project (the timeline's own frame rate was set per timeline). All other comps are 24 fps, 1080p.
- H14's comp contains the v1 macro `SMK_UIBlock`. A macro cannot be added with `AddTool`, so I pasted it with `comp.Execute('comp:Paste(bmd.readfile(...))')`.

## Results

| Gate | Result | Evidence |
|---|---|---|
| **H1** defaults | **PASS** | Frame 60 (hold): the shape is a 576×288 px white rounded rectangle (0.3 × 0.15 of frame width), centred. It is **not a pill**: the default Corner Radius is 0.15 (a pill needs 0.5). A soft shadow shows below it: over a dark background the pixel 10 px under the bottom edge is (20,24,41) vs the background (26,31,51), and over white it is 204 vs 255; both fade back to the background by about 30 px. The corner pixel equals the background exactly, so the surrounding area is transparent. Spring slide-in from the left with fade: frames 0 and 3 invisible, frame 6 centre x 965, frame 12 centre 961.5, frame 60 centre 960. Frame 114 (out phase) invisible. No Shape errors in the Resolve log. |
| **H2** all shapes | **PASS** (800% zoom NOT VERIFIED) | Rectangle with radius 0 / 0.15 / 0.5 (a true pill), Ellipse, Ring, Line, in `images/h2_shapes.png`. Edges have a single-pixel anti-aliased transition at 100%: for example an ellipse top goes 31 → 76 → 255, a pill right edge 255 → 72 → 27, and a ring outer edge 31 → 210 → 255. The ellipse region has 194 distinct intermediate levels. Zooming the viewer to 800% was not possible (no viewer access). |
| **H3** resolutions | **PASS** | One card with an 8 px red Inside border. At 1920×1080, 1080×1920 and 3840×2160 the card is 0.3000 × 0.1500 of the frame **width** in all three. The border is 8 px at 1920, 16 px at 3840, and 4 px (plus one anti-aliased pixel, i.e. 4.5) at 1080 wide, which matches 8 × width / 1920. |
| **H4** fills | **PASS** | Fill A = red, B = blue. Linear 0°: A on the left, B on the right. Linear 90°: A at the bottom, B at the top. Linear 45°: A bottom-left to B top-right. Radial: A in the centre, B at the edge (`images/h4_fills.png`). Translucent solid (alpha 0.5) over light grey: interior (242,114,114), and the edge pixel is (235,184,184), between the background and the fill. The darkest green value anywhere in the box including the edges is 114, equal to the interior, so there is **no dark fringe**. |
| **H5** borders | **PASS** | Border 0 / 4 / 12 px at Inside / Center / Outside on a 345.6 px wide card with the left edge at x = 556.8 (4 px) and 998.4 (12 px). Inside 4 px: border from 557 to 560, fill from 561. Center 4 px: border 555 to 558, fill from 559 (straddles the edge). Outside 4 px: border 553 to 556, fill from 557. The 12 px versions are at 999–1010, 993–1004 and 987–998. Only a single anti-aliased pixel sits between border and fill (for example (51,0,204)), so there is no gap and no double edge. Border colour alpha 0.5 over the fill gives (128,0,128), and over the background (115,115,242), as expected. |
| **H6** shadows | **PASS** | Seven cards drawn at frame 0 (`images/h6_shadows.png`). Default shadow falls off smoothly from 116 to 217 (background) over about 30 px below the card. A hard shadow (blur 0, Y 20) is a constant 108 for 20 px. Shadow colour alpha 0: **0 of 74 332 pixels** around the card differ from the background. The shadow offset follows rotation (the card at 30° has its shadow toward its own lower right) and scales with the card (the 0.5 scale card has a proportionally smaller shadow). |
| **H7** ring trim | **PASS** | Ring Trim 0.25 covers **0–87° clockwise from 12 o'clock**. Trim 0.25 + Trim Start 0.25 covers 90–180° (starts at 3 o'clock). Trim keyframed 0 → 1 (BezierSpline) covers 0–87° at frame 6, 0–180° at frame 12 and a full ring at frame 60. Trim driven by an `SMK2 Motion` modifier: 0–42° at frame 1, 0–129° at frame 2, 0–222° at frame 3, full by frame 6, also clockwise. Line Trim 0.5: the left half is drawn (visible up to x = 1823, the centre), so the line draws left to right. |
| **H8** angle / rotation / scale | **PASS** | Red → blue horizontal gradient. Angle 30°: the blue end is above and right of the red end (blue centroid (370,373), red (166,490)), so positive is **counter-clockwise**. In Rotation 90 at frame 0: blue above red (blue y = 314, red y = 549), counter-clockwise. In Scale 0.5: 192×95 px instead of 384×191, with the **centre unchanged** (1190.0, 431.5 vs expected 1190.4, 432.0). All three combined: the centre is unchanged (1651.0, 431.5), and at frame 60 the card returns to Angle 30 only. |
| **H9** stagger | **PASS** | 20 cards, Index 0..19. Stagger 0.05: first visible frames 2, 3, 4, 6, 7 … 25 at 24 fps (1.2 frames per card = 0.05 s). Changing every card's Stagger to 0.1 (by script, no reload) gives 2, 4, 7, 9 … 48 (2.4 frames per card). |
| **H10** multi-instance | **PASS** | `Left_Card` (red rectangle, slide from the left, Ease) and `Right_Pill` (blue pill, slide from the right, Bounce), both renamed. At rest they sit at 240–718 and 1200–1678 (centres 479 and 1439, as set). At frame 5 the left card is at 128–606 (shifted left) and the right at 1248–1726 (shifted right, a different amount because of the Bounce engine). Independent. |
| **H11** save/close/reopen (**full app restart**) | **PASS** | Project saved, Resolve quit and restarted, project reopened. All 14 timelines and comp names are intact. Tool counts per comp are unchanged. Re-renders of five comps (H1 frame 60, H4 frame 60, H5 frame 60, H6 frame 0, H8 frame 0) are **pixel-identical** to the renders before the restart (max difference 0). The only BezierSpline in the project is the keyframe I added deliberately in `H7_RingTrim` row 3; no SMK2 input in any other comp has one. |
| **H12** colour pickers | **PARTIAL** | The four colour controls (Fill Color, Fill Color B, Border Color, Shadow Color) each show **one colour swatch with an eyedropper**, and then the **four loose Red / Green / Blue / Alpha slider rows are also shown below each swatch** (`images/h12_inspector_crop.png`). So the swatch is there, but the sliders are not hidden. All 16 inputs report `ColorControl` with the right group and index. Whether the small arrow beside each swatch collapses the sliders: NOT VERIFIED (I did not click the Inspector). The whole Inspector is one long flat page of about 60 controls with no collapsible groups, so the layout is "usable but long", which is a judgement for you. |
| **H13** benchmark | **Render: 140.8 ms/frame.** Viewer first-playback and cached fps: **NOT VERIFIED** (no viewer access). | 20 cards, each a Text+ plus an SMK2 Shape (rounded rect, 3 px border, shadow, motion with Index 0..19 and Stagger 0.05), merged over a 1080p Background, **60 fps timeline, 300 frames to PNG: 42 246 ms = 140.8 ms/frame (7.1 fps).** Pictured at frame 150 in `images/h13_bench_look_f150.png`. See the comparison table below. |
| **H14** v1 vs v2 look | **Notes only (see below)** | Both cards in `images/h14_v1_left_v2_right.png`. |

### H13 comparison

Same 60 fps / 1080p / 300 frames / PNG method as G10 and R6, 20 cards:

| Variant | ms/frame | fps equivalent |
|---|---|---|
| Baseline, static Text+ and Merges (Phase 1) | 7.5 | 133 |
| 20 native Transforms (Phase 1) | 27.5 to 35.8 | 28 to 36 |
| 20 Animators (Phase 1 / 1b) | 67 to 72.5 | 14 to 15 |
| 20 Rigs (Phase 1b) | 77 to 84 | about 12 |
| **20 Shape cards + 20 Text+ (this phase, H13)** | **140.8** | **7.1** |
| 20 Shape cards, Merges only, **no Text+** (same comp, text merges bypassed) | **50.8** (15 252 ms) | 19.7 |
| **20 v1 `SMK_UIBlock` + 20 Text+ (H13b, 10 frames measured)** | **about 2 526** (25 258 ms for 10 frames) | **0.4** |

- The Shape is **not faster than the Animator on a per-card basis in a chain**: the Shape alone with merges costs about 50.8 ms/frame (2.5 ms per card), but adding the 20 Text+ merges (40 merges in total, all downstream of animated content so none can be cached) brings it to 140.8 ms.
- It is about **18 times faster than the v1 UIBlock** (2.5 s/frame for 20 UIBlocks: each UIBlock is a group of 28 nodes, so the graph has 662 nodes).
- The v1 number is from a 10-frame render (60 to 69); I cancelled the full 300-frame render after about 2 % because it was estimated at about 12 minutes.
- The 60 fps target (16.6 ms) is not met by any of the variants that animate 20 cards with Fuses.

### H14: v1 `SMK_UIBlock` vs v2 `SMK2 Shape`

- **Scripting the v1 block:** I had to read its defaults to get a fair look. The v1 `Height` is a fraction of the frame **height** (0.15 gives 162 px) while v2 `H` is a fraction of the frame **width** (0.15 gives 288 px). The v1 `Corner Radius` has a small useful range (0.04 default; 0.2 broke the shape into a huge white ellipse/rectangle), whereas v2 uses 0 to 0.5 with 0.5 = pill.
- **What the Shape cannot match yet (from the v1 controls):** v1 has a separate Anchor and Growth Origin control and a Position that is a normal Fusion Point; v1 groups its animation into Quick Animation / UI Motion Style / Animation Pair / Preset menus and exposes a Motion Response and Damping/Oscillations fine-tuning; v1 In/Out have separate enable switches for slide, fade and scale (and Link-Out-to-In switches), while the Shape has one set of numbers per phase and no per-effect enable.
- **What the Shape has that v1 does not:** shadow, gradients (linear, radial), ring, line and trim, border position (Inside/Center/Outside), alpha colours, and rotation as an In/Out effect.
- **Edges:** both are anti-aliased. The v1 straight edge goes 51 → 230 → 255 (two soft pixels), the Shape goes 51 → 51 → 255 (one pixel, sharper); the Shape has more intermediate levels on a corner (49 vs 19 distinct levels).
- **Not compared:** motion feel side by side (NOT VERIFIED by eye).

## Recommendations

| Gate | One line |
|---|---|
| H1–H11 | Go. The Shape is correct in Resolve on CUDA. Everything in the gate that can be measured passed, including pixel-identical results after a full restart. |
| H1 | If you want a pill by default, change the default Corner Radius from 0.15 to 0.5. |
| H12 | Decide if you want the R/G/B/A sliders hidden. Today each colour shows the swatch plus four sliders. |
| H13 | Not 60 fps in render (140.8 ms/frame). The cost is mostly the 40 Merges that can no longer be cached, plus about 2.5 ms per Fuse card. A single-Fuse "card with text" would remove the Text+ merges (the shapes-only chain is 50.8 ms). Check real viewer playback before deciding. |
| H14 | v2 is about 18× faster than v1 for 20 cards. Decide whether the listed v1 convenience controls (anchor, per-effect enables, presets) should be added. |

## Needs the user

1. **H13 viewer fps:** open `H13_Bench20` and measure first-playback and cached playback fps in the viewer, and the same for `H13b_v1_Bench20` (it will be very slow, about 0.4 fps by render time).
2. **H2:** zoom the viewer to 800% on `H2_Shapes` (frame 60) and look at the edges.
3. **H12:** open `H12_ColourPickers`, select `H12_Shape` and judge the colour controls and the long flat Inspector layout; try the arrow beside each swatch.
4. **H14:** scrub `H14_vs_v1_UIBlock` and compare the motion of the two cards by eye.
5. **H7:** scrub `H7_RingTrim` frames 0 to 24 and check the sweep looks right to you (verified by pixels only).
6. **Kernel parity test:** run `python tests/test_shape_kernel.py` on a machine with a C compiler (it was skipped here).
7. The extra Resolve test timelines `H13b_v1_Bench20` and `H14_vs_v1_UIBlock` contain the v1 macro, which is heavy (662 nodes). Open them last.
