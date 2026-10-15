# Phase 11 Results: Card Stack, Stat Card, Click Demo, style presets, outline cost

Resolve Studio 21.1.0.14, Windows. Project `SMK Phase11` (your `SMK Test` was not touched). Scripting only, no UI automation. The macros were pasted fresh from `Macros/SMK2/*.setting` into every comp. One comp per check (named after it), each with a Note and explicit node positions (Note y −3; Background x 0; macro group x 4; Merge x 12; MediaOut x 16; one row per instance), `FlowView.Select()` before every paste, comp rate = timeline rate, Background +0.001 before every timed render, `SaveProject()`. Comps are 24 fps, 120 frames, 1080p unless the name says otherwise. Measurements are PNG renders analysed with PIL; text numbers are read from the text expression with `GetInput("StyledText", frame)`. Setup: `git pull`, `python scripts/install.py`, Resolve restarted, `python build/build.py`, every `tests/test_*.py` run once: all pass (**kernel-parity tests SKIPPED: no C compiler on this machine**).

## Bugs found and fixed in this phase (all in `build/make_macros.py`; every one made a render fail or a product unusable)

1. **CardStack: render failed** ("The Fusion composition … could not be processed"). The Style expression of the text of cards 2–4 read `UIL_L2.Font.Value`, but `Font` of those texts is a link to card 1; the expression evaluated to **None**. Now every card reads `UIL_L1.Font.Value`. (Found by scanning every expression for None values.)
2. **StatCard: render failed.** The number expression concatenated `UIS_Ctrl.Prefix` and `UIS_Ctrl.Suffix`, which are **Text objects** (cdata) in Fusion expressions, so the whole expression evaluated to None. Now `.Value`. The unit test was updated to feed text controls as objects with `.Value` (before, it passed with plain strings, which is why it never showed).
3. **StatCard: Target Value was clamped at 1,000,000** (script and typed values; 1,234,567 showed as 1,000,000). The slider range 0…1,000,000 stays the visible range; `INP_MinAllowed` / `INP_MaxAllowed` ±1e12 added for Value.
4. **StatCard presets did not restyle the number or caption.** `Soft` showed a white number and a light-blue caption on a near-white card (unreadable). The style now also sets `UIS_Num` and `UIS_Label` text colours (Soft: dark text).

Tests after the changes: `test_products.py` 36 pass, `test_macros.py` 352 pass, everything else unchanged.

## A. SMK2_CardStack

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| P1 | Paste fresh; defaults | `P1_defaults` | **PASS after fix 1** | Tools: 20 inside the group (Background hub, 4 × Shape / Text+ / Merge / Animator, 3 merges), only `Fuse.SMK2_Shape`, `Fuse.SMK2_Animator`, `TextPlus`, `Merge`, `Background` IDs. 1,064 + 83 expressions evaluated in the 22-macro scan: 0 return None (a red node cannot be read by script: this is the nearest proxy). Four cards "Card 1…4" evenly spaced; **first ink frames 2, 4, 7, 11** (stagger 0.12 s ≈ 2.9 frames), last ink frames 114 / 112 / 112 / 112; frame 0 and frame 119 empty. |
| P2 | Geometry, gap, centre, first Y; resolutions | `P2_geometry`, `P2_1080x1920`, `P2_4K` | **PASS** | Pitch of the card tops (px): Gap 0 → 134 (cards touch, one 538 px run), 0.015 → 163, 0.05 → 230 = (0.07 + gap) × 1920 exactly. Changed card (W 0.25, H 0.06, radius 0.4, X 0.3, Y 0.8, border 6 yellow, shadow alpha 0.8, Gap 0.03): all four follow, pitch 173 = (0.06 + 0.03) × 1920. 1080p and 4K: card top 0.1224 and pitch 0.0849–0.0852 of the frame width at both; 1080×1920: same card height 0.0704 and pitch (the first Y is a fraction of the height: top 0.463 of the width). |
| P3 | Texts, font, weights, size, colour | `P3_text` | **PASS** | Texts Alpha / Bravo / Charlie / Delta render independently (different widths 82…102 px). Weight 0…7 (Light … Bold Italic) all render (ink px of card 1: 392, 577, 696, 824, 1055, 1347, 592, 1025), Font Arial renders, Text Size and Text Color apply to all four ((255, 230, 26)). |
| P4 | Stagger, engines, Out, trimmed 46 frames | `P4_*`, `P4_trim46` | **PASS** | Stagger 0 → first ink 2, 2, 2, 2; 0.12 → 2, 4, 7, 11; 0.3 → 2, 9, 17, 23 (≈ 7 frames = 0.29 s). **Enable Out on: the last frame is empty for all four cards** in every case (default, stagger 0, 0.3, Spring-in / Elastic-out where all four end at frame 108). Trimmed 46-frame range (comp render range 0–45 set with `SetAttrs`, **not a real trimmed clip**): last ink 40 / 38 / 38 / 38, frame 45 empty. Engines apply to all four. |
| P5 | Cost, 1 and 3 stacks, node count | `P5_Stack1`, `P5_Stack3`, `P5_UIBlock4` | **One stack ≈ four UIBlocks** | 60 fps, 300 frames, cold, 1080p PNG (first / second run) ms/frame: 1 stack **87.3 / 27.5**; 3 stacks **265.6 (partial run) / 75.2**; 4 separate `SMK2_UIBlock` **33.7 / 33.5**. Node count: stack 20 tools, 4 UIBlocks 4 × 5 = 20 tools. Viewer fps NOT VERIFIED. |
| P6 | Save, restart, two instances | `P6_TwoInstances` | **PASS** | Two CardStacks (width 0.3 / 0.2, X 0.3 / 0.75, gap 0.015 / 0.04, red fill, texts) independent; after a full quit and relaunch all 83 published inputs of both identical, comp rate 24, frames 40 and 70 re-rendered **pixel-identical** (max difference 0); tool IDs only Shape, Animator, TextPlus, Merge, Background, Group, MediaOut, Note (**no BezierSpline**). |

## B. SMK2_StatCard

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| T1 | Defaults | `T1_defaults` | **PASS after fix 2** | "12,480": '0' until frame 7 (0.3 s), 9,519 at frame 20, 12,066 at frame 30, **'12,480' from frame 40 on** (exact; 12,480 at frame 119 too). Caption "Total users". Card: ink 0 at frame 0, full from frame 2, leaves on frames 112–118 (0 on 118 and 119). |
| T2 | Value, decimals, thousands, prefix, suffix | `T2_values` | **PASS after fix 3** | Strings at the last frame: 0 → `0`; 7 → `7`; 999 → `999`; 1000 → `1,000`; 1234567 → `1,234,567` (before fix 3: `1,000,000`); 1000000 → `1,000,000`; 12480 Decimals 1 → `12,480.0`, 2 → `12,480.00`; Thousands off → `12480`; Prefix `$` → `$12,480`; Suffix `%` → `12,480%`, `K` → `12,480K`; 1234.5 Decimals 2 `$` ` USD` → `$1,234.50 USD`; 12345.678 Decimals 2 → `$12,345.68K`. |
| T3 | Count engines | `T1_defaults` | **PASS** | Max value reached / over target, min, settle frame for Ease / Spring / Bounce / Elastic / Overshoot / Inertia: 12,480 (0 %) / **12,614 (+1.07 %)** / 12,480 / **17,065 (+36.7 %)** / **13,726 (+9.98 %)** / 12,480; min 0.0 in every case (**no negative value**); all end on `12,480` and never change after settling (frames 36–41). |
| T4 | Timing, fps, Out, trimmed | `T4_Fps24/30/60`, `T4_Trim46` | **PASS** | At t = 0.2 / 0.3 / 0.5 / 1.0 / 1.5 / 1.7 / 2.0 s the string is `0, 0, 4,621, 10,920, 12,444, 12,480, 12,480` at **24, 30 and 60 fps** (identical). The number never changes after the count ends. The card's In / Out is the Animator (published); the number has no separate Out control published. Trimmed 46 frames: `12,480` on frame 41 and 45. |
| T5 | Fonts, weights, sizes, long value | `T2_values` | **PASS; the long value overflows the card** | Number weights 0 / 4 / 5 / 7 and fonts Arial, Times New Roman, Impact, number size 0.09 + colour + a long caption all render (no failure). `1,234,567,890` renders as `1,234,567,890` centred, **546 px wide on a 499 px card: overflows the card by about 22 px each side, not clipped by the frame** (`t2_long.png`). |
| T6 | Cost | `T6_One`, `T6_Five` | **≈ 6 ms warm per card** | 60 fps cold 1080p (first / second run): 1 stat card **25.3 / 16.1**; 5 stat cards **90.0 / 42.4**. Viewer fps NOT VERIFIED. |
| T7 | Save, restart, two instances | `T7_TwoInstances` | **PASS** | Two StatCards (12,480 Ease at X 0.3; 99.5 with Decimals 1, suffix %, Spring at X 0.7) independent; after restart all 94 published inputs of both identical, frames 30 and 70 **pixel-identical**, no BezierSpline. |

## C. SMK2_ClickDemo

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| D1 | Defaults | `D1_defaults` | **PASS** | Full 120-frame render completes. Button visible from frame 4; the cursor fades in from frame ~11 at Cursor Start (0.25, 0.7), moves to the button, clicks (ripple), holds and fades out by frame ~112. `v1_variants.png` bottom row shows button + cursor + ripple. |
| D2 | Button position / width, arrival | `D1_defaults` (4 settings) | **PASS** | Cursor tip (topmost outline pixel) relative to the button centre at frame 60: (0, +1) px for 4 settings (X, Y, Width = 0.6 / 0.4 / 0.16, 0.4 / 0.65 / 0.16, 0.7 / 0.3 / 0.25, 0.5 / 0.5 / 0.1). The click ripple ring is centred (1151.5, 647.5) against the tip (1152, 649): within 1.5 px. |
| D3 | Point expression on the Cursor waypoint; macro crosshair | `D1_defaults` | **YES, it works** | Waypoint 2 `P2` of the Cursor has the expression `Point(UID_Card.CX, UID_Card.CY)`; it evaluates (0.6, 0.4) = the card centre and follows when the card moves (D2). The published `Cursor Start (drag in viewer)` is an OffsetControl whose input `Cursor_P1` reads / writes (0.25, 0.7) from the group; **whether the crosshair is drawn in the viewer is NOT VERIFIED** (no UI). |
| D4 | Timing, move style, arc | `D1_defaults` | **PASS** | Defaults (start delay 0.5 s, reach 1.1 s): fade-in at frame 11, within 4 px of the button at frame **46** (Smooth ease-out tail; at frame 40 still 68 px away). Move Style: Snappy is near the button at frame 28 (1094, 536); **Spring overshoots** (1204, 586 at frame 28) and settles; Arc 0 is a straight path (within 4 px at frame 44); Reach 0.6 s + start 0.2 s: within 4 px at frame 27. Click Delay default 0.12 s. |
| D5 | Cursor honours the frame size inside the macro | `D5_1080x1920`, `D5_4K` | **YES** | Cursor image 1080×1920 / 3840×2160 with data window the full frame (`UseFrameFormatSettings` 1, Width / Height = the comp format); render sizes correct; tip offset from the button centre (0, +1) px at both (0.0 and 0.00026 of the frame width). |
| D6 | Cost, restart | `D6_Bench`, `D6_TwoInstances` | **PASS**; cost **27.5 / 16.4** ms/frame (60 fps cold 1080p, first / second run) | Two ClickDemos (buttons at different places, texts Click 0 / 1): after a full quit and relaunch all 93 published inputs of both identical, frames 40 and 70 **pixel-identical**, no BezierSpline (tool IDs include `Fuse.SMK2_Cursor`). |

## D. Style presets

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| V1 | Paste every variant | `V1_variants`, `V1_others` | **PASS: 22 macros, all paste and render; no expression returns None** | `Macros/SMK2`: Callout, CardStack (+Glass, Neon, Soft), ClickDemo (+3), ProgressBar, ProgressRing, StatCard (+3), TextLetter, TextLine, TextWord, UIBlock (+3) = 22 files. All 16 product macros pasted in one comp (frame 60 render completes) and the 6 older ones in another (completes); 1,064 + 83 expressions evaluated at frame 60, none None. **A red node cannot be read by script: NOT VERIFIED beyond that.** Variants are visibly distinct (`v1_variants.png`: base dark blue, Glass translucent with a light border, Neon near-black with a cyan border and glow, Soft near-white). |
| V2 | Look of the presets, readability | `V1_variants` | **PASS after fix 4** | Glass: fill 12 % white (0.12 alpha), border 45 % white, text white: contrast 5.8:1 over the test background. Neon: fill (0.04, 0.05, 0.10), border cyan (0.1, 0.9, 1.0), shadow cyan alpha 0.55, text (0.75, 1, 1): 17.5:1. Soft: fill (0.97, 0.97, 0.99), text (0.12, 0.14, 0.20): 14.6:1. Before fix 4 the StatCard Soft number was white on near-white. |
| V3 | Node and control counts equal the base | `V1_variants` | **PASS** | Inner tools: UIBlock 5 / 5 / 5 / 5, CardStack 20 × 4, StatCard 7 × 4, ClickDemo 7 × 4; published controls 82 / 83 / 94 / 93 for base, Glass, Neon, Soft of each. |

## E. Open from Phase 10

| # | Check | Comp | Result | Evidence |
|---|---|---|---|---|
| O2 | Look outline 20 px cost, serration | `O2_1080p_*`, `O2_4K_*`, `O2_serration` | **Faster; serration still gone** | Text+ title, 60 fps cold PNG (first / second run): **1080p no effect 5.2 / 4.8, outline 20 px 10.0 / 8.9** (Phase 10: 10.9 / 10.7); **4K no effect 18.4 / 18.3, outline 20 px 45.7 / 45.8** (Phase 10: 70.5 / 70.8, −35 %). At 20 and 40 px the outer edge along an H stem is perfectly straight (x standard deviation 0.00 px). The 4K outline is still +27 ms over the baseline. |

## Restart / reopen (P6, T7, D6)

All three two-instance comps were saved, Resolve was quit and relaunched, the project reopened: published inputs identical (83 / 94 / 93 per instance), frames pixel-identical. A fresh paste of `SMK2_StatCard_Soft` after fix 4 shows dark text (31, 36, 51) on the (247, 247, 252) card (`v2_statcard_soft.png`).

## Not verified
- Whether a macro shows a red node (not readable from scripting): judged by completed renders and by evaluating every expression.
- The macro-level cursor crosshair in the viewer; the Inspector layout of the long control lists; viewer fps; whether the products look good.
- A real trimmed timeline clip (P4, T4): the comp render range was used.
- Kernel parity (no C compiler).

## For you to check by hand
1. Whether the card stack, stat card and click demo (and their Glass / Neon / Soft presets) look good.
2. The Inspector layout of the long control lists (82–94 controls per macro).
3. Dragging the Click Demo cursor crosshair in the viewer.
4. Viewer fps.

## Evidence
`docs/phase11_evidence/`: `h11.py`, `p1an.py`, `p11_notes.md` (raw numbers), `v1_variants.png`, `t2_long.png`, `d2_f60_crop.png`, `o2_serration.png`, `o2_zoom_*.png`, `p2_changed.png`.
